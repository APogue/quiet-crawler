import os
from selenium import webdriver
from bs4 import BeautifulSoup
import time, re, random
from datetime import datetime

# Configuration
url = 'https://dailybruin.com/category/news'
keywords = ['failure', 'website']
start_date = datetime(2024, 12, 6)
end_date = datetime(2024, 12, 7)

# Set up Selenium (disable images and mask automation)
options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)
driver.get(url)

# Start from top
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(random.uniform(1, 2))

# Efficient scrolling
SCROLL_PAUSE = 2
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(1, 2))

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    dates = sorted([
        datetime(*map(int, m.groups())) for m in (
            re.search(r'/([0-9]{4})/([0-9]{2})/([0-9]{2})/', a['href'])
            for a in soup.find_all('a', href=True)
        ) if m
    ], reverse=True)

    if dates and dates[-1] < start_date:
        break

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Sort and extract URLs (newest first)
story_links = sorted(
    set(
        a['href'] for a in soup.find_all('a', href=True)
        if re.search(r'/\d{4}/\d{2}/\d{2}/', a['href'])
    ),
    reverse=True
)

matched_urls = []

for link in story_links:
    match = re.search(r'/([0-9]{4})/([0-9]{2})/([0-9]{2})/', link)
    if match:
        url_date = datetime(*map(int, match.groups()))
        if start_date <= url_date <= end_date:
            print(f"Checking {link}...")
            driver.get(link)
            time.sleep(random.uniform(1, 2))
            article_soup = BeautifulSoup(driver.page_source, 'html.parser')
            text = article_soup.get_text().lower()

            if any(kw in text for kw in keywords):
                matched_urls.append(link)

driver.quit()

# Navigate to root/data directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
data_dir = os.path.join(root_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

# Save matched URLs
with open(os.path.join(data_dir, 'matched_articles.txt'), 'w') as f:
    for url in matched_urls:
        f.write(url + "\n")

print("Matching URLs saved to matched_articles.txt")
