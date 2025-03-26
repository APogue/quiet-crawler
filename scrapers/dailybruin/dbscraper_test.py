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

# code output indicates it finds all "relevant" URL's before scraping, what if the window of iterest is years long? Doesn't it still need to scroll? How will it pre-assess how many URL's of iterest there are? 
# my point is, if more scrolling is required to count the URL's of interest once the end date is reached, then either eliminate the pre-count entirely or manage the scrolling speed for the count 
# if the window of interest is longer than say, two months. 




# Regex pattern to match date in URLs
date_pattern = r'/([0-9]{4})/([0-9]{2})/([0-9]{2})(?:/|-)'

# Randomize user-agent with more variety
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
]

def main():
    # Configuration
    url = 'https://dailybruin.com/category/news'
    keywords = ['marajuana', 'key', 'representative']  # adjust keywords as needed
    # Target date range
    start_date = datetime(2022, 11, 4)
    end_date = datetime(2022, 11, 16)
    
    # Adjust this based on how far back you need to go
    max_scroll_attempts = 200
    
    # Throttling - reducing this allows faster scrolling but may trigger anti-bot measures
    throttle_factor = 0.7  # 1.0 = normal, 0.5 = faster, 2.0 = slower
    
    user_agent = random.choice(user_agents)
    
    # Create cache directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    data_dir = os.path.join(root_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Set up Selenium
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
        
        # Then navigate to the news section
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Accelerated date-based scrolling strategy
        all_links = set()
        oldest_date_found = datetime.now()
        consecutive_no_new_links = 0
        max_consecutive_no_new = 3  
        total_scroll_attempts = 0
        
        print(f"Target date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"Maximum scroll attempts: {max_scroll_attempts}")
        
        # First scroll - large jump to get past recent articles quickly
        scroll_height = 5000
        driver.execute_script(f"window.scrollTo(0, {scroll_height});")
        time.sleep(1.0 * throttle_factor)
        
        while total_scroll_attempts < max_scroll_attempts:
            total_scroll_attempts += 1
            
            # Extract links before scrolling
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            current_links_with_dates = []
            
            # Get all links with their dates
            for a in soup.find_all('a', href=True):
                if (m := re.search(date_pattern, a['href'])):
                    try:
                        url_date = datetime(*map(int, m.groups()))
                        current_links_with_dates.append((a['href'], url_date))
                    except ValueError:
                        continue
            
            # Extract just the links for set operations
            current_links = {link for link, _ in current_links_with_dates}
            new_links = current_links - all_links
            all_links.update(new_links)
            
            # Find the oldest date in current batch
            if current_links_with_dates:
                current_oldest = min(current_links_with_dates, key=lambda x: x[1])[1]
                oldest_date_found = min(oldest_date_found, current_oldest)
                print(f"Scroll attempt {total_scroll_attempts}/{max_scroll_attempts}: Oldest article date found: {oldest_date_found.strftime('%Y-%m-%d')}")
                
                # Calculate progress percentage
                days_total = (datetime.now() - start_date).days
                days_remaining = (oldest_date_found - start_date).days
                if days_total > 0:
                    progress = max(0, min(100, 100 * (1 - days_remaining / days_total)))
                    print(f"Progress: approximately {progress:.1f}%")
                
                # Check if we've gone past our target start date
                if oldest_date_found < start_date:
                    print(f"Found articles older than start date ({start_date.strftime('%Y-%m-%d')}), stopping scroll")
                    break
                
                # Always use end_date as reference since we'll encounter it first
                # in reverse chronological order (newest to oldest)
                reference_date = end_date
                
                # Accelerated scrolling based on how far we are from target date
                years_diff = oldest_date_found.year - reference_date.year
                months_diff = years_diff * 12 + (oldest_date_found.month - reference_date.month)
                
                # More aggressive tier thresholds for faster scrolling to older content
                if years_diff > 1.5 or months_diff > 18:
                    # More than 1.5 years away (was 2), use extra-aggressive scrolling
                    scroll_height += 6000  # Increased from 5000
                    driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                    time.sleep(0.6 * throttle_factor)  # Reduced from 0.7
                elif years_diff > 0 or months_diff > 2:  # Reduced from 3 months
                    # 2+ months away, use very aggressive scrolling
                    scroll_height += 4000  # Increased from 3000
                    driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                    time.sleep(0.7 * throttle_factor)  # Reduced from 0.8
                elif months_diff > 0:
                    # Within 3 months, use medium scrolling
                    scroll_height += 1500
                    driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                    time.sleep(0.8 * throttle_factor)
                else:
                    # Same month, use smaller scrolls
                    for i in range(2):
                        scroll_height += random.randint(400, 800)
                        driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                        time.sleep(0.5 * throttle_factor)
            
            # Safety check for no new links
            if not new_links:
                consecutive_no_new_links += 1
                print(f"No new links found (attempt {consecutive_no_new_links}/{max_consecutive_no_new})")
                
                # Try more aggressive scrolling when stuck
                if consecutive_no_new_links >= 2:
                    print("Trying more aggressive scrolling...")
                    # Try a random big jump
                    scroll_height += random.randint(1000, 3000)
                    driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                    time.sleep(1.5 * throttle_factor)
                    
                if consecutive_no_new_links >= max_consecutive_no_new:
                    print("No new links after multiple attempts, stopping scroll")
                    break
            else:
                consecutive_no_new_links = 0
                print(f"Found {len(new_links)} new links, total: {len(all_links)}")
                
                # Success, continue with normal scrolling
                scroll_height += random.randint(700, 1200)
                driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                time.sleep(0.7 * throttle_factor)
        
        # Filter links by date
        date_filtered_links = []
        for link in all_links:
            if (m := re.search(date_pattern, link)):
                url_date = datetime(*map(int, m.groups()))
                if start_date <= url_date <= end_date:
                    date_filtered_links.append(link)
        
        print(f"Found {len(date_filtered_links)} links within date range")
        
        # Process articles sequentially (avoiding threading issues)
        matched_urls = []
        for link in date_filtered_links:
            print(f"Checking {link}...")
            try:
                # Try with requests first (faster)
                headers = {"User-Agent": random.choice(user_agents)}
                response = requests.get(link, headers=headers, timeout=10)
                article_source = response.text
                
                article_soup = BeautifulSoup(article_source, 'html.parser')
                text = article_soup.get_text().lower()
                
                if any(kw.lower() in text for kw in keywords):
                    matched_urls.append(link)
                    print(f"✓ Match found: {link}")
            except Exception as e:
                print(f"Error checking {link}: {e}")
                # Fallback to Selenium if requests fails
                try:
                    driver.get(link)
                    time.sleep(random.uniform(1, 2))
                    article_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    text = article_soup.get_text().lower()
                    
                    if any(kw.lower() in text for kw in keywords):
                        matched_urls.append(link)
                        print(f"✓ Match found (via Selenium): {link}")
                except Exception as se:
                    print(f"Selenium also failed for {link}: {se}")
    
    finally:
        driver.quit()
    
    # Save matched URLs to file
    with open(os.path.join(data_dir, 'matched_articles.txt'), 'w') as f:
        for url in matched_urls:
            f.write(url + "\n")
    
    print(f"Found {len(matched_urls)} matching articles")
    print("Matching URLs saved to matched_articles.txt")

if __name__ == "__main__":
    main()
