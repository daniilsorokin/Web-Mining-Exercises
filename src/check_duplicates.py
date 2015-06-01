'''
Created on May 19, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

from nltk.tokenize import regexp_tokenize
from os import listdir
from bs4 import BeautifulSoup
import codecs, sys, time
from mysouputils import get_content_from_soup

pattern_words = "[\w\-0-9']+"
my_encoding = "utf-8"

def are_duplicates(doc1, doc2):
    if len(doc1) > 50 and len(doc2) > 50 and  not are_duplicates(doc1[:50], doc2[:50]): 
        return False
    txt_tokens_1 = regexp_tokenize(doc1, pattern_words)
    txt_tokens_2 = regexp_tokenize(doc2, pattern_words)
    ngrams_1 = txt_tokens_1 + generate_ngrams(txt_tokens_1, 2)
    ngrams_2 = txt_tokens_2 + generate_ngrams(txt_tokens_2, 2)
    overlap = len([w for w in ngrams_1 if w in ngrams_2])
    score = (2*overlap)/(len(ngrams_1) + len(ngrams_1) + 1)
#     print(score)
    if score > 0.8: 
        return True
    else:
        return False    
    
def generate_ngrams(tokens, n):
    ngrams = []
    for i,token in enumerate(tokens):
        if i <= len(tokens) - n:
            ngram = ""
            for j in range(n):
                ngram += tokens[i+j] + " "
            ngrams.append(ngram)
    return ngrams 
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        start = time.perf_counter()
        mdir = sys.argv[1]
        file_names = listdir(mdir)
        files = []
        for filename in file_names:
            with codecs.open(mdir + filename, "r", encoding=my_encoding) as f: 
                files.append( (filename, get_content_from_soup(BeautifulSoup(f.read()))) )

        print( "No of files:" + str(len(files)) )
        while len(files):
            file = files.pop()
            if len(files) % 100 == 0: print(len(files))
            content = file[1]
            for another_file in files:
                another_content = another_file[1]
                if are_duplicates(content,another_content):
                    print("{},{}".format(file[0], another_file[0]))
        end = time.perf_counter()
        print("Elapsed time: " + str(end - start)) 
    