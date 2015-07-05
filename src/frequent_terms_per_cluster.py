'''
Created on July 05, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import argparse, os, codecs
from vector_representation import StemmedCorpus, compute_base_terms, filter_base_terms

my_encoding = 'utf-8'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_folder', type=str, help = "Corpus input.")
    params = parser.parse_args()
    
    with codecs.open("cluster_most_frequent_terms.txt", "w", encoding=my_encoding) as out:
        for folder_name in os.listdir(params.input_folder):
            print("Cluster: " + folder_name)
            out.write("Cluster: " + folder_name + ": ")
            corpus = StemmedCorpus(language="english")
            corpus.load_from_folder(params.input_folder + folder_name + os.sep)
            corpus.preprocess_documents()
            base_terms = compute_base_terms(corpus._stemmed_documents)
            print("Base terms extracted: " + str(len(base_terms)))
            base_terms = filter_base_terms(base_terms, 10)
            for bt, idf, _ in base_terms: 
                out.write("{},".format(bt))
            out.write("\n")



