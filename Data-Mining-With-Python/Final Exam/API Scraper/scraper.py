# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# Import the dependencies
import http.client, urllib.parse, urllib.request
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import sqlite3

import scraping_config

class Scraper:
    
    def get_articles(self):
        apis = scraping_config.apis
        
        for api in apis:

            conn = http.client.HTTPConnection(api["url"])
            params = urllib.parse.urlencode(api["params"])
            conn.request('GET', api["uri"].format(params))
            
            res = conn.getresponse()
            data = res.read()
        
            file = open(api["file"],"w")
            file.write(data.decode(api["encoding"]))
            file.close()
                
    
    def language(self,ls,lang=''):
        for i,article in enumerate(ls):
            if article['language'] != 'en':
               ls.pop(i)
        
        return ls
        
    
    def get_article(self,url=None):
        
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        webpage = urlopen(req).read()
        
        soup = BeautifulSoup(webpage, 'html.parser')
        
        mydivs = soup.findAll("div", {"class": "caas-body"})
        article = mydivs[0]
            
        ps = article.findAll("p")
        
        text = ""
        for p in ps:
            #print(p.text)
            text = "\n".join([text,p.text])
            
        return text
        
     
    def get_element(self,article,element):
        keys = article.keys()
        if "url" in keys:
            return article[element]
        else:
            for key in keys:
                return self.get_element(article[key],element)
    
    
    def parse_articles(self):
        self.article_list = []
        
        sources = scraping_config.article_text.keys()
        
        apis = scraping_config.apis
        
        for api in apis: 
            
            file = open(api['file'],"r")
            text = file.readlines()
        
            for item in text:
                payload = json.loads(item)
                
                
                if "lang" in api.keys():
                    # print(api["article-list"])
                    articles = self.language(payload[api["article-list"]], lang=api["lang"])
                else:
                    articles = payload[api["article-list"]]
            
            
            for article in articles:
                
                    url = self.get_element(article=article,element="url")
                    
                    try:
                    
                        for source in sources:
                            
                            if source in url:
                                
                                title = self.get_element(article,"title") 
                                # print(title)
                                
                                # print(title)
                                text = self.get_article(url)
                                
                                self.article_list.append((
                                    title,text
                                ))
                                
                    except Exception as e:
                        print(e)
                        ## Log error to file
                        
    def get_db_connection(self):
        return sqlite3.connect(scraping_config.db_file)
    
    
    def save_articles(self):
        
        print("Saving articles .....")
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.executemany("""
        INSERT INTO {} ('title', 'article')
        VALUES (?, ?)""".format(scraping_config.db_table), self.article_list)
        
        cursor.close()
        conn.commit()
             
    
if __name__ == "__main__":
    
    scraper = Scraper()
    # scraper.get_articles()
    scraper.parse_articles()
    scraper.save_articles()
