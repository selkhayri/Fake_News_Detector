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

* **Detect_Fake_News.ipynb**: The jupyter notebook in which machine learning is performed
* **API Scraper/scraper.py** : The python file using API calls to retrieve articles from the news source.
* **API Scraper/mediastack.txt** : The file containing json data about the retrieved articles.
* **Classifier/classify.py** : The python file used to classify the articles.
* **data/news.sqlite** : The sqlite database used to store the articles as well as their classification.
* **data/1 and data/2** : Folders containing the labeled data used to train and test the machine learning mode.
* **logs/scraper.log** 
* **nlp/stop_words_english.txt** : The text file containing stop words on top of the ones identified by the spacy library.
* <b>*.pkl files</b> : The pickle files used to marshall and unmarshall python objects
* **requirements_jn.txt**: The libraries required for the execution of the **Detect_Fake_News.ipynb** jupyter notebook.
* **requirements_sc.txt**: The libraries required for the execution of the **scaper.py** and **classify.py** processes.

### Config 

#### scraping_config.py

This file contains the following items:

* **apis**: The apis to be scraped for news articles.
* **article_text**: The css elements to use for parsing the sraped articles.
* **project_path**: The path where the project is located.
* **db_table**: The name of the table in which to store the articles.
* **db_file**: The name of the sqlite file
* **db_retrieval_query**: The query for retrieving articles from the sqlite database.
* **db_update_query**: The query for update the article classification in the sqlite database.
* **log_name**: The name of the log file
* **model_pickle_file**: The name of the pickle file containing the machine learning model.
* **vectorizer_file**: The name of the pickle file containing the TFIDF_Vectorizer object
* **encoder_file**: The name of the pickle file containing the trained classification label encoder.


## Results

The logistic regression model that was derived from the training set was tested on the test set and the following was the confusion matrix:

<div align="center">
<table border="1">
<tr><td>6545</td><td>122</td></tr>
<tr><td>252</td><td>5890</td></tr>
</table>
</div>

As such, the following are the precision, recall, and F1 score values for the predictor:

**precision** = 5890 / (5890 + 122) =  96.3%
**recall** = 5890/ (5980 + 252) = 95.8%
**F1 Score** = 2 * precision * recall / (precision + recall) = 96/1%

## Observations

The precision and recall scores, while not terrible, could be further improved by using a bigger training sample and by trimming down the feature (vocabulary) set using the feature importance functionality of Random Forest Regression to reduce the processing overhead and to reduce the noise signal from loosely correlated features.