from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import re
import pandas as pd
import time
from ast import literal_eval
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def scrape_links_from_script(url):
    # Initialize the WebDriver in headless mode
    opts = FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)

    urls = []
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        script_elements = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//script[@class="ds:1"]'))
        )

        if not script_elements:
            print("No <script> tags with class 'ds:1' found.")
            return []

        url_pattern = re.compile(r'(https?://\S+)')
        for idx, script in enumerate(script_elements, start=1):
            content = script.get_attribute('innerHTML')
            found = url_pattern.findall(content)
            if found:
                for u in found:
                    cleaned = u.rstrip('\'"<>.,);')
                    if cleaned.startswith("https://www"):
                        urls.append(cleaned.split('"')[0])
            else:
                print(f"No URLs found in script #{idx} with class 'ds:1'.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    return urls

def extract_text_single_article(url, driver, articles, article_topic, photo_link):
    try:
        driver.set_page_load_timeout(20)
        try:
            driver.get(url)
        except TimeoutException:
            driver.execute_script("window.stop();")
            print(f"Timeout loading page: {url}")

        try:
            wait = WebDriverWait(driver, 5)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "p")))
        except TimeoutException:
            driver.execute_script("window.stop()")
            print(f"Timeout waiting for <p> tag on: {url}")

        title_elems = driver.find_elements(By.TAG_NAME, "h1")
        title = title_elems[0].text if title_elems else "No title found"

        paras = driver.find_elements(By.TAG_NAME, "p")
        paragraph_list = [p.text for p in paras]

        articles['Title'].append(title)
        articles['Link'].append(url)
        articles['Paragraphs'].append(paragraph_list)
        articles['Topic'].append(article_topic)
        articles['Image'].append(photo_link)

        print(f"Extracted: {title}")

    except Exception as e:
        print(f"An unexpected error for URL {url}: {e}")

def extract_text(urls, article_topic, photo_link, index, driver):
    articles = {'Title': [], 'Link': [], 'Paragraphs': [], 'Topic': [], 'Image': []}

    for u in urls:
        if "dailymail" in u:
            continue
        extract_text_single_article(u, driver, articles, article_topic, photo_link)

    df = pd.DataFrame(articles)
    df.to_csv(f'data/article_data/{index}.csv', index=False)
    print(df)

if __name__ == "__main__":
    topics = ['U.S.', 'World', 'Business', 'Technology', 'Entertainment', 'Sports', 'Science', 'Health']
    converters = {col: literal_eval for col in topics}
    todays_news = pd.read_csv('data/featured_content_links.csv', encoding='utf-8', converters=converters)

    # Initialize a single headless driver for article extraction
    opts = FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)
    driver.set_page_load_timeout(30)

    w = 1
    for topic in topics:
        for link in todays_news[topic]:
            index, target_url, photo_link = link
            if target_url == "0":
                continue
            print(f"Processing [{w}/80] topic={topic}, url={target_url}")
            urls = scrape_links_from_script(target_url)
            extract_text(list(set(urls)), topic, photo_link, index, driver)
            w += 1

    driver.quit()
    print("All articles scraped and saved.")
