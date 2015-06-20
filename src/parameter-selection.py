'''
Created on Jun 20, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

from classfiers import *
from vector_representation import *
from scale import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
#     parser.add_argument('-l', action='store_true', help = "Normalize frequency values by document length.")
    parser.add_argument('-n', nargs=4, type=int, help = "Number of most frequent base terms to keep.")
    parser.add_argument('-k', nargs=3, type=int, help = "K for KNN.", default="0 1 1")
    parser.add_argument('-c', choices=["KNN", "NB"], help = "Number of most frequent base terms to keep.", default = "NB")
    parser.add_argument('-s', choices=["Z", "N"], help = "Scaling.", default = "Z")
    
    parser.add_argument('train_folder', type=str, help = "Training corpus input.")
    parser.add_argument('test_folder', type=str, help = "Test corpus input.")
#     parser.add_argument('output_folder', type=str, help = "Save to.")
    
    params = parser.parse_args()
#     if not os.path.exists(params.output_folder): os.makedirs(params.output_folder)

    scale_preprocess_alias = get_mu_sigma if params.s == "Z" else get_min_max
    scale_alias = z_norm_vectors if params.s == "Z" else scale_vectors       

    print("Loading data.")
    train_corpus = StemmedCorpus(language="english")
    train_corpus.load_from_folder(params.train_folder)
    train_corpus.preprocess_documents()
    test_corpus = StemmedCorpus(language="english")
    test_corpus.load_from_folder(params.test_folder)
    test_corpus.preprocess_documents()
    print("Compute base terms.")
    base_terms = compute_base_terms(train_corpus._stemmed_documents)
    print("Base terms extracted: " + str(len(base_terms)))
    for n in [params.n[0]**x for x in range(params.n[1], params.n[2], params.n[3])] :
        print("Compute vectors for N=" + str(n))
        base_terms_n = filter_base_terms(base_terms, n)
        train_vectors = compute_vectors(train_corpus._stemmed_documents, base_terms_n)
        test_vectors = compute_vectors(test_corpus._stemmed_documents, base_terms_n)
        print("Scaling vectors ({}).".format(params.s))
        mu_min_v, sigma_max_v = scale_preprocess_alias(train_vectors)
        train_vectors = scale_alias(train_vectors, mu_min_v, sigma_max_v)
        test_vectors = scale_alias(test_vectors, mu_min_v, sigma_max_v)
        for k in list(range(params.k[0], params.k[1], params.k[2])):
            print("Training. Classifier: {}. Scaling: {}. Parameters: N={}, K={}".format(params.c, params.s, n, k))
            classifier = NBClassifier() if params.c == "NB" else NNClassifier(k)
            classifier.train(train_vectors)
            accuracy = classifier.evaluate(test_vectors)
            print("accuracy: " + str(accuracy))