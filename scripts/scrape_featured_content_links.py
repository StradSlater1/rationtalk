from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import csv
import undetected_chromedriver as uc
import numpy as np
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime

# 1) Define your fixed topics and pre-seed the dict
topics = ['U.S.', 'World', 'Business', 'Technology',
          'Entertainment', 'Sports', 'Science', 'Health']
topic_articles = {topic: [] for topic in topics}

current_url = 'https://news.google.com/home?hl=en-US&gl=US&ceid=US:en'

# 2) Initialize driver (headless by default in CI)
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

# 3) Load the Google News homepage and grab the topic tabs
driver.get(current_url)
wait = WebDriverWait(driver, 15)  # increase timeout for CI
raw_tabs = wait.until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, 'brSCsc'))
)

# 4) Build a mapping of tab-text → href
tab_map = {}
for tab in raw_tabs:
    txt = tab.text.strip()
    if txt in topics:
        tab_map[txt] = tab.get_attribute('href')

# Debug output for CI logs
print("DEBUG: available tabs:", list(tab_map.keys()))

# 5) Iterate in fixed order and scrape articles
i = 0
for topic in topics:
    link = tab_map.get(topic)
    if not link:
        print(f"WARNING: no tab found for topic {topic!r}, skipping")
        continue

    driver.get(link)
    try:
        article_divs = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'LU3Rqb'))
        )
    except TimeoutException:
        print(f"WARNING: no articles loaded for {topic!r}, skipping")
        continue

    success_count = 0
    for article in article_divs:
        if success_count >= 10:
            break
        try:
            coverage_link = article.find_element(By.CLASS_NAME, 'jKHa4e').get_attribute('href')
            photo_link    = article.find_element(By.CLASS_NAME, 'Quavad').get_attribute('src')
            topic_articles[topic].append((i, coverage_link, photo_link))
            i += 1
            success_count += 1
        except NoSuchElementException:
            continue

    print(f"Collected {success_count} valid articles for topic '{topic}'.")

# 6) Equalize list lengths by padding with placeholders
max_length = max(len(lst) for lst in topic_articles.values())
j = 0
for key, lst in topic_articles.items():
    if len(lst) < max_length:
        deficit = max_length - len(lst)
        lst.extend([(f"{j}_empty", "0", "0")] * deficit)
        j += 1

# 7) Write out to CSV
article_links = pd.DataFrame({
    topic: [entry for entry in entries]
    for topic, entries in topic_articles.items()
})
article_links.to_csv('data/featured_content_links.csv', index=False)

driver.quit()


