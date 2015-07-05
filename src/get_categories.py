'''
Created on July 05, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import argparse, re, codecs
from compose_corpus import DocumentCorpus

my_encoding = 'utf-8'

def categories_from_html_corpus(corpus):
    mapping = []
    for document in corpus._documents:
        doc_name = document[1]
        html = document[0]
        categories = set(re.findall("(title=\"Category:(.*?)\")", html))
        mapping.append((doc_name, [c[1] for c in categories]) )
    return mapping

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_folder', type=str, help = "Corpus input.")
    params = parser.parse_args()

    corpus = DocumentCorpus()
    corpus.load_from_folder(params.input_folder)
    mapping = categories_from_html_corpus(corpus)
    with codecs.open("categories_mapping.csv", "w", encoding=my_encoding) as out:
        for name, categories in mapping:
            out.write("{},{}\n".format(name, ",".join(categories)))
    
    

