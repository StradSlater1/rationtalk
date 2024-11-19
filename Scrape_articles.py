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

'''
def scroll_to_bottom(driver, max_scrolls=5, pause_time=1):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
'''

def extract_text_single_article(url, driver, articles):

        try:
            driver.get(url)

            # Wait until at least one <p> tag is present
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "p")))

            # Extract the title from the first <h1> tag
            title_elements = driver.find_elements(By.TAG_NAME, "h1")

            if title_elements:
                title = title_elements[0].text
            else:
                title = "No title found"


            # Extract all paragraphs
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            paragraph_list = []

            for paragraph in paragraphs:
                text = paragraph.text
                paragraph_list.append(text)

            # Append data to the articles dictionary
            articles['Title'].append(title)
            articles['Link'].append(url)
            articles['Paragraphs'].append(paragraph_list)
            print(title)
            print(paragraph_list)
            print()

        except TimeoutException:
            print(f"Timeout while loading page: {url}")

        except Exception as e:
            print(f"An unexpected error has occurred for URL {url}")



def extract_text(urls, index, driver):
    articles = {

        'Title' : [],
        'Link' : [],
        'Paragraphs' : []
    }

    for url in urls:
        try:
            extract_text_single_article(url, driver, articles)
        except Exception as e:
            raise SystemExit(f"WebDriver initialization failed: {e}")



    # Create DataFrame and save to CSV
    df = pd.DataFrame(articles)
    df.to_csv(f'Scraped_news/102824/{index}.csv', index=False)
    print(df)


if __name__ == "__main__":
    # Replace this URL with the target webpage you want to scrape
    topics = ['U.S.', 'World', 'Business', 'Technology', 'Entertainment', 'Sports', 'Science', 'Health']
    converters = {col: literal_eval for col in topics}
    todays_news = pd.read_csv('10-28-24.csv', encoding='utf-8',  converters=converters)
    topics_raw_text = {}
    w = 1

    driver = webdriver.Firefox()
    driver.set_page_load_timeout(30)

    for topic in topics:
        for link in todays_news[topic]:
            index = link[0]
            target_url = link[1]
            urls = scrape_links_from_script(target_url)
            urls = list(set(urls))
            extract_text(urls, index, driver)
            print(f"{w}/80 stories extracted")
            w += 1

    from article_clean_class import Articles
    from ast import literal_eval
    import nltk
    from sklearn.cluster import DBSCAN
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import pandas as pd
    from openai import OpenAI

    sum_ques = {
        "Title": [],
        "Summary": [],
        "Question 1": [],
        "Question 2": [],
        "Question 3": []
    }

    for i in range(0, 80):
        article = pd.read_csv(f'Scraped_news/102824/{i}.csv', encoding='utf-8', converters={'Paragraphs': literal_eval})
        articles = Articles(article)

        cleand_articles = articles.clean_articles()

        all_sentences = []
        article_sentences = []  # To keep track of sentences in each article

        for article in cleand_articles:
            sentences = nltk.sent_tokenize(article)
            all_sentences.extend(sentences)
            article_sentences.append(sentences)

        # Step 2: Embed the Sentences
        model = SentenceTransformer('all-MiniLM-L6-v2')  # You can choose other models as well
        embeddings = model.encode(all_sentences)

        # Step 3: Cluster the Sentences using DBSCAN for tighter clusters
        dbscan_model = DBSCAN(eps=0.4, min_samples=3, metric='cosine')  # Adjust 'eps' as needed
        cluster_assignments = dbscan_model.fit_predict(embeddings)

        # Step 4: Organize sentences into clusters
        unique_labels = set(cluster_assignments)
        clusters = {label: [] for label in unique_labels if label != -1}  # Exclude noise points (-1)

        for idx, label in enumerate(cluster_assignments):
            if label != -1:
                clusters[label].append((all_sentences[idx], embeddings[idx]))


        # Function to find the most representative sentence (closest to the centroid)
        def find_representative_sentence(cluster_sentences):
            if len(cluster_sentences) == 1:
                return cluster_sentences[0][0]

            cluster_embeddings = np.array([embedding for _, embedding in cluster_sentences])
            centroid = np.mean(cluster_embeddings, axis=0)
            distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
            closest_index = np.argmin(distances)
            return cluster_sentences[closest_index][0]


        # Optionally: Evaluate the frequency of similar facts across articles
        for label, cluster_sentences in clusters.items():
            articles_with_sentences = len(set([sentence for sentence, _ in cluster_sentences]))

        # Collect summary sentences
        summary_sentences = []

        for label, cluster_sentences in clusters.items():
            representative_sentence = find_representative_sentence(cluster_sentences)
            summary_sentences.append(representative_sentence)
            # print(representative_sentence)
            # print()

        combined_summary = ' '.join(summary_sentences)

        # Set your OpenAI API key
        client = OpenAI(
            api_key='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'
        )


        def summarize(combined_summary):
            prompt = f"Summarize this passage in a paragraph or two. Only use information from the passage and make it well written. Also provide a title for the topic. : {combined_summary} Afterwards provide three thoughtful questions about the topic that someone might ask another in a conversation about their thoughts on the topic. Order the response with the title first, then the summary, then the three questions.\n\n"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )

            return response.choices[0].message.content


        summary = summarize(combined_summary)
        try:
            divided = summary.splitlines()
            sum_ques['Question 3'].append(divided[-1])
            sum_ques['Question 2'].append(divided[-2])
            sum_ques['Question 1'].append(divided[-3])
            sum_ques['Title'].append(divided[0])
            sum_ques['Summary'].append(divided[1:-3])
        except Exception as e:
            print("Format error")

        print(f"{i + 1}/80 summaries done")
    sum_ques_df = pd.DataFrame(sum_ques)
    sum_ques_df.to_csv(f'Scraped_news/102824/all_summaries.csv')

