from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import re
import pandas as pd
import time
from ast import literal_eval
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException
)

def scrape_links_from_script(url):
    opts = FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)
    driver.set_page_load_timeout(20)

    urls = []
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        script_elements = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//script[@class="ds:1"]'))
        )
        url_pattern = re.compile(r'(https?://\S+)')
        for script in script_elements:
            content = script.get_attribute('innerHTML')
            for u in url_pattern.findall(content):
                cleaned = u.rstrip('\'"<>.,);')
                if cleaned.startswith("https://www"):
                    urls.append(cleaned.split('"')[0])
    except Exception as e:
        print(f"Error scraping links from {url}: {e}")
    finally:
        driver.quit()

    return list(set(urls))

def extract_text_single_article(url, driver, articles, topic, photo):
    # 1) Try to load the page, skip on any load errors
    try:
        driver.set_page_load_timeout(20)
        driver.get(url)
    except (TimeoutException, WebDriverException) as e:
        print(f"Error loading {url}: {e}")
        return

    # 2) Wait for at least one <p>
    try:
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "p")))
    except TimeoutException:
        driver.execute_script("window.stop()")
        print(f"No <p> on {url}")

    # 3) Extract title
    title_elems = driver.find_elements(By.TAG_NAME, "h1")
    title = title_elems[0].text if title_elems else "No title found"

    # 4) Safely gather paragraphs
    paras = driver.find_elements(By.TAG_NAME, "p")
    paragraph_list = []
    for p in paras:
        try:
            paragraph_list.append(p.text)
        except StaleElementReferenceException:
            continue

    # 5) Append to articles
    articles['Title'].append(title)
    articles['Link'].append(url)
    articles['Paragraphs'].append(paragraph_list)
    articles['Topic'].append(topic)
    articles['Image'].append(photo)

    print(f"Extracted: {title}")

def extract_text_for_topic(urls, topic, photo, index):
    opts = FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)
    driver.set_page_load_timeout(30)

    articles = {'Title': [], 'Link': [], 'Paragraphs': [], 'Topic': [], 'Image': []}
    for url in urls:
        if "dailymail" in url:
            continue
        extract_text_single_article(url, driver, articles, topic, photo)

    driver.quit()

    df = pd.DataFrame(articles)
    df.to_csv(f'data/article_data/{index}.csv', index=False)
    print(f"Saved {len(df)} articles for {topic} to {index}.csv")

if __name__ == "__main__":
    topics = ['U.S.', 'World', 'Business', 'Technology',
              'Entertainment', 'Sports', 'Science', 'Health']
    todays = pd.read_csv(
        'data/featured_content_links.csv',
        converters={t: literal_eval for t in topics}
    )

    w = 1
    for topic in topics:
        for link in todays[topic]:
            index, url, photo = link
            if url == "0":
                continue
            print(f"\nBatch [{w}/80] topic={topic}, url={url}")
            urls = scrape_links_from_script(url)
            extract_text_for_topic(urls, topic, photo, index)
            w += 1

    print("All articles scraped and saved.")
