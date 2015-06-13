'''
Created on Jun 13, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import math, argparse
from evaluation_metrics import *
from test.test_smtplib import sim_auth

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

class NN_classifier:
    def __init__(self):
        self._train_docs = []
    
    def train(self, vectors_with_classes):
        self._train_docs.extend(vectors_with_classes)
    
    def classify(self, vectors_no_classes):
        results = []
        for vector in vectors_no_classes:
            prediction = self._train_docs[0][1]
            max_sim = -1.0
            for train_doc in self._train_docs:
                sim = cosine(vector, train_doc[0])
                if sim > max_sim:
                    max_sim = sim
                    prediction = train_doc[1]
            results.append(prediction)
        return results
                
    
    def evaluate(self, vectors_with_classes):
        results = self.classify([vector for vector, _ in vectors_with_classes])
        accuracy = compute_accuracy(results, [clss for _, clss in vectors_with_classes])
        return accuracy
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
#     parser.add_argument('-s',action='store_true', help = "Save filtered base terms to file.")
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
        
    classifier = NN_classifier() 
    classifier.train(train_data)
    print("accuracy: " + str(classifier.evaluate(test_data)))
    
    
    