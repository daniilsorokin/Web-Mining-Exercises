'''
Created on Jun 3, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

import codecs, math, argparse, os
from vector_representation import StemmedCorpus, filter_base_terms, save_as_libsvm


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_folder_train', type=str, help = "Corpus input train.")
    parser.add_argument('input_folder_test', type=str, help = "Corpus input test.")
    parser.add_argument('output_folder', type=str, help = "Save to.")
    
    params = parser.parse_args()
    if not os.path.exists(params.output_folder): os.makedirs(params.output_folder)


    train_corpus = StemmedCorpus()
    train_corpus.load_from_folder(params.input_folder_train)
    train_corpus.preprocess_documents()
    test_corpus = StemmedCorpus()
    test_corpus.load_from_folder(params.input_folder_test)
    test_corpus.preprocess_documents()
    
    base_terms = train_corpus.compute_base_terms()
    print("Base terms extracted: " + str(len(base_terms)))
    max_n = len(base_terms)
    
    ns = [5*2**exp for exp in range(0,math.floor(math.log2(max_n/2))) ] + [max_n]
    print(ns)
    
    for n in ns:
        base_terms_n = filter_base_terms(base_terms, n)
        print("Base terms filtered: " + str(len(base_terms_n)))
        train_vectors = train_corpus.compute_vectors(base_terms_n)
        save_as_libsvm(train_vectors, params.output_folder + "train_vectors_n" + str(len(base_terms_n)) + ".data")
        test_vectors = train_corpus.compute_vectors(base_terms_n)
        save_as_libsvm(test_vectors, params.output_folder + "test_vectors_n" + str(len(base_terms_n)) + ".data")