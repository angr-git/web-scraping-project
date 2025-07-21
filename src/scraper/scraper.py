import requests
from bs4 import BeautifulSoup
import urllib3

# Suppress SSL certificate warnings (only safe for dev)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Custom headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.1 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com"
}

ALLOW_INSECURE_DOMAINS = [
    "www.smccme.edu"
]

class Scraper:
    def __init__(self, url):
        self.url = url

    def fetch_page(self):
        """
        Fetch the HTML content of the page.
        :return: HTML content as a string.
        """
        response = requests.get(self.url, headers=HEADERS, verify=False, timeout=10)
        response.raise_for_status()
        return response.text

    def parse_page(self, html):
        """
        Parse the HTML content using BeautifulSoup.
        :param html: HTML content as a string.
        :return: BeautifulSoup object.
        """
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def scrape(self):
        """
        Scrape the <h1> tags from the given URL.
        :return: A list of <h1> tag text content.
        """
        try:
            # Fetch the page content
            html = self.fetch_page()
            
            # Parse the page content
            soup = self.parse_page(html)
            
            # Extract <h1> tags
            h1_tags = soup.find_all('h1')
            return [h1.get_text(strip=True) for h1 in h1_tags]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {self.url}: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []

def scrape_h1_tags(url):
    try:
        domain = requests.utils.urlparse(url).netloc
        verify_ssl = domain not in ALLOW_INSECURE_DOMAINS

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://google.com"
        }

        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        h1_tags = soup.find_all('h1')
        return [h1.get_text(strip=True) for h1 in h1_tags]

    except requests.exceptions.SSLError as ssl_err:
        print(f"[SSL ERROR] {url}: {ssl_err}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []