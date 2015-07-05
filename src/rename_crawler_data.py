'''
Created on July 05, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import argparse
from urllib.parse import unquote
from compose_corpus import DocumentCorpus


def rename_corpus_with_map(corpus, mapping):
    for i, document in enumerate(corpus._documents):
        index = document[1].rsplit("_",2)[-1]
        corpus._documents[i] = (document[0], mapping[index])

my_encoding = 'utf-8'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',type=str, help = "Remove the given prefix from every url.",
                        default=None)  
    parser.add_argument('visited_links', type=argparse.FileType('r', encoding=my_encoding), help = "File containing a list of visited links.")
    parser.add_argument('input_folder', type=str, help = "Corpus input.")
    parser.add_argument('output_folder', type=str, help = "Save to.")
    params = parser.parse_args()


    visited_urls_map = {line.strip().split(",")[0] : unquote(line.strip().split(",")[1]) for line in params.visited_links}
    if params.p: visited_urls_map = {k : v.replace(params.p, "") for k,v in visited_urls_map.items()}
    
    corpus = DocumentCorpus()
    corpus.load_from_folder(params.input_folder)
    rename_corpus_with_map(corpus, visited_urls_map)
#     corpus.print_stat()
    corpus.save_to_folder(params.output_folder)
