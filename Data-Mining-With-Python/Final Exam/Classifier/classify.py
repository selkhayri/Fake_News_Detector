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
import http.client, urllib.parse, urllib.request
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import sqlite3
import logging
import re
import string

# Import the config file
import scraping_config

from nltk.corpus import stopwords

import spacy


# Class Classifier 
class Classifier:
    
    #========================================================================
    # Class constructor
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
        
        self.nlp = spacy.load("en_core_web_sm")
    
        
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
    
    
    def to_lower(self,text):
        return "".join([x.lower() for x in text])
    
    def add_spaces(self, text):
        added_spaces = re.subn(r'(\s\w+[\.\,])(\w+\s)', '\\1 \\2', text, flags=re.IGNORECASE)[0]
        
        return added_spaces
    
    def remove_numbers(self, text):
        digits = '0123456789'
        
        no_digits = " ".join([w for w in text.split() if not w.isnumeric()])
        return no_digits
    
    def remove_punctuation(self, text):
        return "".join([char for char in text if char not in string.punctuation])
    
    def stop_words(self):
        sw1 = stopwords.words("english")
        sw2 = open("../nlp/stop_words_english.txt").read().splitlines()
        return set(sw1 + sw2)

    def remove_stopwords(self,text):
        text_no_sw = " ".join(word for word in text.split() if word not in self.stop_words())
    
        return text_no_sw
    
    def lemmatize(self,text):
        # nlp = spacy.load('en')
        #     lemmatized = df[column].apply(lambda l: " ".join(set([Word(x).lemmatize() for x in l.split()])))
        lemmatized = " ".join(set([token.lemma_ for token in self.nlp(text)]))
    
        return lemmatized
    
    def clean_articles(self):
        for i,article in enumerate(self.article_list):
            text = article['text']
            text = self.to_lower(text)
            text = self.add_spaces(text)
            
            text = self.remove_numbers(text)
            text = self.remove_punctuation(text)
            text = self.remove_stopwords(text)
            text = self.lemmatize(text)
            
            print(text)
    
    
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
    def parse_articles(self):
        
        # Initialize the article_list instance list variable
        self.article_list = []
        
        self.logger.debug("Process articles")
        
        # For each article ...
        for article in self.raw_article_list:
            self.article_list.append(
                {
                    "title": article[0],
                    "text": article[1]
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
    def get_db_connection(self):
        return sqlite3.connect(scraping_config.db_file)
    
    #========================================================================
    # This method saves the contents of the article_list instance list
    # variable and inserts them into the sqlite database.
    #
    # Input:
    #   None
    #
    # Return:
    #   None
    def get_articles(self):
        
        self.logger.debug("Saving articles .....")
        
        try:
            
            # Get a database connection
            conn = self.get_db_connection()
            
            # Get a cursor from the connection
            cursor = conn.cursor()
            
            # Insert the contents of the article_list instance list variable
            # into the database table specified in the config file
            args = scraping_config.db_query
            sql = "SELECT {} FROM {} {}".format(args[0],args[1],args[2])
            
            cursor.execute(sql)
            
            self.raw_article_list = cursor.fetchall()
            
            # Close the cursor
            cursor.close()
            
            # Commimt the transaction
            conn.commit()
                        
        except Exception as e:
            self.logger.fatal(f"Error retrieving articles from database: {e}")
 
    
    def process(self):
         # Retrieve the articles
        self.get_articles()
        
        # Parse the articles and place them into the article_list instance variable
        self.parse_articles()
        
        self.clean_articles()
        
        # Save the articles to the database
        # scraper.save_articles()
         
if __name__ == "__main__":

    # Instantiate the Scraper class    
    classifier = Classifier()
    
    # Process articles
    classifier.process()
    # print(classifier.remove_digits("how to watch election night 2020"))
    
    
