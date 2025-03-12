import requests
from bs4 import BeautifulSoup

base_url = 'https://chancellor.ucla.edu/messages/page/'
keywords = ['muslim', 'islam', 'arab', 'palestine', 'palestinian', 'gaza', 'west bank']
matched_statements = []

for page in range(1, 6):  # testing first 5 pages; adjust range as needed
    print(f"Scraping page {page}...")
    response = requests.get(f"{base_url}{page}")
    soup = BeautifulSoup(response.text, 'html.parser')

    links = soup.find_all('a', href=True)
    # Filter out any link that is:
    # - A pagination link (contains '/messages/page/')
    # - The main landing page (exact match)
    statements = [a['href'] for a in links
                  if '/messages/' in a['href']
                  and '/messages/page/' not in a['href']
                  and a['href'] != 'https://chancellor.ucla.edu/messages/']

    for url in statements:
        print(f"Checking {url} ...")
        res_statement = requests.get(url)
        statement_soup = BeautifulSoup(res_statement.text, 'html.parser')
        content = statement_soup.get_text().lower()  # case-insensitive matching
        if any(kw in content for kw in keywords):
            matched_statements.append(url)

with open('matched_muslim_statements.txt', 'w') as f:
    for url in matched_statements:
        f.write(url + "\n")

print("Matching URLs saved to matched_muslim_statements.txt")
