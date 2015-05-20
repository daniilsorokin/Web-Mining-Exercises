'''
Created on 01.05.2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

import codecs
import sys
import re
import os
import argparse
import nltk
from nltk.probability import FreqDist
from nltk.tokenize import regexp_tokenize
from nltk.corpus import stopwords
from email.policy import default

my_encoding = 'utf-8'

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-n',type=int, help = "Number of most common word to compare between documents", default=30)
    parser.add_argument('-m',type=int, help = "Number of most letters and letter pairs to compare between documents", default=30)
    parser.add_argument('-s',type=argparse.FileType('r', encoding=my_encoding), 
                        help = "Use the given list of stop words. Should be in " + my_encoding)
    parser.add_argument('files', nargs='+', type=argparse.FileType('r', encoding=my_encoding),  
                        help = "Text documents to process. Should be in " + my_encoding)
    params = parser.parse_args()
    
    # Patterns for splitting text into words and ngrams
    pattern_words = "[\w\-0-9']+"
    pattern_unigrams = "[^\W\d_]"
    pattern_bigrams = "[^\W\d_]{2}"
    
    # Store most common words and ngrams for latter comparison of texts
    words_most_common = []
    ngrams_most_common = []
    
    # Load stopwords if necessary
    if params.s:
        stopwords = [sw.strip() for sw in params.s.readlines()]
        params.s.close()
    
    #Process documents    
    for f in params.files:
        txt = f.read().lower()
        f.close()
        
        # Tokenize
#         txt_tokens = regexp_tokenize(txt, pattern_words)
#         if params.s:
#             txt_tokens = [token for token in txt_tokens if token not in stopwords]                 
        
        # Extract ngrams
        unigrams = regexp_tokenize(txt, pattern_unigrams)
        bigrams = regexp_tokenize(txt, pattern_bigrams) 
        
        #Create frequency distributions    
#         fdist_words = FreqDist(txt_tokens)
        fdist_ngrams = FreqDist(unigrams + bigrams)
        
        # Store most common words and ngrams for latter comparison of texts
#         words_most_common.append([k for (k,_) in fdist_words.most_common(params.n)])
        ngrams_most_common.append([k for (k,_) in fdist_ngrams.most_common(params.m)])
        outputname = "output_for_" + f.name.rsplit(os.sep, 2)[1]
        
        # Write out the distribution of words in the document
#         with codecs.open("output/words_" + outputname, "w", encoding=my_encoding) as out:
#             for k,v in fdist_words.most_common():
#                 prozent = fdist_words.freq(k)
#                 out.write("{},{},{}\n".format(k,v, prozent))
        # Write out the distribution of ngrams in the document
        with codecs.open("output/letters_" + outputname, "w", encoding=my_encoding) as out:
            for k,v in fdist_ngrams.most_common():
                prozent = v / (len(unigrams) if len(k) == 1 else len(bigrams))
                out.write("{},{},{}\n".format(k,v, prozent))  
        # Write the size of bins of words that appear with the same frequency               
#         with codecs.open("bins/" + outputname, "w", encoding=my_encoding) as out:
#             for i in sorted(set(fdist_words.values())):
#                 bin_size = fdist_words.Nr(i)
#                 out.write("{},{}\n".format(i,bin_size))     
    print('Output distributions saved in \'output\' folder.')
    print('Output bins saved in \'bins\' folder.')
    # If there are many documents -> compare their most common words and ngrams
    if len(params.files) > 1:
        print("Pairwise overlap between {} most frequent words:".format(params.n))
        short_names = [f.name[-15:] for f in params.files]
        for i, list1 in enumerate(words_most_common):
            for j, list2 in enumerate(words_most_common[i+1:]):
                print("{} | {} | ".format(short_names[i], short_names[i+j+1]), end="")
                overlap = len([w for w in list1 if w in list2])
                print(overlap)
        print("Pairwise overlap between {} most frequent letters and letter pairs:".format(params.m))
        short_names = [f.name[-15:] for f in params.files]
        for i, list1 in enumerate(ngrams_most_common):
            for j, list2 in enumerate(ngrams_most_common[i+1:]):
                print("{} | {} | ".format(short_names[i], short_names[i+j+1]), end="")
                overlap = len([w for w in list1 if w in list2])
                print(overlap)
            
                 
    