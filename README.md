# AI Web Scraper

An AI-powered web scraper that extracts business data using Crawl4AI and LLM.

## How It Works

1. Enter a **city** and **business category** when prompted
2. The scraper visits JustDial and extracts business listings
3. An LLM processes the page content to extract structured data
4. Results are saved to a CSV file

## Setup

1. Clone the repo
   ```bash
   git clone https://github.com/Nandha-06/AI-web-scraper.git
   cd AI-web-scraper
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Add your API key in `.env`
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Run

```bash
python main.py
```

Then enter the city and category when prompted. The data will be saved to a CSV file.

## Output

The scraper extracts:
- Business name
- Phone number
- Address
- Rating
- Number of reviews
