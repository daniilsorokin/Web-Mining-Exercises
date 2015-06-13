'''
Created on Jun 13, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import math, argparse, codecs
from collections import Counter
from evaluation_metrics import *

my_encoding = 'utf-8'
min_freq = 0.0001

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

    

class NN_classifier:
    def __init__(self, k=1):
        self._train_docs = []
        self._k = k
        
    def train(self, vectors_with_classes):
        self._train_docs.extend(vectors_with_classes)
    
    def classify(self, vectors_no_classes):
        results = []
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
            predicted_classes = [clss for _, clss in sims[:self._k]]
            prediction, _ = Counter(predicted_classes).most_common(1)[0]
            results.append(prediction)
        with codecs.open("results.txt", "w", encoding="utf-8") as out:
            for result in results:
                out.write(result + "\n")
        return results
                
    
    def evaluate(self, vectors_with_classes):
        results = self.classify([vector for vector, _ in vectors_with_classes])
        accuracy = compute_accuracy(results, [clss for _, clss in vectors_with_classes])
        return accuracy
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e',action='store_true', help = "Evaluate on test file.")
#     parser.add_argument('-n',type=int, help = "Number of most frequent base terms to keep.", default=10)
#     parser.add_argument('-b', type=argparse.FileType('r', encoding=my_encoding),  
#                         help = "Read a list of base terms from file. Should be in " + my_encoding + ". Options -s and -n ignored.")
#     
    parser.add_argument('train_file', type=argparse.FileType('r', encoding=my_encoding))
    parser.add_argument('test_file', type=argparse.FileType('r', encoding=my_encoding))

    params = parser.parse_args()
    
    train_data = []
    for line in params.train_file.readlines():
        columns = line.split(",")
        clss = columns[0]
        vector = [float(el) for el in columns[1:]]
        train_data.append( (vector, clss) )
    
    test_data = []
    for line in params.test_file.readlines():
        columns = line.split(",")
        clss = columns[0]
        vector = [float(el) for el in columns[1:]]
        test_data.append( (vector, clss) )
        
    classifier = NN_classifier(10) 
    classifier.train(train_data)
    if params.e:
        print("accuracy: " + str(classifier.evaluate(test_data)))
    else:
        results = classifier.classify([vector for vector, doc_name in test_data])
        with codecs.open("G42_predictions", "w", encoding="utf-8") as out:
            for i in range(len(test_data)):
                doc_name = test_data[i][1]
                out.write(doc_name + "\t" + results[i] + "\n")
     
    
    
    