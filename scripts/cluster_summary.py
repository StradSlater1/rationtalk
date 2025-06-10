
from article_clean_class import Articles
from ast import literal_eval
import nltk
from sklearn.cluster import DBSCAN
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from openai import OpenAI
from nltk.tokenize import sent_tokenize
from numpy.linalg import norm
from collections import defaultdict
from dotenv import load_dotenv
import os

nltk.download('punkt')
nltk.download('punkt_tab')

dotenv_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),  # path to the current script's folder (scripts/)
        "..",                        # go up one level, into the repo root
        ".env"                       # the filename of your env file
    )
)

# 2) Load environment variables from that file
load_dotenv(dotenv_path)

# 3) Now you can grab your key
API_KEY_OPEN_AI = os.getenv("OPENAI_API_KEY")

# Make sure you have NLTK’s punkt tokenizer downloaded:
# nltk.download('punkt')

sum_ques = {
    "Topic" : [],
    "Image" : [],
    "Title": [],
    "Summary": [],
    "Question 1": [],
    "Question 2": [],
    "Question 3": []
}

# Load the SBERT model once:
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

for file_index in range(0, 80):  # adjust upper bound to your total file count
    #
    # 1) Read & clean articles from CSV
    #
    path = f"data/article_data/{file_index}.csv"
    if not os.path.isfile(path):
        # no such file — skip to the next index
        print(f"[File {file_index}] not found. Skipping.")
        continue

    df = pd.read_csv(
        path,
        encoding="utf-8",
        converters={"Paragraphs": literal_eval}
    )

    if len(df) <= 10:
        print(f"[File {file_index}] Not enough articles to summarize (found {len(df)}). Skipping.")
        continue
    articles = Articles(df)
    clean_texts = articles.clean_articles()  # returns a list of cleaned article strings
    if len(clean_texts) <= 10:
        print(f"[File {file_index}] Not enough articles to summarize (found {len(clean_texts)}). Skipping.")
        continue
    #
    # 2) Split each article into sentences
    #
    all_sentences = []
    sentence_index = []  # parallel list of (article_id, sent_id)
    for art_id, full_text in enumerate(clean_texts):
        sents = sent_tokenize(full_text)
        for sent_id, sentence in enumerate(sents):
            all_sentences.append(sentence)
            sentence_index.append((art_id, sent_id))

    print(f"[File {file_index}] Total sentences across {len(clean_texts)} articles: {len(all_sentences)}")

    #
    # 3) Embed all sentences (normalized for cosine)
    #
    embeddings = sbert_model.encode(
        all_sentences,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True  # L2‐normalize so dot=cosine
    )
    # embeddings.shape == (N, D)

    #
    # 4) Cluster sentences with DBSCAN (cosine metric)
    #
    db = DBSCAN(
        eps=0.25,           # adjust this to tune how strict clusters are
        min_samples=2,     # at least 2 sentences needed to form a cluster
        metric='cosine',   # cosine distance = 1 - cosine similarity
        n_jobs=-1
    )
    cluster_labels = db.fit_predict(embeddings)
    # cluster_labels[i] is the cluster ID for sentence i, -1 = noise

    # Collect all non‐noise cluster labels
    unique_labels = sorted({lbl for lbl in cluster_labels if lbl >= 0})
    print(f"→ Found {len(unique_labels)} non-noise clusters.")

    #
    # 5) For each non-noise cluster, count distinct articles.
    #    If exactly 5 distinct articles appear, pick its representative sentence.
    #
    representative_sentences = []
    articles_per_cluster = {}  # cluster_label → number of distinct article_ids

    for lbl in unique_labels:
        # 5a) Get all sentence‐indices in this cluster
        cluster_indices = np.where(cluster_labels == lbl)[0]

        # 5b) Compute the set of distinct article IDs in this cluster
        article_ids = { sentence_index[i][0] for i in cluster_indices }
        count_distinct_articles = len(article_ids)
        articles_per_cluster[lbl] = count_distinct_articles

        # 5c) Only proceed if this cluster has exactly 5 distinct articles
        if count_distinct_articles >= 5:
            # 5d) Compute cluster centroid (mean of normalized embeddings) and renormalize
            cluster_embs = embeddings[cluster_indices]  # shape = (k, D)
            centroid = cluster_embs.mean(axis=0)
            centroid = centroid / norm(centroid)

            # 5e) Find the sentence whose embedding is closest to centroid
            sims = cluster_embs @ centroid
            best_local_idx = np.argmax(sims)           # index within cluster_indices
            best_global_idx = cluster_indices[best_local_idx]

            rep_sentence = all_sentences[best_global_idx]
            representative_sentences.append(rep_sentence)

            print(f"\nCluster {lbl} (Accepted):")
            print(f"  • Num articles in cluster: {count_distinct_articles}")
            print(f"  • Representative sentence: “{rep_sentence}”")
        else:
            # If cluster size ≠ 5, we simply skip including it in combined_summary
            print(f"\nCluster {lbl} (Skipped):")
            print(f"  • Num articles in cluster: {count_distinct_articles} (not greater than 4)")

    print(f"\n→ Collected {len(representative_sentences)} representative sentences from clusters of exactly 5 articles.\n")

    #
    # 6) Combine only those representative sentences into one “combined_summary”
    #
    combined_summary = " ".join(representative_sentences)

    #
    # 7) Send that combined_summary to GPT-4o-mini for title / summary / questions
    #
    client = OpenAI(api_key=API_KEY_OPEN_AI)

    def summarize_with_gpt(text):
        prompt = (
            "Summarize this passage in a paragraph or two. Only use information "
            "from the passage and make it well written. Also provide a title "
            "for the topic.\n\n"
            f"{text}\n\n"
            "Afterwards, provide three thoughtful questions about the topic that someone "
            "might ask another in a conversation about their thoughts on the topic. "
            "Order the response with the title first, then the summary, then the three "
            "questions."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()

    summary_output = summarize_with_gpt(combined_summary)

    #
    # 8) Parse GPT’s output: Title, Summary, Questions
    #
    lines = [line.strip() for line in summary_output.splitlines() if line.strip()]
    question_start = next((i for i, l in enumerate(lines) if l.startswith("1.")), None)

    if question_start is None or len(lines) < question_start + 3:
        print(f"[Warning] unexpected GPT format:\n{summary_output}\n")
        continue

    title_line   = lines[0]
    summary_body = " ".join(lines[1:question_start])
    q1 = lines[question_start].lstrip("1. ").strip()
    q2 = lines[question_start + 1].lstrip("2. ").strip()
    q3 = lines[question_start + 2].lstrip("3. ").strip()


    sum_ques["Topic"].append(df['Topic'][0])  # Use the first topic from the CSV for this summary
    sum_ques["Image"].append(df['Image'][0])  # Use the first image from the CSV for this topic
    sum_ques["Title"].append(title_line)
    sum_ques["Summary"].append(summary_body)
    sum_ques["Question 1"].append(q1)
    sum_ques["Question 2"].append(q2)
    sum_ques["Question 3"].append(q3)

    print(f"\n[{file_index + 1}/80] Summarization complete using {len(representative_sentences)} clusters of size 5.\n")

# After processing all files, save to CSV
sum_ques_df = pd.DataFrame(sum_ques)
sum_ques_df.to_csv('data/story_data.csv', index=False)
