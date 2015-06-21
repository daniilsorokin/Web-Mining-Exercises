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
    parser.add_argument('-n', nargs=3, type=int, help = "Number of the base terms to keep. Three parameters to generate a range: n[0]**x for x in range(n[1],n[2])")
    parser.add_argument('-k', nargs=3, type=int, help = "K for KNN. Three parameters to generate a range: range(n[0],n[1],n[2])", default=[0,1,1])
    parser.add_argument('-c', choices=["KNN", "NB"], help = "Classifier to use.", default = "NB")
    parser.add_argument('-s', choices=["Z", "N"], help = "Scaling.", default = "Z")
    parser.add_argument('-f', choices=["idf", "mi"], help = "Base term filtering criterion.", default = "mi")
    parser.add_argument('-w', action='store_true', help = "Lemmatize tokens.")
    parser.add_argument('-r', action='store_false', help = "Keep stopwords.")
    
    parser.add_argument('train_folder', type=str, help = "Training corpus input.")
    parser.add_argument('test_folder', type=str, help = "Test corpus input.")
    params = parser.parse_args()

    scale_preprocess_alias = get_mu_sigma if params.s == "Z" else get_min_max
    scale_alias = z_norm_vectors if params.s == "Z" else scale_vectors       

    print("Loading data.")
    train_corpus = StemmedCorpus(language="english")
    train_corpus.load_from_folder(params.train_folder)
    train_corpus.preprocess_documents(lemmatize=params.w, remove_stopwords=params.r)
    test_corpus = StemmedCorpus(language="english")
    test_corpus.load_from_folder(params.test_folder)
    test_corpus.preprocess_documents(lemmatize=params.w, remove_stopwords=params.r)
    print("Compute base terms.")
    base_terms = compute_base_terms(train_corpus._stemmed_documents)
    print("Base terms extracted: " + str(len(base_terms)))
    for n in [params.n[0]**x for x in range(params.n[1], params.n[2])] :
#         print("Compute vectors for N=" + str(n))
        base_terms_n = filter_base_terms(base_terms, n) if params.f == "idf" else filter_base_terms_with_mi(base_terms, n)
        train_vectors = compute_vectors(train_corpus._stemmed_documents, base_terms_n)
        test_vectors = compute_vectors(test_corpus._stemmed_documents, base_terms_n)
#         print("Scaling vectors ({}).".format(params.s))
        mu_min_v, sigma_max_v = scale_preprocess_alias(train_vectors)
        train_vectors = scale_alias(train_vectors, mu_min_v, sigma_max_v)
        test_vectors = scale_alias(test_vectors, mu_min_v, sigma_max_v)
        for k in list(range(params.k[0], params.k[1], params.k[2])):
            print("Training. Cl= {}, S= {}, F= {}, L= {}, R={}, N={}, K={}".format(params.c, params.s, params.f, params.w, params.r, n, k))
            classifier = NBClassifier() if params.c == "NB" else NNClassifier(k)
            classifier.train(train_vectors)
            accuracy, m_p, m_r, m_f1 = classifier.evaluate(test_vectors)
            print("accuracy, P, R, F1: {},{},{},{}".format(accuracy, m_p, m_r, m_f1))