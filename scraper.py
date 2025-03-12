import requests
from bs4 import BeautifulSoup

base_url = 'https://chancellor.ucla.edu/messages/page/'
keywords = ['jewish', 'israel', 'muslim', 'islam']
matched_statements = []

for page in range(1, 6):  # testing the first 5 pages
    print(f"Scraping page {page}...")
    response = requests.get(f"{base_url}{page}")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = soup.find_all('a', href=True)
    statements = [a['href'] for a in links if '/messages/' in a['href']]
    
    for url in statements:
        print(f"Checking {url} ...")
        res_statement = requests.get(url)
        statement_soup = BeautifulSoup(res_statement.text, 'html.parser')
        content = statement_soup.get_text().lower()
        
        if any(kw in content for kw in keywords):
            matched_statements.append(url)

# Write matching URLs to a file
with open('matched_statements.txt', 'w') as f:
    for url in matched_statements:
        f.write(url + "\n")

print("Matching URLs have been saved to matched_statements.txt")
