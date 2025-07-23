import requests
from bs4 import BeautifulSoup
import json
import logging
from urllib.parse import urlparse
import os
import csv
import xml.etree.ElementTree as ET
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import time

DATA_FILE = os.getenv("DATA_FILE", "src/data/urls.json")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

SAVE_DIR = "html_outputs"
os.makedirs(SAVE_DIR, exist_ok=True)

OUTPUT_DIR = "html_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

ALLOW_INSECURE_DOMAINS = [
    "batestech.smartcatalogiq.com",
    "csprd.ctclink.us",
    "umaine.edu",
    "usm.maine.edu",
    "web.newriver.edu",
    "www.cmcc.edu",
    "www.glenville.edu",
    "www.smccme.edu",
    "www.yccc.edu",
]

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def load_urls(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            urls = data.get("urls", [])
            return [url for url in urls if is_valid_url(url)]
    except Exception as e:
        logging.error(f"Error loading URLs: {e}")
        return []

def sanitize_filename(url):
    """Convert URL to a safe filename"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', urlparse(url).netloc + urlparse(url).path)[:100]



def fetch_and_classify_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        verify_ssl = not any(domain in url for domain in ALLOW_INSECURE_DOMAINS)
        response = requests.get(url, headers=headers, timeout=10, verify=verify_ssl)
        content_type = response.headers.get("Content-Type", "").lower()

        # Handle APIs
        if "application/json" in content_type:
            return "API_JSON"
        elif "xml" in content_type:
            try:
                ET.fromstring(response.text)
                return "API_XML"
            except ET.ParseError:
                return "API_XML_INVALID"

        # Handle HTML (check if static or JS-rendered)
        elif "text/html" in content_type:
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            visible_text = soup.get_text(strip=True)

            if len(visible_text) > 500:
                _save_html(url, html)
                return "HTML_STATIC"
            else:
                rendered_html = render_with_chrome(url)
                if rendered_html:
                    _save_html(url, rendered_html)
                    return "HTML_JS_RENDERED"
                return "HTML_JS_RENDER_FAILED"

        return f"OTHER ({content_type})"

    except Exception as e:
        logging.warning(f"Failed to process {url}: {e}")
        return "ERROR"
    
def _save_html(url, html):
    domain_path = urlparse(url).netloc.replace(".", "_")
    page_path = urlparse(url).path.strip("/").replace("/", "_") or "index"
    file_name = f"{domain_path}__{page_path}.html"
    path = os.path.join(OUTPUT_DIR, file_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

def render_with_chrome(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.get(url)
        try:
            # Wait for course section or fallback to body
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
            )
            # Scroll down to ensure lazy content loads
            scroll_to_bottom(driver)
            time.sleep(3)  # additional buffer time
        except Exception as wait_err:
            logging.warning(f"Wait condition failed for {url}: {wait_err}")

        html = driver.page_source
        return html
    except Exception as e:
        logging.warning(f"Render failed for {url}: {e}")
        return None
    finally:
        try:
            driver.quit()
        except:
            pass

def scroll_to_bottom(driver, step=1000, pause=1):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, arguments[0]);", step)
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def process_in_batches(urls, batch_size=10):
    for i in range(0, len(urls), batch_size):
        yield urls[i:i + batch_size]

def save_to_csv(results, file_path="output.csv"):
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "Type"])
        for url, type_str in results.items():
            writer.writerow([url, type_str])

def main():
    try:
        urls = load_urls(DATA_FILE)
        if not urls:
            logging.info("No URLs to process.")
            return

        logging.info("Starting classification...")
        for batch in process_in_batches(urls, batch_size=10):
            results = {}
            for url in batch:
                logging.info(f"Processing: {url}")
                result_type = fetch_and_classify_url(url)
                logging.info(f"→ {result_type}")
                results[url] = result_type
            save_to_csv(results)
    except Exception as e:
        logging.critical(f"Critical error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
