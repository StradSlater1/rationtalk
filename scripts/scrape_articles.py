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
    WebDriverException,
    StaleElementReferenceException
)

def get_driver():
    opts = FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)
    driver.set_page_load_timeout(20)
    return driver

def safe_load(url, driver):
    """Try loading url on driver; on fatal failure, restart driver once."""
    try:
        driver.get(url)
        return driver
    except (WebDriverException, TimeoutException) as e:
        print(f"Page-load error on {url}: {e}. Restarting driver and retrying…")
        try:
            driver.quit()
        except:
            pass
        new_driver = get_driver()
        try:
            new_driver.get(url)
            return new_driver
        except Exception as e2:
            print(f"Retry failed on {url}: {e2}. Skipping.")
            try:
                new_driver.quit()
            except:
                pass
            return None

def scrape_links_from_script(url):
    driver = get_driver()
    urls = []
    try:
        driver.get(url)
        scripts = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//script[@class="ds:1"]'))
        )
        pat = re.compile(r'(https?://\S+)')
        for s in scripts:
            for u in pat.findall(s.get_attribute('innerHTML')):
                cleaned = u.rstrip('\'"<>.,);')
                if cleaned.startswith("https://www"):
                    urls.append(cleaned.split('"')[0])
    except Exception as e:
        print(f"Error scraping links from {url}: {e}")
    finally:
        driver.quit()
    return list(set(urls))

def extract_text_single_article(url, driver, articles, topic, photo):
    driver = safe_load(url, driver)
    if not driver:
        return driver  # skip this URL but keep driver state

    # wait for paragraph presence
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "p")))
    except TimeoutException:
        print(f"No <p> on {url}")

    # title
    titles = driver.find_elements(By.TAG_NAME, "h1")
    title = titles[0].text if titles else "No title found"

    # paragraphs
    paras = driver.find_elements(By.TAG_NAME, "p")
    texts = []
    for p in paras:
        try:
            texts.append(p.text)
        except StaleElementReferenceException:
            continue

    articles['Title'].append(title)
    articles['Link'].append(url)
    articles['Paragraphs'].append(texts)
    articles['Topic'].append(topic)
    articles['Image'].append(photo)

    print(f"Extracted: {title}")
    return driver

def extract_text_for_topic(urls, topic, photo, index):
    driver = get_driver()
    articles = {'Title': [], 'Link': [], 'Paragraphs': [], 'Topic': [], 'Image': []}

    for url in urls:
        if "dailymail" in url:
            continue
        driver = extract_text_single_article(url, driver, articles, topic, photo)
        # if driver is None, start a fresh one for next URL
        if driver is None:
            driver = get_driver()

    try:
        driver.quit()
    except:
        pass

    df = pd.DataFrame(articles)
    df.to_csv(f'data/article_data/{index}.csv', index=False)
    print(f"Saved {len(df)} articles for {topic} to {index}.csv")

if __name__ == "__main__":
    topics = ['U.S.', 'World', 'Business', 'Technology',
              'Entertainment', 'Sports', 'Science', 'Health']
    today = pd.read_csv(
        'data/featured_content_links.csv',
        converters={t: literal_eval for t in topics}
    )

    counter = 1
    for topic in topics:
        for index, url, photo in today[topic]:
            if url == "0":
                continue
            print(f"\nBatch [{counter}/80] topic={topic}, url={url}")
            links = scrape_links_from_script(url)
            extract_text_for_topic(links, topic, photo, index)
            counter += 1

    print("All articles scraped and saved.")
