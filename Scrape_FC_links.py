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
    coverage_links = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'jKHa4e'))
    )
    for article in coverage_links[:10]:
        story_link = article.get_attribute('href')
        topic_articles[topic].append((i, story_link))
        i += 1

article_links = pd.DataFrame(topic_articles)
article_links.to_csv('10-28-24.csv')

driver.quit()

