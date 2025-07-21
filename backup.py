import requests
from bs4 import BeautifulSoup



# List of URLs to scrape
URLS = [
    "https://www.cmcc.edu/academics/programs/course-listing//?course-select=1",
    "https://usm.maine.edu/registration-scheduling-services/course-search/?doClassSearch=1&keywords=&strm=2610&career=UGRD&subject=&courseNumber=&meetingsStartTimeStart=&meetingsStartTimeEnd=&meetingsEndTimeStart=&meetingsEndTimeEnd=&location=&startDate=&endDate=",
    "https://umaine.edu/clasadvisingcenter/2025/06/12/fall-2025-course-descriptions/",
    "https://www.smccme.edu/academics/courses/current-credit-course-offerings/",
    "https://www.yccc.edu/explore/applying-to-yccc/course-schedules/fall-2025-16-week-semester/",
    "https://web.newriver.edu/courses/202601/",
    "https://csprd.ctclink.us/psp/csprd/EMPLOYEE/PSFT_CS/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_Main?",
    "https://www.glenville.edu/academics/course-schedule",
    "https://batestech.smartcatalogiq.com/current/course-catalog/"
]

# List of domains that are known to have SSL issues
ALLOW_INSECURE_DOMAINS = [
    "www.smccme.edu"
]

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


def main():
    print("Starting the web scraping project...")
    for url in URLS:
        print(f"\nScraping URL: {url}")
        h1_tags = scrape_h1_tags(url)
        if h1_tags:
            print("H1 Tags Found:")
            for tag in h1_tags:
                print(f" - {tag}")
        else:
            print("No H1 tags found.")

if __name__ == "__main__":
    main()
