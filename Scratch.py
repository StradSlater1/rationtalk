from article_clean_class import Articles
from ast import literal_eval
import nltk
from sklearn.cluster import DBSCAN
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from openai import OpenAI

sum_ques = {
    "Title" : [],
    "Summary" : [],
    "Question 1" : [],
    "Question 2" : [],
    "Question 3" : []
}

for i in range(0,80):
    article = pd.read_csv(f'Scraped_news/102824/{i}.csv', encoding='utf-8',  converters={'Paragraphs': literal_eval})
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
    dbscan_model = DBSCAN(eps=0.3, min_samples=3, metric='cosine')  # Adjust 'eps' as needed
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
        print(representative_sentence)
        print()

    combined_summary = ' '.join(summary_sentences)

    # Set your OpenAI API key
    '''
        client = OpenAI(
            api_key=''
        )
        '''


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

    print(f"{i+1}/80 summaries done")
sum_ques_df = pd.DataFrame(sum_ques)
#print(sum_ques)
sum_ques_df.to_csv(f'Scraped_news/102824/all_summaries_lower_eps.csv')

