import pandas as pd
from ast import literal_eval
import spacy
import classy_classification



class Articles:

    def __init__(self, df, threshold=0.95, trash_file='texts/trash.txt'):
        self.df = df
        self.threshold = threshold
        self.trash_df = {
            "not_trash": self.df.iloc[:, 0].dropna().tolist(),
        }

        try:
            with open(trash_file, "r") as f:
                trash = f.read().splitlines()
                self.trash_df["trash"] = trash
        except FileNotFoundError:
            print(f"Error: The file '{trash_file}' was not found.")
            self.trash_df["trash"] = []

        self.nlp = spacy.blank("en")
        self.nlp.add_pipe(
            "classy_classification",
            config={
                "data": self.trash_df,
                "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                "device": "cuda"
            }
        )

    def remove_empty_strings(self, lst):
        return [item for item in lst if (item.strip() != '')]

    def remove_trash(self, article):
        clean = []

        for doc in self.nlp.pipe(article, batch_size=128):
            if doc._.cats["trash"] <= self.threshold:
                clean.append(doc.text)
        return clean

    def clean_articles(self):
        self.df['Paragraphs'] = self.df['Paragraphs'].apply(lambda x: self.remove_empty_strings(x))
        self.df = self.df.drop(self.df[self.df['Paragraphs'].apply(len) == 0].index)
        self.df = self.df.reset_index(drop=True)

        self.df['Paragraphs'] = self.df['Paragraphs'].apply(self.remove_trash)

        self.df['Paragraphs'] = self.df['Paragraphs'].apply(lambda x: " ".join(x))

        article_list = []
        for i in range(len(self.df)):
            article_list.append(self.df.loc[i][2])

        article_list_unique = list(set(article_list))

        return article_list_unique

