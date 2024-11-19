from article_clean_class import Articles
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer
from hdbscan import HDBSCAN
import numpy as np
from ast import literal_eval

# Ensure NLTK resources are downloaded
nltk.download('punkt')

# Load your articles
article = pd.read_csv('Scraped_news/biden_oct_7.csv', encoding='utf-8', converters={'Paragraphs': literal_eval})
articles = Articles(article)

# Clean the articles
cleaned_articles = articles.clean_articles()

# Create a DataFrame from cleaned articles
articles_df = pd.DataFrame({'text': cleaned_articles})

# Split each article into sentences
sentences = []
for article in articles_df['text']:
    for sentence in sent_tokenize(article):
        sentences.append(sentence.strip())  # Strip leading/trailing whitespace

# Remove duplicate sentences
unique_sentences = list(set(sentences))

# Alternatively, you can use pandas to remove duplicates:
# sentence_df = pd.DataFrame({'sentence': sentences})
# sentence_df = sentence_df.drop_duplicates(subset='sentence')
# unique_sentences = sentence_df['sentence'].tolist()

# Sentiment analysis using VADER
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    score = analyzer.polarity_scores(text)
    if score['compound'] >= 0.05:
        return 'positive'
    elif score['compound'] <= -0.05:
        return 'negative'
    else:
        return 'neutral'

# Classify unique sentences into sentiments
sentiments = [get_sentiment(sentence) for sentence in unique_sentences]

# Create a DataFrame for sentences and their sentiments
sentence_df = pd.DataFrame({'sentence': unique_sentences, 'sentiment': sentiments})

# Separate sentences by sentiment
positive_sentences = sentence_df[sentence_df['sentiment'] == 'positive']['sentence'].tolist()
negative_sentences = sentence_df[sentence_df['sentiment'] == 'negative']['sentence'].tolist()

# Function to perform HDBSCAN clustering and print clusters with sentences
def hdbscan_clustering_and_print(sentences, sentiment_label):
    if not sentences:
        print(f"\nNo {sentiment_label} sentences to cluster.")
        return

    # Initialize the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Compute embeddings
    embeddings = model.encode(sentences, show_progress_bar=True)

    # Perform HDBSCAN clustering
    hdbscan_clusterer = HDBSCAN(min_cluster_size=5, metric='euclidean', cluster_selection_method='eom')
    cluster_labels = hdbscan_clusterer.fit_predict(embeddings)

    # Create a DataFrame with sentences and their cluster labels
    cluster_df = pd.DataFrame({'sentence': sentences, 'cluster': cluster_labels})

    # Get unique clusters (excluding noise points labeled as -1)
    unique_clusters = set(cluster_labels)
    unique_clusters.discard(-1)  # Remove noise label if present

    # Print clusters and their top 5 representative sentences
    print(f"\n{sentiment_label.capitalize()} Sentiment Clusters:")
    for cluster_num in unique_clusters:
        cluster_indices = np.where(cluster_labels == cluster_num)[0]
        cluster_embeddings = embeddings[cluster_indices]
        if len(cluster_embeddings) == 0:
            continue

        # Compute centroid of the cluster
        centroid = np.mean(cluster_embeddings, axis=0)

        # Compute distances to centroid
        distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)

        # Get sentences and distances
        cluster_sentences = [sentences[i] for i in cluster_indices]
        cluster_info = list(zip(cluster_sentences, distances))

        # Sort sentences by distance to centroid
        cluster_info.sort(key=lambda x: x[1])

        # Select top N sentences
        top_n = 5
        top_sentences = [s for s, d in cluster_info[:top_n]]

        print(f"\nCluster {cluster_num} (Total Sentences: {len(cluster_sentences)}):")
        print(f"Top {top_n} representative sentences:")
        for sentence in top_sentences:
            print(f" - {sentence}")

# Cluster and print positive sentences using HDBSCAN
hdbscan_clustering_and_print(positive_sentences, 'positive')

# Cluster and print negative sentences using HDBSCAN
hdbscan_clustering_and_print(negative_sentences, 'negative')

