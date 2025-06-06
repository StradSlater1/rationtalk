from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import pandas as pd
import time
from ast import literal_eval
from selenium.common.exceptions import TimeoutException



def scrape_links_from_script(url):
    # Set up Chrome options

    # Initialize the WebDriver (Selenium Manager handles driver installation)
    driver = webdriver.Firefox()
    urls = []
    try:
        # Open the specified URL
        driver.get(url)

        # Wait until at least one <script> tag with class "ds:1" is present
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
        script_elements = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//script[@class="ds:1"]'))
        )

        if not script_elements:
            print("No <script> tags with class 'ds:1' found.")
            return

        # Regular expression pattern to identify URLs
        url_pattern = re.compile(
            r'(https?://\S+)'  # Matches http:// or https:// followed by non-whitespace characters
        )

        # Iterate through all matching <script> tags
        for idx, script in enumerate(script_elements, start=1):
            script_content = script.get_attribute('innerHTML')

            # Find all URLs in the script content
            urls_found = url_pattern.findall(script_content)

            if urls_found:
                for url in urls_found:
                    # Clean the URL by removing trailing characters that are not part of the URL
                    cleaned_url = url.rstrip('\'"<>.,);')
                    if url.startswith("https://www"):
                        cleaned_url = cleaned_url.split('"')[0]
                        urls.append(cleaned_url)
            else:
                print(f"No URLs found in script #{idx} with class 'ds:1'.\n")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Always quit the driver to free resources
        driver.quit()
    return urls



def extract_text_single_article(url, driver, articles, article_topic, photo_link):
    try:
        # Set the page load timeout to 20 seconds
        driver.set_page_load_timeout(20)
        try:
            driver.get(url)
        except TimeoutException:
            # If the page load times out, stop the page from loading further
            driver.execute_script("window.stop();")
            print(f"Timeout while loading page: {url}")
        
        # Wait for a <p> tag with a shorter timeout (5 seconds)
        try:
            wait = WebDriverWait(driver, 5)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "p")))
        except TimeoutException:
            driver.execute_script("window.stop();")
            print("Timeout waiting for <p> tag; stopping page load and proceeding with available content.")
        
        # Extract the title from the first <h1> tag
        title_elements = driver.find_elements(By.TAG_NAME, "h1")
        title = title_elements[0].text if title_elements else "No title found"
        
        # Extract all paragraphs
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        paragraph_list = [paragraph.text for paragraph in paragraphs]
        
        # Append data to the articles dictionary
        articles['Title'].append(title)
        articles['Link'].append(url)
        articles['Paragraphs'].append(paragraph_list)
        articles['Topic'].append(article_topic)
        articles['Image'].append(photo_link)
        
        print(title)
        print(paragraph_list)
        print()
        
    except TimeoutException:
        print(f"Timeout while waiting for elements on page: {url}")
    except Exception as e:
        print(f"An unexpected error has occurred for URL {url}: {e}")


def extract_text(urls, article_topic, photo_link, index, driver):
    articles = {

        'Title' : [],
        'Link' : [],
        'Paragraphs' : [],
        'Topic' : [],
        'Image' : []
    }

    for url in urls:
        if "dailymail" in url:
            continue
        try:
            extract_text_single_article(url, driver, articles, article_topic, photo_link)
        except Exception as e:
            raise SystemExit(f"WebDriver initialization failed: {e}")



    # Create DataFrame and save to CSV
    df = pd.DataFrame(articles)
    df.to_csv(f'data/article_data/{index}.csv', index=False)
    print(df)


if __name__ == "__main__":
    # Replace this URL with the target webpage you want to scrape
    topics = ['U.S.', 'World', 'Business', 'Technology', 'Entertainment', 'Sports', 'Science', 'Health']
    converters = {col: literal_eval for col in topics}
    todays_news = pd.read_csv('data/featured_content_links.csv', encoding='utf-8',  converters=converters)
    topics_raw_text = {}
    w = 1

    driver = webdriver.Firefox()
    driver.set_page_load_timeout(30)

    for topic in topics:
        for link in todays_news[topic]:
            print(link)
            index = link[0]
            target_url = link[1]
            photo_link = link[2]
            if target_url == "0":
                continue
            urls = scrape_links_from_script(target_url)
            urls = list(set(urls))
            extract_text(urls, topic, photo_link, index, driver)
            print(f"{w}/80 stories extracted")
            w += 1

    driver.quit()
    print("All articles have been scraped and saved to CSV files.")