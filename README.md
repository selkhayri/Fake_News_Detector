# Pirple

## Purpose

The goal of this project is the creation of a system to detect and identify news articles that are fake.

## Process

The process by which fake news articles were identified is the following:

### Supervised Machine Learning

Labeled news articles were retrieved from Kaggle and used to train a logistic regression model. During the training, it was verified that the numbers of real news articles and fake news articles were reasonably similar. If that had not been the case, an oversampling strategy would have been implemented. 

To facilitate the classification process, the following objects were pickled for future use:

* The logistic regression model
* The label encoder
* The tfidf vectorizer

###  Scraping news sites

News articles were retrieved from mediastack.com and stored in an sqlite database for later processing by the classification process.

### Classification

The classifier module accomplished its task as follows:

* Load the unclassified articles from the database
* Clean up the text of the articles
* Load the pickled objects from file
* Predict the classification of the articles

### Folders and files

* API Scraper/scraper.py: The python file used to retrieve articles from the news source.
* API Scraper/mediastack.txt: The file containin json data about the retrieved articles.
* Classifier/classify.py: The python file used to classify the articles.
* data/news.sqlite: The sqlite database used to store the articles as well as their classification.
* data/1 and data/2: Folders containing the labeled data used to train and test the machine learning mode.
* logs/scraper.log
* nlp/stop_words_english.txt: The text file containing stop words on top of the ones identified by the spacy library.
* *.pkl files: The pickle files used to marshall and unmarshall python objects


