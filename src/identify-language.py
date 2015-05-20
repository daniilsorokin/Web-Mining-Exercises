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

my_encoding = 'utf-8'
default_lang = 'en'
pattern_unigrams = "[^\W\d_]"
pattern_bigrams = "[^\W\d_]{2}"

def cosineOnDicts(a, b, base):
    amagn = 0.0
    bmagn = 0.0
    abproduct = 0.0
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


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', type=argparse.FileType('r', encoding=my_encoding),  
                        help = "Text documents to process. Should be in " + my_encoding)
    params = parser.parse_args()
    
    prototypes = {}
    
    for fname in os.listdir("langs/"):
        lang = fname.split(".")[0]
        lang_fdist = {}
        with codecs.open("langs/" + fname, "r", encoding=my_encoding) as f:
            lines = [line.strip() for line in list(islice(f, 101))]
        for line in lines:
            columns = line.split(",")
            lang_fdist[columns[0]] = float(columns[2])
        prototypes[lang] = lang_fdist;
    
    union = set()
    for v in prototypes.values():
        union.update(v)
    
    for f in params.files:
        txt = f.read().lower()
        f.close()

        # Extract ngrams
        unigrams = regexp_tokenize(txt, pattern_unigrams)
        bigrams = regexp_tokenize(txt, pattern_bigrams) 
        
        #Create frequency distributions    
        doc_fdist = FreqDist(unigrams + bigrams)
        predicted_lang = default_lang
        max_sim = -2
        for k,v in prototypes.items():
            sim = cosineOnDicts(v, doc_fdist, union)
            if sim > max_sim:
                max_sim = sim
                predicted_lang = k 
        
        filename = f.name.rsplit(os.sep, 2)[1] if os.sep in f.name else f.name
        print("{} | {} | ".format(filename, predicted_lang),)
