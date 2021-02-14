# -*- coding: utf-8 -*-

# =============================================================================
# Article Classifier 
# 
# This module uses an API call to retrieve a list of article snippets which 
# contain links to the actual articles. It retrieves the links from the 
# snippets, retrieves the linked articles, then proceeds to extract the article
# text contents which it stores in a relational database for further processing.
#  
# =============================================================================


# Import the dependencies
import sqlite3
import logging
import re
import string
import pandas as pd
from nltk.corpus import stopwords

import spacy
import pickle

# Import the config file
import scraping_config


# Class Classifier 
class Classifier:
    
    #========================================================================
    # Class constructor
    #========================================================================
    def __init__(self):
        # Initialize logging    
        self.logger = logging.getLogger(scraping_config.log_file)
        self.logger.setLevel(logging.DEBUG)
        
        # create file handler which logs even debug messages
        fh = logging.FileHandler(scraping_config.log_file)
        fh.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        # add the handlers to logger
        self.logger.addHandler(fh)
        
        # Initialize spacy nlp library 
        self.nlp = spacy.load("en_core_web_sm")
        
        # Load the DL model that was created from the training that was
        # carried out in the Jupyter Notebook
        with open(scraping_config.model_pickle_file,"rb") as f:
            self.dl_model = pickle.load(f)
        
        # Load the vectorizer object that was created from the training that was
        # carried out in the Jupyter Notebook        
        with open(scraping_config.vectorizer_file,"rb") as f:
            self.vect = pickle.load(f)
        
        # Load the label encoder that was created from the training that was
        # carried out in the Jupyter Notebook    
        with open(scraping_config.encoder_file,"rb") as f:
            self.enc = pickle.load(f)    
    
    
    #========================================================================
    # This method filters out the articles from the retrieved 
    # article snippets that are not in the specified language, lang.
    #
    # Input:
    #   ls - the list of article snippets
    #   lang - the language to which articles are to be limited
    #
    # Return:
    #   ls - filtered list of article snippers
    #========================================================================
    def language(self,ls,lang=''):
        for i,article in enumerate(ls):
            if article['language'] != lang:
               ls.pop(i)
        
        return ls
        
           
    #========================================================================
    # This method returns the specified JSON element of the article in question. 
    # It recursively traverses the JSON structure until it finds the sought 
    # JSON item.
    #
    # Input:
    #   article - the article snippet from which the JSON element is sought
    #   element - the JSON element that is sought
    #
    # Return:
    #   the sought element
    #========================================================================
    def get_element(self,article,element):
        # Retrieve the keys from article
        keys = article.keys()
        
        # If the sought element is found ...
        if element in keys:
            
            # Return the element
            return article[element]
        else:
            
            # recursively traverse the tree structure to find the sought key
            for key in keys:
                return self.get_element(article[key],element)
    
    
    # =======================================================================
    # This method transforms a given passage of text to lower case
    #
    # Input:
    #     text - the text to be transformed to lower case
    # Return:
    #     the text in lower case
    # =======================================================================
    def to_lower(self,text):
        return "".join([x.lower() for x in text])
    
    
    # ========================================================================
    # This method places a space between periods at the end of a sentence and
    # the beginning of the following sentence.
    #
    # Input:
    #     text - the text to be transformed
    # Return:
    #     the text with spaces placed after period characters
    # ========================================================================
    def add_spaces(self, text):
        return re.subn(r'(\s\w+[\.\,])(\w+\s)', '\\1 \\2', text, flags=re.IGNORECASE)[0]
 
       
    # ========================================================================
    # This method removes all the numeric strings
    #
    # Input: 
    #     text - the text from which the numeric strings are going to be removed
    # Return:
    #     the text with numeric strings removed
    # ========================================================================
    def remove_numbers(self, text):
        return " ".join([w for w in text.split() if not w.isnumeric()])

    
    # =========================================================================
    # This method removes the punctuation characters from the text
    #
    # Input:
    #     text - the text from which punctuation is to be removed
    # Return:
    #     the text with the punctuation removed    
    # ========================================================================
    def remove_punctuation(self, text):
        return "".join([char for char in text if char not in string.punctuation])

    
    # ========================================================================
    # This method returns a list of customized stopwords from the text
    #
    # Input:
    #     None
    # Return:
    #     the list of stopwords
    # ========================================================================
    def stop_words(self):
        sw1 = stopwords.words("english")
        sw2 = open("../nlp/stop_words_english.txt").read().splitlines()
        return set(sw1 + sw2)


    # ========================================================================
    # This method removes the stopwords from the text
    # Input:
    #     text - the text from which stopwords are to be removed
    # Return:
    #     the text with the stopwords removed
    # ========================================================================
    def remove_stopwords(self,text):
        return " ".join(word for word in text.split() if word not in self.stop_words())
    
    
    # ========================================================================
    # This method removes the stopwords from the text
    #
    # Input:
    #     text - the text from which stopwords are to be removed
    # Return:
    #     the text with the stopwords removed
    # ========================================================================    
    def lemmatize(self,text):
        return " ".join(set([token.lemma_ for token in self.nlp(text)]))

    
    # ========================================================================
    # This method cleans the articles text by calling the above cleaning 
    # methods.
    #
    # Input:
    #     None
    # Return:
    #     None
    # ========================================================================  
    def clean_articles(self):
             
        self.df = pd.DataFrame(self.article_list)
        
        self.df["text"] = self.df["text"].apply(lambda x: self.to_lower(x))
        self.df["text"] = self.df["text"].apply(lambda x: self.add_spaces(x))
        
        self.df["text"] = self.df["text"].apply(lambda x: self.remove_numbers(x))
        self.df["text"] = self.df["text"].apply(lambda x: self.remove_punctuation(x))
        self.df["text"] = self.df["text"].apply(lambda x: self.remove_stopwords(x))
        self.df["text"] = self.df["text"].apply(lambda x: self.lemmatize(x))
        
 
    # ========================================================================
    # This method predicts whether the articles are likely true or likely false
    # and updates the TrueOrFalse column of the dataframe.
    # 
    # Input:
    #     None
    # Return:
    #     None
    # ========================================================================        
    def make_predictions(self):
        X = self.vect.transform(self.df["text"])
        
        true_or_false = self.enc.inverse_transform(self.dl_model.predict(X))
        self.df["TrueOrFalse"] = ["Likely True" if x == "REAL" \
                                  else "Likely False" for x in true_or_false]
        
        # self.logger.debug("self.df['TrueOrFalse'] = {}".format(self.df["TrueOrFalse"]))
        
    #========================================================================
    # This method retrieves the article snippets from the api-specific
    # text files, filters them to only those in a specific language. For each 
    # of the remaining article snippets, it retrieves the title and the 
    # contents, places them into a tuple, and appends the tuple to the 
    # article_list instance list variable.
    #
    # Input:
    #   None
    #
    # Return:
    #   None
    #========================================================================
    def parse_articles(self):
        
        # Initialize the article_list instance list variable
        self.article_list = []
        
        self.logger.debug("Process articles")
        
        # For each article ...
        for article in self.raw_article_list:
            self.article_list.append(
                {
                    "pk": article[0],
                    "title": article[1],
                    "text": article[2]
                }
            )


    #========================================================================
    # This method returns the connection to the sqlite database
    #
    # Input:
    #   None
    #
    # Return:
    #   None
    #========================================================================
    def get_db_connection(self):
        return sqlite3.connect(scraping_config.db_file)


    #========================================================================
    # This method retrieves the articles from the sqlite database.
    #
    # Input:
    #   None
    #
    # Return:
    #   None
    #========================================================================
    def get_articles(self):
        
        self.logger.debug("Retrieving articles .....")
        
        try:
            
            self.logger.debug("DB Connection")
            # Get a database connection
            conn = self.get_db_connection()
            
            self.logger.debug("DB Cursor")
            # Get a cursor from the connection
            cursor = conn.cursor()
            
            self.logger.debug("SQL")
            # Insert the contents of the article_list instance list variable
            # into the database table specified in the config file
            sql = scraping_config.db_retrieval_query
            
            self.logger.debug(sql)
            cursor.execute(sql)
            
            self.logger.debug("fetchall")
            self.raw_article_list = cursor.fetchall()
            
            self.logger.debug(f"raw_article_list: {len(self.raw_article_list)}")
            # Close the cursor
            cursor.close()
            
            # Commit the transaction
            conn.commit()
            
            self.logger.debug("Retrieved articles ...")
            
            conn.close()
                        
        except Exception as e:
            self.logger.fatal(f"Error retrieving articles from database: {e}")
 
    
    #========================================================================
    # This method updates the "TrueOrFalse" column of the sqlite database with 
    # "likely true" or "likely false."
    #
    # Input:
    #   None
    #
    # Return:
    #   None
    #======================================================================== 
    def update_record(self,x):
        self.logger.debug("Updating DB record ... {}".format(x["pk"]))
        # self.logger.debug("x[\"TrueOrFalse\"] = {}".format(x['TrueOrFalse']))
        
        try:
            self.logger.debug("Getting db connection ...")
            
            # Get a database connection
            conn = self.get_db_connection()
            
            # Get a cursor from the connection
            cursor = conn.cursor()
            
            
            # Update the contents of the article_list instance list variable
            # into the database table specified in the config file           
            sql = scraping_config.db_update_query.format(x["TrueOrFalse"],x["pk"])
            
            self.logger.debug(sql)
            
            cursor.execute(sql)
            
            # Close the cursor
            cursor.close()
            
            # Commit the transaction
            conn.commit()
            
            conn.close()
            
            self.logger.debug("Updated db record ...")
                        
        except Exception as e:
            self.logger.fatal(f"Error updating record database: {e}")


    #========================================================================
    # This method invokes the update_record method for each record of the
    # articles dataframe.
    #
    # Input:
    #   None
    #
    # Return:
    #   None
    #========================================================================
    def update_articles(self):
       
        self.logger.debug("Saving articles ...")
        self.df.apply(lambda x: self.update_record(x), axis=1)


    #========================================================================
    # This method updates the "fake" column of the sqlite database with 
    # "likely true" or "likely false."
    #
    # Input:
    #   None
    #
    # Return:
    #   None
    #========================================================================    
    def process(self):
         # Retrieve the articles
        self.get_articles()
        
        # Parse the articles and place them into the article_list instance variable
        self.parse_articles()
        
        # Clean the text of the articles
        self.clean_articles()
        
        # Predict which articles are likely true and which are likely false
        self.make_predictions()
        
        # Populate the TrueOrFalse column in the database with the predictions
        self.update_articles()
         
if __name__ == "__main__":

    # Instantiate the Scraper class    
    classifier = Classifier()
    
    # Process articles
    classifier.process()
    
    
