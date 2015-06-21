'''
Created on Jun 13, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import math, argparse, codecs
import logging
from collections import Counter, defaultdict
from statistics import mean, variance
from evaluation_metrics import *
from scale import get_mu_sigma
from compose_corpus import get_document_class
from vector_representation import read_vectors_from_csv

my_encoding = 'utf-8'
min_freq = 1e-4
epsilon = 1e-7
logging.basicConfig(filename="classifiers.log",level=logging.INFO)

def cosine(a, b):
    amagn = min_freq
    bmagn = min_freq
    abproduct = min_freq
    for idx in range(len(a)):
        amagn += a[idx] * a[idx];
        bmagn += b[idx] * b[idx];
        abproduct += a[idx] * b[idx];
    amagn = math.sqrt(amagn);
    bmagn = math.sqrt(bmagn);
    cosine = abproduct / (amagn * bmagn);
    return cosine;

def euclideanDis(a, b):
    return math.sqrt( sum( (v1 - v2)**2 for v1,v2 in zip(a,b)) )

def _pdf(mu, sigma, x ):
    term_1 = 1 / math.sqrt( 2 * math.pi * sigma)
    term_2 = math.exp( -((x - mu)**2 / (2 * sigma) ) )
    if term_2 == 0.0: term_2 = math.exp(-700)
    if term_1*term_2 == 0: logging.info("pdf = {} * {} = 0.0".format(term_1, term_2)) 
    return term_1 * term_2


class EvalClassifier():

    def evaluate(self, vectors_with_classes):
        vectors, doc_names = zip(*vectors_with_classes)
#         results = self.classify([vector for vector, _ in vectors_with_classes])
#         accuracy = compute_accuracy(results, [get_document_class(clss) for _, clss in vectors_with_classes])
        results = self.classify(vectors)
        gold =  [get_document_class(doc_name) for doc_name in doc_names]
        compute_confusion_matrix(results, gold)
        accuracy = compute_accuracy(results, gold)
        m_p = compute_micro_precision(results, gold)
        m_r = compute_micro_recall(results, gold)
        m_f1 = compute_micro_f(results, gold)
        logging.info("Accuracy: " + str(accuracy))
        logging.info(c_matrix_tostr(compute_confusion_matrix(results, gold)))
        return accuracy, m_p, m_r, m_f1

class NBClassifier(EvalClassifier):
    def __init__(self):
        EvalClassifier.__init__(self)
        self._p_clss = defaultdict(float)
        self._clss_x_mean = defaultdict(list)
        self._clss_x_variance = defaultdict(list)
        self._x_mean = []
        self._x_variance = []
        self._default_class = "" 
        self._scaling_factor = 1.0
    
    def train(self, vectors_with_classes):
        _clss_vectors = defaultdict(list)
        for vector, doc_name in vectors_with_classes:
            clss = get_document_class(doc_name)
            self._p_clss[clss] += 1
            _clss_vectors[clss].append(vector)
            
        self._default_class, _ = Counter(self._p_clss).most_common(1)[0]
        self._x_mean, self._x_variance = get_mu_sigma(vectors_with_classes)
   
        for clss, vectors in _clss_vectors.items():
            self._p_clss[clss] = float(self._p_clss[clss]/len(vectors_with_classes))
            variable_vectors = zip(*vectors)
            for v_vector in variable_vectors:
                self._clss_x_mean[clss].append(mean(v_vector))
                self._clss_x_variance[clss].append(variance(v_vector))
        logging.info("Classes learned: " + str(self._p_clss))
        logging.info("Number of dimensions: " + str(len(self._clss_x_mean["learned"])))
        logging.info("Means learned: " + str(self._clss_x_mean))
        logging.info("Variance learned: " + str(self._clss_x_variance))
        
    def get_model(self):
        return self._clss_x_mean, self._clss_x_variance
        
    def classify(self, vectors_no_classes):
        results = []
        logging.info("Classifying {} documents.".format(len(vectors_no_classes)))
        for vector in vectors_no_classes:
            max_p = 0.0
            prediction = self._default_class
            for clss, p_clss in self._p_clss.items():
                product_p_x_clss = 1.0
                for i,x in enumerate(vector):
                    clss_x_variance = self._clss_x_variance[clss][i]
                    if clss_x_variance != 0.0:
                        p_x_clss = _pdf(self._clss_x_mean[clss][i], clss_x_variance, x) / _pdf(self._x_mean[i], self._x_variance[i], x)
                        product_p_x_clss *= p_x_clss
                p_clss_vector = p_clss * product_p_x_clss
                if p_clss_vector > max_p:
                    max_p = p_clss_vector
                    prediction = clss
            logging.info("Class: {}, p: {}".format(prediction, max_p))
            results.append(prediction)
        return results    

class NNClassifier(EvalClassifier):
    def __init__(self, k=1):
        EvalClassifier.__init__(self)
        self._train_docs = []
        self._k = k
        self._default_class = "None"
        
    def train(self, vectors_with_classes):
        self._train_docs.extend([ (vector, get_document_class(doc_name)) for vector, doc_name in vectors_with_classes])
        self._default_class, _ = Counter( clss for _, clss in self._train_docs).most_common(1)[0]
        logging.info("Default class: " + self._default_class)
    
    def classify(self, vectors_no_classes):
        results = []
        logging.info("Classifying {} documents.".format(len(vectors_no_classes)))
        sim_ties = 0
        cntr_ties = 0
        for vector in vectors_no_classes:
#             prediction = self._train_docs[0][1]
#             max_sim = -1.0
            sims = []
            for train_doc in self._train_docs:
                sim = cosine(vector, train_doc[0])
                sims.append( (sim, train_doc[1]) )
#                 if sim > max_sim:
#                     max_sim = sim
#                     prediction = train_doc[1]
            sims = sorted(sims, key = lambda x: x[0], reverse=True)
            if sims[self._k-1][0] - sims[self._k][0] < 0.00001: sim_ties += 1
            predicted_classes = [clss for sim, clss in sims[:self._k] if sim > 0.0]
            logging.info(sims[:self._k])
            cntr = Counter(predicted_classes)
#             two_choices = cntr.most_common(2)
#             if two_choices[0][1] == two_choices[1][1]: cntr_ties += 1
            prediction, _ = cntr.most_common(1)[0]  if len(predicted_classes) > 0 else (self._default_class, 0)
            results.append(prediction)
        logging.info("Sim ties: " + str(sim_ties))
        logging.info("Cntr ties: " + str(cntr_ties))
        return results
                

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e',action='store_true', help = "Evaluate on test file.")
    parser.add_argument('-k',type=int, help = "K for KNN.", default=1)
    parser.add_argument('-c', choices=["KNN", "NB"], help = "Number of most frequent base terms to keep.", default = "NB")
    
#     parser.add_argument('-n',type=int, help = "Number of most frequent base terms to keep.", default=10)
#     parser.add_argument('-b', type=argparse.FileType('r', encoding=my_encoding),  
#                         help = "Read a list of base terms from file. Should be in " + my_encoding + ". Options -s and -n ignored.")
#     
    parser.add_argument('train_file', type=str)
    parser.add_argument('test_file', type=str)

    params = parser.parse_args()
    
    train_data = read_vectors_from_csv(params.train_file)
    test_data = read_vectors_from_csv(params.test_file)
#     for line in params.test_file.readlines():
#         columns = line.split(",")
#         clss = columns[0]
#         vector = [float(el) for el in columns[1:]]
#         test_data.append( (vector, clss) )
        
    classifier = NBClassifier() if params.c == "NB" else NNClassifier(params.k)
    logging.info("Trainin {} on: {}".format(params.c, params.train_file)) 
    classifier.train(train_data)
    if params.e:
        logging.info("Evaluating on: {}".format(params.test_file))
        print("accuracy: " + str(classifier.evaluate(test_data)))
    else:
        logging.info("Classifying: {}".format(params.test_file))
        results = classifier.classify([vector for vector, _ in test_data])
        with codecs.open("G42_predictions", "w", encoding="utf-8") as out:
            for i in range(len(test_data)):
                doc_name = test_data[i][1]
                out.write(doc_name + "\t" + results[i] + "\n")
     
    
    
    