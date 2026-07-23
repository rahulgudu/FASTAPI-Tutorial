import httpx
from bs4 import BeautifulSoup

# Step 1: Define the target URL
url = "https://example.com"

# Step 2: Fetch the raw HTML content from the web
# Headers make our script look like a standard web browser instead of a bot
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = httpx.get(url, headers=headers)

# Step 3: Check if the website responded successfully (Status Code 200 OK)
if response.status_code == 200:
    raw_html = response.text
    
    # Step 4: Parse the raw HTML string using BeautifulSoup
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # Step 5: Extract specific elements
    page_title = soup.title.string          # Gets text inside <title>tag</title>
    heading = soup.find("h1").get_text()    # Gets text inside the first <h1> tag
    first_paragraph = soup.find("p").get_text() # Gets text inside the first <p> tag
    
    # Print the extracted data
    print("--- Extracted Web Data ---")
    print(f"Title: {page_title}")
    print(f"Main Heading: {heading}")
    print(f"First Paragraph: {first_paragraph}")

else:
    print(f"Failed to fetch page. Status code: {response.status_code}")