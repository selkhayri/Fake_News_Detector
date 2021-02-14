# -*- coding: utf-8 -*-
"""
Article Scraper 

This module uses an API call to retrieve a list of article snippets which 
contain links to the actual articles. It retrieves the links from the 
snippets, retrieves the linked articles, then proceeds to extract the article
text contents which it stores in a relational database for further processing.
 
"""

# Import the dependencies
import http.client, urllib.parse, urllib.request
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import sqlite3
import logging

# Import the config file
import scraping_config


# Class Scraper 
class Scraper:
    
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
    
        
    #========================================================================
    # This method retrieves tha articles from the apis that are identified
    # in the scraping_config configuration file. It stores the articles in
    # a text file also identified in the config file.
    #
    # Input:
    #   None
    #
    # Return:
    #   None
    def get_articles(self):
        
        # Get the apis from the config file
        apis = scraping_config.apis 
        
        # For each api ...
        for api in apis:
            
            # Issue the api call ...
            conn = http.client.HTTPConnection(api["url"])
            params = urllib.parse.urlencode(api["params"])
            conn.request('GET', api["uri"].format(params))
            
            # Retrieve the response ...
            res = conn.getresponse()
            data = res.read()
        
            # Save the response to the text file specified in the config file ...
            file = open(api["file"],"w")
            file.write(data.decode(api["encoding"]))
            file.close()
                
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
    # This method retrieves the article from the specified url. 
    # 
    # Input:
    #   url - The url of the article to be retrieved
    #
    # Return:
    #   text - the text of the article
    def get_article(self,url=None,source=None):
        
        # Create the request object to retrieve the article
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        # Retrieve the article webpage
        webpage = urlopen(req).read()
        
        # Create a BeautifulSoup object to parse the webpage
        soup = BeautifulSoup(webpage, 'html.parser')
        
        # Locate the article element
        # mydivs = soup.findAll("div", {"class": "caas-body"})
        article_element = scraping_config.article_text[source]["css"]["element"]
        article_class = scraping_config.article_text[source]["css"]["class"]
        elements = soup.findAll(article_element, {"class": article_class})
        
        # Retrieve the first element
        article = elements[0]
            
        # Get all the paragraph elements
        ps = article.findAll("p")
        
        # Iterate through all the paragraph elements and append then to the 
        # text of the article. 
        text = ""
        for p in ps:
            text = "\n".join([text,p.text])
        
        # Return the text of the article
        return text
        
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
        
        # Retrieve the list of supported sources (publications) from
        # the config file.
        sources = scraping_config.article_text.keys()
        
        # Retrieve the list of supported apis ...
        apis = scraping_config.apis
        
        # For each api ...
        for api in apis: 
            
            self.logger.debug("API: {}".format(api['name']))
            
            # Open the api text file for reading ...
            file = open(api['file'],"r")
            
            # Read in the contents of the api text file ...
            text = file.readlines()

            # For each item in the api text file ...
            for item in text:
                
                # Load the contents as JSON ...
                payload = json.loads(item)
                
                # If the language is specified for the api ...
                if "lang" in api.keys():
                    
                    # Filter the contents to only the articles that are in 
                    # the specified language
                    articles = self.language(payload[api["article-list"]], lang=api["lang"])
                else:
                    
                    # Otherwise, use the entire list of articles
                    articles = payload[api["article-list"]]
            
            
            self.logger.debug("Process articles")
            
            # For each article ...
            for article in articles:
                
                # Retrieve the url ...
                url = self.get_element(article=article,element="url")
                
                # Exception handling ...
                try:
                
                    # Iterate through the supported publications ...
                    for source in sources:
                        
                        # If the url is from the publication ...
                        if source in url:
                            
                            # Retrieve the title of the article
                            title = self.get_element(article,"title") 
                            
                            # Retrieve the article text
                            text = self.get_article(url,source)
                            
                            # Place the title and text into a tuple and 
                            # append the tuple to the article_list instance
                            # variable
                            self.article_list.append((
                                title,text
                            ))
                
                # Catch and log exceptions
                except Exception as e:
                    self.logger.error("Cound not retrieve article from {}.\n Error = {}".
                                    format(url, e))
                    
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
    def save_articles(self):
        
        self.logger.debug("Saving articles .....")
        
        try:
            
            # Get a database connection
            conn = self.get_db_connection()
            
            # Get a cursor from the connection
            cursor = conn.cursor()
            
            # Insert the contents of the article_list instance list variable
            # into the database table specified in the config file
            cursor.executemany("""
            INSERT INTO {} ('title', 'article')
            VALUES (?, ?)""".format(scraping_config.db_table), self.article_list)
            
            # Close the cursor
            cursor.close()
            
            # Commimt the transaction
            conn.commit()
        
        except Exception as e:
            self.logger.fatal(f"Error connecting to database: {e}")
    
if __name__ == "__main__":

    # Instantiate the Scraper class    
    scraper = Scraper()
    
    # Retrieve the articles
    scraper.get_articles()
    
    # Parse the articles and place them into the article_list instance variable
    scraper.parse_articles()
    
    # Save the articles to the database
    scraper.save_articles()
