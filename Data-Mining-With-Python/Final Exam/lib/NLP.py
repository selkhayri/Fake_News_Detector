#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 15:44:13 2021

@author: sami
"""

import re
from nltk.corpus import stopwords


def to_lower_case(df,column):
    
    lowercase = df[column].apply(lambda x: x.lower())
    
    return lowercase

def join_chars(text):
    
    if not isinstance(text,str):
        print("This")
    # print(f"type: {type(text)} \noffending text --> {text}")
    
    joined = "".join([char for char in text if char not in string.punctuation])
    return joined

def remove_punctuation(df,column):
    try:
        df["lc_rp"] = df[column].apply(lambda x: join_chars(x))
    except:
        print(f"Exception: {df}")
        
    return df

def remove_digits(df, column):
    digits = '0123456789'
    
    no_digits = df[column].apply(lambda l: "".join([x for x in l if str(x) not in digits]))
    
    return no_digits

# Insert a space after every period signifying the end of a sentence. Also insert a space between every comma.
def period_space(df, column):
    
    period_space = df[column].apply(lambda x: print(re.subn(r'(\s\w+[\.\,])(\w+\s)', '\\1 \\2', x, flags=re.IGNORECASE)))

    return period_space


# def lemmatize(df,column):
#    nlp = spacy.load('en')
#     lemmatized = df[column].apply(lambda l: " ".join(set([Word(x).lemmatize() for x in l.split()])))
#    lemmatized = df[column].apply(lambda x: " ".join(set([token.lemma_ for token in nlp(x)])))
    
#    return lemmatized


def stop_words():
    sw1 = stopwords.words("english")
    sw2 = open("nlp/stop_words_english.txt").read().splitlines()

    return set(sw1 + sw2)


def clean_articles(args):
    
    df, column = args[0:2]
    df["lowercase"] = df[column].apply(lambda x: x.lower())
    df.drop(columns=[column],inplace=True)
    # df = remove_punctuation(df,"_".join([column,"lowercase"])
    df["add_spaces"] = df["lowercase"].apply(lambda x: re.subn(r'(\s\w+[\.\,])(\w+\s)', '\\1 \\2', x, flags=re.IGNORECASE)[0])
    
    df.drop(columns=["lowercase"],inplace=True)
    df["no_digits"] = remove_digits(df,"add_spaces")

    df.drop(columns=["add_spaces"],inplace=True)
    df["text_no_sw"] = remove_stopwords(df,"no_digits")
    
    df.drop(columns=["no_digits"],inplace=True)
    
    df["lemmatized"] = lemmatize(df,"text_no_sw")
    df.drop(columns=["text_no_sw"],inplace=True)

    return df