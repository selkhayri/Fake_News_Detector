# Fake News Detector

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

Using an API call, news articles were retrieved from mediastack.com and stored in an sqlite database for later processing by the classification process.

### Classification

The classifier module accomplished its task as follows:

* Load the unclassified articles from the database
* Clean up the text of the articles
* Load the pickled objects from file
* Predict the classification of the articles

### Folders and files

* **API Scraper/scraper.py** : The python file using API calls to retrieve articles from the news source.
* **API Scraper/mediastack.txt** : The file containing json data about the retrieved articles.
* **Classifier/classify.py** : The python file used to classify the articles.
* **data/news.sqlite** : The sqlite database used to store the articles as well as their classification.
* **data/1 and data/2** : Folders containing the labeled data used to train and test the machine learning mode.
* **logs/scraper.log** 
* **nlp/stop_words_english.txt** : The text file containing stop words on top of the ones identified by the spacy library.
* <b>*.pkl files</b> : The pickle files used to marshall and unmarshall python objects

### Config 

#### scraping_config.py

This file contains the following items:

* **apis**: The apis to be scraped for news articles
* **article_text**: The css elements to use for parsing the sraped articles
* **project_path**: The path where the project is located
* **db_table**: The name of the table in which to store the articles
* **db_file**: The name of the sqlite file
* **db_retrieval_query**: The query for retrieving articles from the sqlite database
* **db_update_query**: The query for update the article classification in the sqlite database
* **log_name**: The name of the log file
* **model_pickle_file**: The name of the pickle file containing the machine learning model
* **vectorizer_file**: The name of the pickle file containing the TFIDF_Vectorizer object
* **encoder_file**: The name of the pickle file containing the trained classification label encoder

