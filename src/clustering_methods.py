'''
Created on July 04, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

import random
import logging
from classifiers import euclideanDis
from vector_representation import read_vectors_from_csv
from statistics import mean
from collections import defaultdict
import argparse, os
import codecs
from shutil import copyfile

my_encoding = "utf-8"

def save_assignment_stat(assignments, names):
    with codecs.open("clustering_assignments_stats.csv", "w", encoding=my_encoding) as out:
        cluster_size = defaultdict(int)
        cluster_names = defaultdict(lambda: [])
        for i, a in enumerate(assignments):
            cluster_size[a] += 1
            cluster_names[a].append(names[i])
        out.write("Cluster id,Size,Ex.\n")
        for c, s in cluster_size.items():
            out.write("{},{},{}\n".format(c,s, (cluster_names[c][:4] if len(cluster_names[c]) > 4 else cluster_names[c]) ))
    

class KMeans():
    
    def __init__(self):
        self._means = []
        self._k = 0
    
    def cluster(self, vectors, k):
        self._k = k
        if self._k > len(vectors): raise Exception("K must be smaller than the dataset size.")
        self._means = random.sample(vectors, self._k)
        _converged = False
        _assignments = []
        iteration = 1
        while not _converged:
            logging.info(str(iteration) + " iteration: " + str(self._means))
            iteration += 1
            new_assignments = self._assignment(vectors)
            self._means = self._update(vectors, new_assignments)
            _converged = new_assignments == _assignments 
            _assignments = new_assignments
        return _assignments

    def _assignment(self, vectors):
        assignments = []
        for vector in vectors:
            g_min = -1
            i_m = 0
            for i, m in enumerate(self._means):
                c_min = euclideanDis(vector, m)
                if c_min < g_min or g_min==-1:
                    g_min = c_min
                    i_m = i
            assignments.append(i_m)
        return assignments
    
    def _update(self, vectors, assignments):
        mean_vectors = defaultdict(lambda: [])
        for i, a in enumerate(assignments):
            mean_vectors[a].append(vectors[i])
        new_means = []
        for i in range(len(self._means)):
            new_mean  = [ mean(dimension_vector)  for dimension_vector in zip(*mean_vectors[i])]
            new_means.append(new_mean)   
        return new_means     
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-k',type=int, help = "K for clustering.", default=1)
    parser.add_argument('-s',type=str, help = "Save clusters to folders. You have to specify the folder containing original files.", default=None)
    parser.add_argument('input_file', type=str)
    params = parser.parse_args()
    logging.basicConfig(filename="clustering.log", level=logging.INFO)

    input_data, names = zip(*read_vectors_from_csv(params.input_file))
    kmeans = KMeans()
    logging.info("Clustering on: {}".format(params.input_file))
    assignments = kmeans.cluster(list(input_data), params.k)
    with codecs.open("clustering_assignments.csv", "w", encoding=my_encoding) as out:
        for i, name in enumerate(names):
            out.write("{}, {}\n".format(name, assignments[i]))
    print("Clustering finished")
    save_assignment_stat(assignments, names)
    if params.s:
        print("Grouping files")
        for i, name in enumerate(names):
            if not os.path.exists(params.s + os.sep + str(assignments[i])): os.makedirs(params.s + os.sep + str(assignments[i]))
            copyfile(params.s + name, params.s + os.sep + str(assignments[i]) + os.sep + name)
            
        
        
    
    
    
    