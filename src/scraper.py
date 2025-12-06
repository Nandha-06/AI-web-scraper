import json
import asyncio
from pydantic import BaseModel
from typing import List, Set, Tuple
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy,
)
from src.utils import is_duplicated
from config import LLM_MODEL, API_TOKEN, HEADLESS_MODE


def get_browser_config() -> BrowserConfig:
    """
    Returns the browser configuration for the crawler.
    """
    return BrowserConfig(
        browser_type="chromium",
        headless=HEADLESS_MODE,  # Configurable in config.py
        verbose=True,
    )


def get_llm_strategy(llm_instructions: str, output_format: BaseModel) -> LLMExtractionStrategy:
    """
    Returns the configuration for the language model extraction strategy.
    """
    # Using older crawl4ai API (0.4.x) - provider and api_token passed directly
    return LLMExtractionStrategy(
        provider=LLM_MODEL,
        api_token=API_TOKEN,
        schema=output_format.model_json_schema(),
        extraction_type="schema",
        instruction=llm_instructions,
        input_format="markdown",
        verbose=True,
    )


def build_justdial_url(city: str, category: str, page_number: int = 1) -> str:
    """
    Build JustDial search URL for the given city and category.
    
    JustDial will automatically redirect to the proper URL with nct-id.
    URL Pattern:
    - Page 1: https://www.justdial.com/{City}/{Category}
    - Page 2+: https://www.justdial.com/{City}/{Category}/page-{N}
    
    Args:
        city: The city name (e.g., "Mumbai", "Delhi")
        category: The business category (e.g., "Dentists", "Restaurants")
        page_number: The page number (default: 1)
    
    Returns:
        The JustDial search URL
    """
    # Format city and category for URL
    city_formatted = city.strip().title().replace(" ", "-")
    category_formatted = category.strip().title().replace(" ", "-")
    
    base_url = f"https://www.justdial.com/{city_formatted}/{category_formatted}"
    
    if page_number > 1:
        return f"{base_url}/page-{page_number}"
    return base_url


async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    page_number: int,
    city: str,
    category: str,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    seen_names: Set[str],
) -> Tuple[List[dict], bool]:
    """
    Fetches and processes a single page from JustDial.
    
    Args:
        crawler: The web crawler instance.
        page_number: The page number to fetch.
        city: The city name.
        category: The business category.
        css_selector: The CSS selector to target the content.
        llm_strategy: The LLM extraction strategy.
        session_id: The session identifier.
        seen_names: Set of business names that have already been seen.
    
    Returns:
        Tuple containing list of businesses and a flag indicating if no results found.
    """
    # Build URL directly - JustDial will redirect to proper URL with nct-id
    url = build_justdial_url(city, category, page_number)
    print(f"Loading page {page_number}: {url}")

    # Fetch page content with the extraction strategy
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=llm_strategy,
            css_selector=css_selector,
            session_id=session_id,
            wait_until="domcontentloaded",
            page_timeout=60000,
        ),
    )

    if not result.success:
        print(f"Error fetching page {page_number}: {result.error_message}")
        return [], False
    
    # Check for no results indicators
    if result.cleaned_html:
        no_result_indicators = ["No Results Found", "Sorry, no results found", "0 results found"]
        for indicator in no_result_indicators:
            if indicator.lower() in result.cleaned_html.lower():
                print(f"No results found on page {page_number}.")
                return [], True
    
    if not result.extracted_content:
        print(f"No extracted content from page {page_number}")
        if result.markdown:
            print(f"Markdown content available ({len(result.markdown)} chars)")
            # Print a preview for debugging
            print(f"Preview: {result.markdown[:500]}...")
        return [], True if page_number == 1 else False

    # Parse extracted content
    try:
        extracted_data = json.loads(result.extracted_content)
    except json.JSONDecodeError as e:
        print(f"Error parsing extracted content: {e}")
        return [], False
        
    if not extracted_data:
        print(f"No businesses found on page {page_number}.")
        return [], True

    print(f"Extracted {len(extracted_data)} raw records from page {page_number}")

    # Process businesses
    all_businesses = []
    for business in extracted_data:
        # Skip error entries
        if business.get("error") is False:
            business.pop("error", None)

        # Skip if no name
        if not business.get("name"):
            continue

        if is_duplicated(business["name"], seen_names):
            print(f"Duplicate '{business['name']}' found. Skipping.")
            continue

        seen_names.add(business["name"])
        all_businesses.append(business)

    if not all_businesses:
        print(f"No unique businesses found on page {page_number}.")
        return [], False

    print(f"Extracted {len(all_businesses)} unique businesses from page {page_number}.")
    return all_businesses, False
