import os

# Specify the LLM model to use. You can choose any LLM supported by LiteLLM.
# Example options include "gpt-4o", "claude", "deepseek-chat", etc.
# For a full list of supported models, refer to:
# https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json
LLM_MODEL = "gemini/gemini-2.0-flash"

# API token for authentication with the LLM provider.
# This is fetched from the environment variable "GEMINI_API_KEY".
API_TOKEN = os.getenv("GEMINI_API_KEY")

# Browser mode: True = headless (no browser window), False = headful (visible browser)
HEADLESS_MODE = True

# CSS selector to target the main HTML element containing the business information.
# This is specific to JustDial and helps focus the scraper on relevant content.
# We target `.resultbox` which contains the business listings.
CSS_SELECTOR = "div.resultbox"

# Maximum number of pages to crawl. Adjust this value based on how much data you want to scrape.
MAX_PAGES = 3  # Example: Set to 5 to scrape 5 pages.

# Instructions for the LLM on what information to extract from the scraped content.
SCRAPER_INSTRUCTIONS = (
    "Extract all business information from JustDial listings: "
    "'name' (company/business name), 'rating_score' (numerical rating like 4.5), "
    "'address' (full location/address), 'years_in_business' (experience years if shown, e.g., '15 Years in Healthcare'), "
    "'categories' (business categories/services), and 'phone_number' from the content."
)