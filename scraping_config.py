#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the config file for the web-scraping-classification project
"""
apis = [{ 
                'name': 'mediastack',
                'url': 'api.mediastack.com',
                'uri': '/v1/news?{}',
                'file': "mediastack.txt",
                'encoding': "utf-8",
                'params': {
                    'access_key': '<-- SNIP -->',
                    'categories': '-general',
                    'sort': 'published_desc',
                    'limit': 100,
                    'sources': "yahoo"
                },
                'article-list': "data",
                'article-title': "title",
                'article-url': "url",
                'lang': 'en'
                
        }]

article_text = {
        "yahoo.com": {
            "css" : {
                "element": "div",
                "class": "caas-body"
                }
            }   
    }

project_path = "<-- SNIP -->"

db_table = "news_articles"
db_file = "".join([project_path,"/data/news.sqlite"])
db_retrieval_query = "SELECT pk, title, article FROM news_articles "\
                        "WHERE TrueOrFalse IS NULL"
db_update_query = "UPDATE news_articles "\
                    "SET TrueOrFalse='{}' WHERE pk={}"

log_name = "Scraping Logger"
log_file = "".join([project_path,"/logs/scraping.log"])

model_pickle_file = "".join([project_path,"/logistic_reg_model.pkl"])
vectorizer_file = "".join([project_path,"/tfidf_vectorizer.pkl"])
encoder_file = "".join([project_path,"/label_encoder.pkl"])
