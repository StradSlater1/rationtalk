from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import pandas as pd
import time
import csv
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
import numpy as np
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime


current_url = 'https://news.google.com/home?hl=en-US&gl=US&ceid=US:en'
driver = webdriver.Firefox()

driver.get(current_url)


wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
topic_tabs = wait.until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, 'brSCsc'))
    )

topics = ['U.S.', 'World', 'Business', 'Technology', 'Entertainment', 'Sports', 'Science', 'Health']

for topic in topic_tabs:
    if topic.text not in topics:
        topic_tabs.remove(topic)

topic_links = []
topic_articles = {}
topic_tabs = topic_tabs[2:]

for topic in topic_tabs:
    topic_articles[topic.text] = []
    topic_links.append(topic.get_attribute('href'))


i = 0

for link, topic in zip(topic_links, topics):
    driver.get(link)

    # Wait until at least one <div class="LU3Rqb"> is present
    article_divs = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'LU3Rqb'))
    )

    # Reset success counter for this topic
    success_count = 0

    # Iterate through all articles until we've collected 10 valid ones
    for article in article_divs:
        if success_count >= 10:
            break  # We already have 10; move on to the next topic

        try:
            coverage_link = article.find_element(By.CLASS_NAME, 'jKHa4e')
            photo_link    = article.find_element(By.CLASS_NAME, 'Quavad')

            final_photo_link  = photo_link.get_attribute('src')
            final_story_link  = coverage_link.get_attribute('href')

            # Append this (i, story, photo) tuple to the list for this topic
            topic_articles[topic].append((i, final_story_link, final_photo_link))

            # Increment both counters
            i += 1
            success_count += 1

        except NoSuchElementException:
            # If either element is missing, just skip this article
            continue

    # (Optionally) if you want to know how many you actually found:
    print(f"Collected {success_count} valid articles for topic '{topic}'.")
    

max_length = max(len(lst) for lst in topic_articles.values())

j = 0
for key, lst in topic_articles.items():
    if len(lst) < max_length:
        deficit = max_length - len(lst)
        lst.extend([(f"{j}_empty","0")] * deficit)
        j += 1
article_links = pd.DataFrame(topic_articles)


article_links.to_csv('data/featured_content_links.csv', index=False)

driver.quit()

