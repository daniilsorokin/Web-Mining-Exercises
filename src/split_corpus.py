'''
Created on Jun 3, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

import argparse, os
from compose_corpus import DocumentCorpus

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r',type=float, help = "Test to whole size ratio.", default=0.5)
    parser.add_argument('input_folder', type=str, help = "Corpus input.")
    parser.add_argument('output_folder', type=str, help = "Save to.")
    
    params = parser.parse_args()

    corpus = DocumentCorpus()
    corpus.load_from_folder(params.input_folder)
    corpus.print_stat()
    corpus_test, corpus_train = corpus.split_train_test(params.r)
    print("Train corpus:")
    corpus_train.print_stat()
    if not os.path.exists(params.output_folder + "train/"): os.makedirs(params.output_folder + "train/")
    corpus_train.save_to_folder(params.output_folder + "train/")
    print("Test corpus:")
    corpus_test.print_stat()
    if not os.path.exists(params.output_folder + "test/"): os.makedirs(params.output_folder + "test/")
    corpus_test.save_to_folder(params.output_folder + "test/")
