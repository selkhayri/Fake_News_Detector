# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import http.client, urllib.parse, urllib.request
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import scraping_config

# class scraper
def get_articles():
    apis = scraping_config.apis
    
    for api in apis:
        print(api["url"])
        conn = http.client.HTTPConnection(api["url"])
        params = urllib.parse.urlencode(api["params"])
        conn.request('GET', api["uri"].format(params))
        
        res = conn.getresponse()
        data = res.read()
    
        file = open(api["file"],"w")
        file.write(data.decode(scraping_config.mediastack_encoding))
        file.close()
            

def language(ls,lang=''):
    for i,article in enumerate(ls):
        if article['language'] != 'en':
           ls.pop(i)
    
    return ls
    

def get_article(article=None):
    
    # url = "https://www.politico.eu/article/charles-michel-coronavirus-vaccinating-70-percent-by-summer-will-be-difficult/"

    url = article["url"]
    
    print(url)
    
    return None

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    webpage = urlopen(req).read()
    
    soup = BeautifulSoup(webpage, 'html.parser')
    # print(soup.prettify())
    
    # bs = BeautifulSoup(url)
    # div = soup[".article-meta__title"]
    mydivs = soup.findAll("div", {"class": "article__content"})
    article = mydivs[0]
    
    article_text = article.findAll("div",{"class": "article__content"})
    
    ps = article_text[0].findAll("p")
    
    for p in ps:
        print(p.text)
    
    """
    for div in divs:
        if div["class"] == "article__content":
            print(div)
    """
def parse_articles():
    sources = scraping_config.article_text.keys()
    
    apis = scraping_config.apis
    
    for api in apis: 
        print("\n\n\n\n\n")
        print(api["file"])
        print(" ========================================================>>>")
        file = open(api['file'],"r")
        text = file.readlines()
    
        for item in text:
            payload = json.loads(item)
            
            
            if "lang" in api.keys():
                # print(api["article-list"])
                articles = language(payload[api["article-list"]], lang=api["lang"])
            else:
                articles = payload[api["article-list"]]
        
        # print(articles)
        
        for article in articles:
            print("A R T I C L E ===================> ")
            print(article)
            for source in sources:
                if source in article["url"]:
                    print("found")
                    get_article(article)
            
if __name__ == "__main__":
    # get_articles()
    parse_articles()
   #  get_article()
   
