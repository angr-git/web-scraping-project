from bs4 import BeautifulSoup
import pandas as pd

# Load your HTML file
with open("Academic Course Listings - CMCC.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Locate the table by ID
table = soup.find("table", id="course-results")
if not table:
    raise Exception("Table with ID 'course-results' not found.")

# Extract headers
headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]

# Extract each row
rows = []
for tr in table.find("tbody").find_all("tr"):
    cells = tr.find_all("td")
    row = [td.get_text(separator=" ", strip=True) for td in cells]
    if row:
        rows.append(row)

# Create DataFrame
df = pd.DataFrame(rows, columns=headers)

# Save to CSV
df.to_csv("cmcc_course_listings.csv", index=False)
print("Data saved to cmcc_course_listings.csv")
