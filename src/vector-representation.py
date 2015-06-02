'''
Created on Jun 2, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import codecs
from nltk.probability import FreqDist
from nltk.tokenize import regexp_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer


pattern_words = "[\w\-0-9']+"
language = "german"
my_encoding = 'utf-8'

with codecs.open("stopwords/" + language, "r", encoding=myencoding) as f:
    stopwords = [sw.strip() for sw in f.readlines()]
    
stemmer = SnowballStemmer(language)

def tokenize_document(document):
    return regexp_tokenize(document, pattern_words)

def remove_stopword(tokens):
    return [token for token in tokens if token not in stopwords]

def stemm_tokens(tokens):
    return [stemmer.stem(token) for token in tokens]

if __name__ == '__main__':
    pass