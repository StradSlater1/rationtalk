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
    StaleElementReferenceException,
    WebDriverException
)

def scrape_links_from_script(url):
    opts = FirefoxOptions(); opts.headless = True
    driver = webdriver.Firefox(options=opts)
    driver.set_page_load_timeout(20)

    urls = []
    try:
        driver.get(url)
        scripts = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//script[@class="ds:1"]'))
        )
        pat = re.compile(r'(https?://\S+)')
        for s in scripts:
            for u in pat.findall(s.get_attribute('innerHTML')):
                u2 = u.rstrip('\'"<>.,);')
                if u2.startswith("https://www"):
                    urls.append(u2.split('"')[0])
    except Exception as e:
        print(f"Error scraping links from {url}: {e}")
    finally:
        driver.quit()

    return list(set(urls))


def extract_text_single_article(url, topic, photo, index):
    opts = FirefoxOptions(); opts.headless = True
    driver = webdriver.Firefox(options=opts)
    driver.set_page_load_timeout(20)

    article = {'Title': [], 'Link': [], 'Paragraphs': [], 'Topic': [], 'Image': []}

    try:
        driver.get(url)
    except (TimeoutException, WebDriverException) as e:
        print(f"Skipping {url} due to load error: {e}")
        driver.quit()
        return article

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

    article['Title'].append(title)
    article['Link'].append(url)
    article['Paragraphs'].append(texts)
    article['Topic'].append(topic)
    article['Image'].append(photo)

    print(f"Extracted: {title}")
    driver.quit()
    return article


if __name__ == "__main__":
    topics = ['U.S.', 'World', 'Business', 'Technology',
              'Entertainment', 'Sports', 'Science', 'Health']
    today = pd.read_csv(
        'data/featured_content_links.csv',
        converters={t: literal_eval for t in topics}
    )

    # loop over each link individually
    for w, topic in enumerate(topics, start=1):
        for index, url, photo in today[topic]:
            if url == "0":
                continue
            print(f"\n[{w}/80] topic={topic}, url={url}")
            links = scrape_links_from_script(url)

            # for each article URL in this batch, scrape and save
            for art_url in links:
                art_data = extract_text_single_article(art_url, topic, photo, index)
                df = pd.DataFrame(art_data)
                if not df.empty:
                    df.to_csv(f'data/article_data/{index}.csv', mode='a', header=not pd.io.common.file_exists(f'data/article_data/{index}.csv'), index=False)

    print("All articles scraped and saved.")
