import requests
from bs4 import BeautifulSoup
from scraper.scraper import scrape_h1_tags
from utils.parser import parse_h1_tags
import json
import logging
from urllib.parse import urlparse
import os
import csv


DATA_FILE = os.getenv("DATA_FILE", "src/data/urls.json")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),  # Log to a file
        logging.StreamHandler()              # Log to the console
    ]
)

# List of domains that are known to have SSL issues
ALLOW_INSECURE_DOMAINS = [
    "www.smccme.edu"
]

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def load_urls(file_path):
    """
    Load URLs from a JSON file.
    :param file_path: Path to the JSON file containing URLs.
    :return: List of URLs.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            urls = data.get("urls", [])
            return [url for url in urls if is_valid_url(url)]
    except Exception as e:
        logging.error(f"Error loading URLs: {e}")
        return []

def process_in_batches(urls, batch_size=10):
    for i in range(0, len(urls), batch_size):
        yield urls[i:i + batch_size]

def save_to_csv(data, file_path="output.csv"):
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "H1 Tags"])
        for url, h1_tags in data.items():
            writer.writerow([url, ", ".join(h1_tags)])

def main():
    """
    Main function to orchestrate the web scraping process.
    """
    # Load URLs from the JSON file
    try:
        urls = load_urls("src/data/urls.json")  # Update the path to your JSON file
        if not urls:
            logging.info("No URLs to scrape.")
            return

        logging.info("Starting the web scraping project...")
        for batch in process_in_batches(urls, batch_size=10):
            results = {}
            for url in batch:
                logging.info(f"Scraping URL: {url}")
                h1_tags = scrape_h1_tags(url)
                results[url] = h1_tags
                parsed_data = parse_h1_tags(h1_tags)
                logging.info(parsed_data)
            save_to_csv(results)
    except Exception as e:
        logging.critical(f"Critical error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
