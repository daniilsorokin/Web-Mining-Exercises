'''
Created on May 19, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

import os
import codecs
import math
import argparse
from nltk.probability import FreqDist
from nltk.tokenize import regexp_tokenize
from itertools import islice

from check_duplicates import get_content

my_encoding = 'utf-8'
pattern_unigrams = "[^\W\d_]"
pattern_bigrams = "[^\W\d_]{2}"
min_freq = 0.0001

def cosineOnDicts(a, b, base):
    amagn = min_freq
    bmagn = min_freq
    abproduct = min_freq
    for el in base:
        v_a = a[el] if el in a else 0.0
        v_b = b[el] if el in b else 0.0
        amagn += v_a * v_a;
        bmagn += v_b * v_b;
        abproduct += v_a * v_b;
    amagn = math.sqrt(amagn);
    bmagn = math.sqrt(bmagn);
    cosine = abproduct / (amagn * bmagn);
    return cosine;

class LangIdentifier:
    def __init__(self, langs_dir):
        self._prototypes = {}
        
        for fname in os.listdir(langs_dir):
            lang = fname.split(".")[0]
            lang_fdist = {}
            with codecs.open(langs_dir + fname, "r", encoding=my_encoding) as f:
                lines = [line.strip() for line in list(islice(f, 101))]
            for line in lines:
                columns = line.split(",")
                lang_fdist[columns[0]] = float(columns[2])
            self._prototypes[lang] = lang_fdist;
        
        self._union = set()
        for v in self._prototypes.values():
            self._union.update(v)

    def identify_language(self, document, default_lang = None):
        # Extract ngrams
        unigrams = regexp_tokenize(document, pattern_unigrams)
        bigrams = regexp_tokenize(document, pattern_bigrams) 
        
        #Create frequency distributions    
        doc_fdist = FreqDist(unigrams + bigrams)
        predicted_lang = default_lang
        max_sim = 0.5
        for k,v in self._prototypes.items():
            sim = cosineOnDicts(v, doc_fdist, self._union)
            if sim > max_sim:
                max_sim = sim
                predicted_lang = k
                 
        return predicted_lang
    
    def get_score(self, document, lang):
        # Extract ngrams
        unigrams = regexp_tokenize(document, pattern_unigrams)
        bigrams = regexp_tokenize(document, pattern_bigrams) 
        #Create frequency distributions    
        doc_fdist = FreqDist(unigrams + bigrams)
        sim = cosineOnDicts(self._prototypes[lang], doc_fdist, self._union)
        return sim
       
if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', action='store_true')
    parser.add_argument('files', nargs='+', type=argparse.FileType('r', encoding=my_encoding),  
                        help = "Text documents to process. Should be in " + my_encoding)
    params = parser.parse_args()
    identifier = LangIdentifier("langs/")

    for f in params.files:
        txt = f.read().lower()
        if params.w:
            txt = get_content(txt)

        predicted_lang = identifier.identify_language(txt)
        filename = f.name.rsplit(os.sep, 2)[1] if os.sep in f.name else f.name
        print("{} | {} | ".format(filename, predicted_lang))
