from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import csv


current_url = 'https://news.google.com/stories/CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2lIOC1DRURCR2R0bTA5RjZrczVpZ0FQAQ?hl=en-US&gl=US&ceid=US%3Aen'
driver = webdriver.Chrome()

driver.get(current_url)

articles = driver.find_elements(By.CLASS_NAME, "ipQwMb")

article_list = []

for i, article in enumerate(articles):
    a_element = article.find_element(By.TAG_NAME, "a")
    link = a_element.get_attribute("href")
    text = article.text

    article_info = {"title": text, "link": link}

    article_list.append(article_info)
i = 0
for article in article_list:
    print(i)
    print(article)
    i += 1
driver.quit()

data = []

for article in article_list:
    try:
        current_url = article['link']
        driver = webdriver.Chrome()

        driver.get(current_url)

        # Scroll to the bottom of the page to load more content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Give time for content to load

        #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "p")))

        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        paragraph_list = []


        for paragraph in paragraphs:
            text = paragraph.text
            print(text)
            print("__________")
            paragraph_list.append(text)

        print(paragraph_list)
        data.append([article["title"], article["link"], paragraph_list])

        driver.quit()

    except Exception as e:
        print("An error has occured")
        continue

df = pd.DataFrame(data, columns=["Title", "Link", "Paragraphs"])
df.to_csv('delta.csv', index=False)
print(df)

