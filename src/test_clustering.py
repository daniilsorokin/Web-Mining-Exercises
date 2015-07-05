'''
Created on July 05, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import argparse, logging
from vector_representation import read_vectors_from_csv
from clustering_methods import KMeans
from _collections import defaultdict
import codecs

my_encoding='utf-8'

def group_clusters(assignment, k):
    clusters = []
    for i in range(k):
        clusters.append([j for j,c in enumerate(assignment) if c == i])
    return clusters

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-k',type=int, help = "K for clustering.", default=1)
    parser.add_argument('input_file', type=str)
    params = parser.parse_args()
    logging.basicConfig(filename="clustering.log", level=logging.INFO)
    
    input_data, names = list(zip(*read_vectors_from_csv(params.input_file)))
    kmeans = KMeans()
    logging.info("Clustering on: {}".format(params.input_file))
    assignments = [] 
    iterations = 20
    print("Clustering")
    for i in range(iterations):
        assignment = kmeans.cluster(list(input_data), params.k)
        assignments.append(assignment)
        logging.info(assignment)
    print("Analysis")
    pair_assignments = defaultdict(int)    
    for i in range(iterations):
        clusters = group_clusters(assignments[i], params.k)
        logging.info(clusters)
        for cluster in clusters:
            for i,j in [ (i,j) for i in cluster for j in cluster if i != j]:
                pair_assignments[(i,j)] += 1
    
    logging.info(pair_assignments)
    with codecs.open("test_clustering_results.txt", "w", encoding=my_encoding) as out:
        out.write("Most common pairs: " + str( [(names[i], names[j], pair_assignments[(i,j)]) for i,j in sorted(pair_assignments.keys(), key = lambda x: pair_assignments[x], reverse = True)[:10] ]))
        out.write("\n")
        out.write("Most rare pairs: " + str( [(names[i], names[j], pair_assignments[(i,j)]) for i,j in sorted(pair_assignments.keys(), key = lambda x: pair_assignments[x])[:10] ]))
    
            
            
        
