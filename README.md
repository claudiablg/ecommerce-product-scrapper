# E-Commerce Product Scraper

A Python scraper that extracts product data from e-commerce sites and exports clean, structured CSV files.

## What It Does

- Scrapes product listings across multiple pages automatically
- Extracts: **product name, price, rating, availability, category, UPC, stock count, and description**
- Handles pagination, rate limiting, and error handling
- Exports to clean CSV ready for analysis or import

## Sample Output

| id | name | price_gbp | rating | in_stock | category |
|----|------|-----------|--------|----------|----------|
| 1 | A Light in the Attic | 51.77 | 3 | True | Poetry |
| 2 | Tipping the Velvet | 53.74 | 1 | True | Historical Fiction |
| 3 | Soumission | 50.10 | 1 | True | Fiction |

## Quick Start

```bash
# Install dependencies
pip3 install requests beautifulsoup4 pandas

# Scrape all products
python3 scraper.py

# Scrape first 5 pages only
python3 scraper.py --pages 5

# Include detailed product info (description, UPC, stock count)
python3 scraper.py --pages 5 --details

# Custom output file
python3 scraper.py --output my_data.csv
```

## Tech Stack

- **Python 3** — core language
- **BeautifulSoup4** — HTML parsing
- **Requests** — HTTP client with headers and rate limiting
- **Pandas** — data cleaning and CSV export

## Features

- Automatic pagination detection and traversal
- Polite scraping with configurable delays between requests
- Detailed logging with progress indicators
- Summary statistics after each run
- Clean CSV output with proper indexing
- Optional deep scraping for product details (UPC, description, stock levels)

## Adapting to Other Sites

This scraper is built with a modular structure. To adapt it for a different e-commerce site:

1. Update the CSS selectors in `scrape_page()` to match the target site's HTML
2. Adjust the pagination logic in `get_total_pages()`
3. Modify the data fields in the product dictionary

I regularly adapt this approach for client projects involving product monitoring, competitor price tracking, and lead generation.

## Author

[Your Name] — [your Upwork profile link]