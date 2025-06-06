import os
import random
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

# Regex pattern to match full date in URLs (e.g., /YYYY/MM/DD/...)
full_date_pattern = r'/([0-9]{4})/([0-9]{2})/([0-9]{2})(?:/|-)?'

# List of user agents for random selection
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
]

def remove_old_content(driver, threshold=1000):
    """Remove off-screen articles to limit DOM growth (assumes articles are in <article> tags)."""
    driver.execute_script("""
        var threshold = arguments[0];
        var articles = document.querySelectorAll("article");
        articles.forEach(function(article) {
            var rect = article.getBoundingClientRect();
            if (rect.bottom < -threshold) {
                article.parentNode.removeChild(article);
            }
        });
    """, threshold)

def get_pub_date(url):
    """
    Extract publication date from a URL by matching the full date format.
    Relative URLs are completed by adding the base domain.
    Returns a datetime object or None.
    """
    # Skip non-article links (like author pages)
    if url.startswith("/author/"):
        return None
    # Complete relative URLs
    if url.startswith("/"):
        url = "https://dailybruin.com" + url
    m = re.search(full_date_pattern, url)
    if m:
        try:
            return datetime(*map(int, m.groups()))
        except Exception:
            return None
    return None

def main():
    # Configuration
    url = 'https://dailybruin.com/category/news'
    keywords = ['marajuana', 'key', 'representative']  # adjust keywords as needed
    # Target date range
    start_date = datetime(2022, 11, 4)
    end_date = datetime(2022, 11, 16)
    max_scroll_attempts = 200
    throttle_factor = 0.7

    user_agent = random.choice(user_agents)

    # Create cache directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    data_dir = os.path.join(root_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    # Set up Selenium options
    options = webdriver.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1280,800')

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        # Mimic human behavior: visit homepage first
        driver.get('https://dailybruin.com')
        time.sleep(random.uniform(1, 2))
        # Navigate to the news section
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        all_links = set()
        oldest_date_found = datetime.now()
        total_scroll_attempts = 0
        scroll_height = 5000

        print(f"Target date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"Maximum scroll attempts: {max_scroll_attempts}")

        driver.execute_script(f"window.scrollTo(0, {scroll_height});")
        time.sleep(1.0 * throttle_factor)

        while total_scroll_attempts < max_scroll_attempts:
            total_scroll_attempts += 1
            remove_old_content(driver, threshold=1000)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            current_links_with_dates = []
            for a in soup.find_all('a', href=True):
                link = a['href']
                # Skip non-article links (like author pages)
                if link.startswith("/author/"):
                    continue
                if link.startswith("/"):
                    link = "https://dailybruin.com" + link
                m = re.search(full_date_pattern, link)
                if m:
                    try:
                        url_date = datetime(*map(int, m.groups()))
                        current_links_with_dates.append((link, url_date))
                    except Exception:
                        continue
            # Update link collection
            current_links = {link for link, _ in current_links_with_dates}
            new_links = current_links - all_links
            all_links.update(new_links)
            # Update oldest date found
            if current_links_with_dates:
                valid_dates = [d for _, d in current_links_with_dates]
                current_oldest = min(valid_dates)
                oldest_date_found = min(oldest_date_found, current_oldest)
                print(f"Scroll {total_scroll_attempts}: Oldest article date found: {oldest_date_found.strftime('%Y-%m-%d')}")
            # Stop scrolling if articles older than start_date are reached
            if current_links_with_dates and oldest_date_found < start_date:
                print(f"Found articles older than start date ({start_date.strftime('%Y-%m-%d')}), stopping scroll")
                break
            # Adjust scrolling based on how far we are from the target
            years_diff = oldest_date_found.year - end_date.year
            months_diff = years_diff * 12 + (oldest_date_found.month - end_date.month)
            if years_diff > 1.5 or months_diff > 18:
                scroll_height += 6000
                driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                time.sleep(0.6 * throttle_factor)
            elif years_diff > 0 or months_diff > 2:
                scroll_height += 4000
                driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                time.sleep(0.7 * throttle_factor)
            elif months_diff > 0:
                scroll_height += 1500
                driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                time.sleep(0.8 * throttle_factor)
            else:
                scroll_height += random.randint(400, 800)
                driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                time.sleep(0.5 * throttle_factor)

        # Filter collected URLs by publication date
        date_filtered_links = []
        for link in all_links:
            pub_date = get_pub_date(link)
            if pub_date and (start_date <= pub_date <= end_date):
                date_filtered_links.append(link)

        print(f"Collected {len(all_links)} URLs in total.")
        print(f"Found {len(date_filtered_links)} URLs within date range.")

        # Process articles for keyword matching
        matched_urls = []
        for link in date_filtered_links:
            print(f"Checking {link}...")
            try:
                headers = {"User-Agent": random.choice(user_agents)}
                response = requests.get(link, headers=headers, timeout=10)
                article_source = response.text
                article_soup = BeautifulSoup(article_source, 'html.parser')
                text = article_soup.get_text().lower()
                if any(kw.lower() in text for kw in keywords):
                    matched_urls.append(link)
                    print(f"✓ Match found: {link}")
            except Exception as e:
                print(f"Error checking {link} with requests: {e}")
                try:
                    driver.get(link)
                    time.sleep(random.uniform(1, 2))
                    article_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    text = article_soup.get_text().lower()
                    if any(kw.lower() in text for kw in keywords):
                        matched_urls.append(link)
                        print(f"✓ Match found via Selenium: {link}")
                except Exception as se:
                    print(f"Selenium also failed for {link}: {se}")

    finally:
        driver.quit()

    output_file = os.path.join(data_dir, 'matched_articles.txt')
    with open(output_file, 'w') as f:
        for url in matched_urls:
            f.write(url + "\n")

    print(f"Found {len(matched_urls)} matching articles")
    print(f"Matching URLs saved to {output_file}")

if __name__ == "__main__":
    main()
