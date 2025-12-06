import asyncio
from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv
from config import CSS_SELECTOR, MAX_PAGES, SCRAPER_INSTRUCTIONS
from src.utils import save_data_to_csv
from src.scraper import (
    get_browser_config,
    get_llm_strategy,
    fetch_and_process_page,
    build_justdial_url,
)
from models.business import BusinessData

load_dotenv()


def get_user_input():
    """
    Get search parameters from user.
    
    Returns:
        Tuple[str, str]: City and category entered by the user.
    """
    print("\n" + "=" * 50)
    print("       JustDial Business Scraper")
    print("=" * 50 + "\n")
    
    city = input("Enter city (e.g., Mumbai, Delhi, Bangalore): ").strip()
    if not city:
        city = "Mumbai"
        print(f"Using default city: {city}")
    
    category = input("Enter business category (e.g., Dentists, Restaurants): ").strip()
    if not category:
        category = "Dentists"
        print(f"Using default category: {category}")
    
    print(f"\nSearching for '{category}' in '{city}'...")
    print(f"URL: {build_justdial_url(city, category)}\n")
    return city, category


async def crawl_justdial():
    """
    Main function to crawl businesses data from JustDial.
    """
    # Get user input for city and category
    city, category = get_user_input()
    
    # Initialize configurations
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy(
        llm_instructions=SCRAPER_INSTRUCTIONS,
        output_format=BusinessData
    )
    session_id = "justdial_crawler_session"

    # Initialize state variables
    page_number = 1
    all_records = []
    seen_names = set()

    # Start the web crawler context
    async with AsyncWebCrawler(config=browser_config) as crawler:
        while True:
            # Fetch and process data from the current page
            records, no_results_found = await fetch_and_process_page(
                crawler,
                page_number,
                city,
                category,
                CSS_SELECTOR,
                llm_strategy,
                session_id,
                seen_names,
            )

            if no_results_found:
                print("No more records found. Ending crawl.")
                break

            if not records:
                print(f"No records extracted from page {page_number}.")
                if page_number == 1:
                    print("Stopping as first page had no records.")
                    break
                break

            # Add the records from this page to the total list
            all_records.extend(records)
            page_number += 1
            
            if page_number > MAX_PAGES:
                print(f"Reached maximum pages limit ({MAX_PAGES}).")
                break

            # Pause between requests
            print("Waiting before next page...")
            await asyncio.sleep(4)

    # Save the collected records to a CSV file
    if all_records:
        # Sanitize filename
        safe_city = city.replace(" ", "_").lower()
        safe_category = category.replace(" ", "_").lower()
        filename = f"justdial_{safe_city}_{safe_category}_data.csv"
        
        save_data_to_csv(
            records=all_records, 
            data_struct=BusinessData,
            filename=filename
        )
        print(f"\n✓ Successfully scraped {len(all_records)} businesses!")
    else:
        print("\nNo records were found during the crawl.")

    # Display usage statistics for the LLM strategy
    llm_strategy.show_usage()


async def main():
    """
    Entry point of the script.
    """
    await crawl_justdial()


if __name__ == "__main__":
    asyncio.run(main())
