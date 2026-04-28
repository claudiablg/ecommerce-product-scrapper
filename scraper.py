"""
E-Commerce Product Scraper
==========================
Scrapes product data from an e-commerce site and exports to CSV.
Extracts: product name, price, rating, availability, category, and product URL.

Usage:
    python scraper.py                  # Scrape all pages
    python scraper.py --pages 5        # Scrape first 5 pages
    python scraper.py --output data.csv  # Custom output filename

Author: Claudia Bélanger
"""

import warnings
warnings.filterwarnings("ignore")
import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import time
import sys

BASE_URL = "https://books.toscrape.com"

# Map word ratings to numbers
RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}


def get_soup(url: str) -> BeautifulSoup:
    """Fetch a URL and return a BeautifulSoup object."""
    headers = {"User-Agent": "Mozilla/5.0 (ProductScraper Demo)"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_total_pages(soup: BeautifulSoup) -> int:
    """Extract total number of pages from pagination."""
    pager = soup.select_one("li.current")
    if pager:
        # Text is like "Page 1 of 50"
        return int(pager.text.strip().split()[-1])
    return 1


def scrape_product_detail(url: str) -> dict:
    """Scrape additional details from a product's individual page."""
    soup = get_soup(url)
    
    details = {}
    
    # Get product description
    desc_tag = soup.select_one("#product_description ~ p")
    details["description"] = desc_tag.text.strip() if desc_tag else "N/A"
    
    # Get table data (UPC, product type, tax, etc.)
    table = soup.select_one("table.table-striped")
    if table:
        for row in table.select("tr"):
            header = row.select_one("th").text.strip()
            value = row.select_one("td").text.strip()
            if header == "UPC":
                details["upc"] = value
            elif header == "Number of reviews":
                details["num_reviews"] = int(value)
            elif header == "Availability":
                # Extract number from "In stock (22 available)"
                if "In stock" in value:
                    try:
                        details["stock_count"] = int(
                            value.split("(")[1].split(" ")[0]
                        )
                    except (IndexError, ValueError):
                        details["stock_count"] = 0
                else:
                    details["stock_count"] = 0
    
    # Get breadcrumb for category
    breadcrumbs = soup.select("ul.breadcrumb li")
    if len(breadcrumbs) >= 3:
        details["category"] = breadcrumbs[2].text.strip()
    else:
        details["category"] = "N/A"
    
    return details


def scrape_page(page_url: str) -> list[dict]:
    """Scrape all products from a single listing page."""
    soup = get_soup(page_url)
    products = []
    
    for article in soup.select("article.product_pod"):
        # Product name & URL
        title_tag = article.select_one("h3 a")
        name = title_tag["title"]
        relative_url = title_tag["href"]
        
        # Build absolute URL for product detail page
        if relative_url.startswith("catalogue/"):
            product_url = f"{BASE_URL}/{relative_url}"
        elif relative_url.startswith("../"):
            product_url = f"{BASE_URL}/catalogue/{relative_url.replace('../', '')}"
        else:
            product_url = f"{BASE_URL}/catalogue/{relative_url}"
        
        # Price
        price_text = article.select_one("p.price_color").text.strip()
        price = float(price_text.replace("£", "").replace("Â", ""))
        
        # Star rating
        star_tag = article.select_one("p.star-rating")
        rating_class = star_tag["class"][1] if star_tag else "Zero"
        rating = RATING_MAP.get(rating_class, 0)
        
        # Availability
        avail_tag = article.select_one("p.instock.availability")
        in_stock = bool(avail_tag and "In stock" in avail_tag.text)
        
        products.append({
            "name": name,
            "price_gbp": price,
            "rating": rating,
            "in_stock": in_stock,
            "product_url": product_url,
        })
    
    return products


def main():
    parser = argparse.ArgumentParser(description="E-Commerce Product Scraper")
    parser.add_argument("--pages", type=int, default=None, help="Number of pages to scrape (default: all)")
    parser.add_argument("--output", type=str, default="products.csv", help="Output CSV filename")
    parser.add_argument("--details", action="store_true", help="Scrape individual product pages for extra details (slower)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  E-Commerce Product Scraper")
    print("=" * 60)
    
    # Get total pages
    print("\n[*] Fetching site catalog...")
    first_page = get_soup(BASE_URL)
    total_pages = get_total_pages(first_page)
    pages_to_scrape = min(args.pages, total_pages) if args.pages else total_pages
    print(f"[*] Found {total_pages} pages total — scraping {pages_to_scrape}")
    
    # Scrape listing pages
    all_products = []
    for page_num in range(1, pages_to_scrape + 1):
        if page_num == 1:
            url = f"{BASE_URL}/catalogue/page-1.html"
        else:
            url = f"{BASE_URL}/catalogue/page-{page_num}.html"
        
        products = scrape_page(url)
        all_products.extend(products)
        
        progress = f"[*] Page {page_num}/{pages_to_scrape} — {len(products)} products"
        print(progress, end="")
        
        # Be polite — small delay between requests
        if page_num < pages_to_scrape:
            print(" (waiting 0.3s...)", end="")
            time.sleep(0.3)
        print()
    
    # Optionally scrape individual product pages for extra details
    if args.details:
        print(f"\n[*] Fetching details for {len(all_products)} products...")
        for i, product in enumerate(all_products):
            details = scrape_product_detail(product["product_url"])
            product.update(details)
            
            if (i + 1) % 10 == 0 or (i + 1) == len(all_products):
                print(f"    {i + 1}/{len(all_products)} done")
            time.sleep(0.2)  # Be polite
    
    # Export to CSV
    df = pd.DataFrame(all_products)
    df.index += 1  # Start index at 1
    df.index.name = "id"
    df.to_csv(args.output)
    
    # Print summary
    print(f"\n{'=' * 60}")
    print(f"  RESULTS SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Total products scraped : {len(df)}")
    print(f"  Price range            : £{df['price_gbp'].min():.2f} — £{df['price_gbp'].max():.2f}")
    print(f"  Average price          : £{df['price_gbp'].mean():.2f}")
    print(f"  Average rating         : {df['rating'].mean():.1f} / 5")
    print(f"  In stock               : {df['in_stock'].sum()} / {len(df)}")
    print(f"  Output file            : {args.output}")
    print(f"{'=' * 60}")
    
    # Show sample
    print(f"\n  Sample data (first 5 rows):\n")
    sample = df.head().astype(str)
    widths = {col: max(sample[col].str.len().max(), len(str(col))) for col in sample.columns}
    formatters = {col: (lambda x, w=widths[col]: f"{x:<{w}}") for col in sample.columns}
    print(sample.to_string(formatters=formatters, justify="left"))
    print()


if __name__ == "__main__":
    main()