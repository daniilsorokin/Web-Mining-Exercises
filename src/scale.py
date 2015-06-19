'''
Created on Jun 18, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

import codecs, math, argparse, os
from statistics import mean, variance
from vector_representation import read_vectors_from_csv, save_as_csv

my_encoding = 'utf-8'

def z_norm_vectors(vectors_with_classes, mu_v, sigma_v):
    new_vectors_with_classes = []
    for vector, name in vectors_with_classes:
        new_vector = []
        for i,v in enumerate(vector):
            if sigma_v[i] != 0.0:
                new_vector.append( (v - mu_v[i]) / sigma_v[i] )
            else:
                new_vector.append( v )
        new_vectors_with_classes.append( (new_vector, name) )
    return new_vectors_with_classes
    
def get_mu_sigma(vectors_with_classes):
    mu_v = []
    sigma_v = []
    vectors = zip(*[vector for vector, _ in vectors_with_classes])
    for v_vector in vectors:
        mu_v.append(mean(v_vector))
        sigma_v.append(variance(v_vector))
    return mu_v, sigma_v

def scale_vectors(vectors_with_classes, min_v, max_v):
    new_vectors_with_classes = []
    for vector, name in vectors_with_classes:
        new_vector = []
        for i,v in enumerate(vector):
            if max_v[i] != 0.0 or min_v[i] != 0.0:
                new_vector.append( (v - min_v[i]) / (max_v[i] - min_v[i]) )
            else:
                new_vector.append( v )
        new_vectors_with_classes.append( (new_vector, name) )
    return new_vectors_with_classes

def get_min_max(vectors_with_classes):
    min_v = list(vectors_with_classes[0][0])
    max_v = list(vectors_with_classes[0][0])
    for vector, _ in vectors_with_classes:        
        for i,v in enumerate(vector):            
            if v < min_v[i]: min_v[i] = v
            if v > max_v[i]: max_v[i] = v
    return min_v, max_v

def read_min_max_vectors_from_csv(file_name):
    min_v = [] 
    max_v = []
    data = []
    with codecs.open(file_name, "r", encoding=my_encoding) as doc_file:
        for line in doc_file.readlines():
            columns = line.split(",")
            vector = [float(el) for el in columns[0:]]
            data.append( vector )
    if len(data) > 1:
        min_v = data[0]
        max_v = data[1]
    return min_v, max_v

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', type=str,  
                        help = "Read a scale from file. Should be in " + my_encoding + ".")
    parser.add_argument('-z',action='store_true', help = "Z-score normalization.")    
    parser.add_argument('input_file', type=str)
    
    params = parser.parse_args()
    
    input_data = read_vectors_from_csv(params.input_file)
    preprocess_alias = get_min_max
    scale_alias = scale_vectors
    if params.z:
        preprocess_alias = get_mu_sigma
        scale_alias = z_norm_vectors        
    if params.b:
        min_v, max_v = read_min_max_vectors_from_csv(params.b)
        print("Scale read from file: {}, {}".format(str(len(min_v)), str(len(max_v))))
        input_data = scale_alias(input_data, min_v, max_v)
    else:
        min_v, max_v = preprocess_alias(input_data)
        print(min_v[:10])
        print(max_v[:10])
        input_data = scale_alias(input_data, min_v, max_v)
        scale_vector_filename = os.path.basename(params.input_file)
        with codecs.open("scale_vector_" + scale_vector_filename + ".csv", "w", encoding=my_encoding) as out: 
            out.write(",".join(map(str,min_v)) + "\n")
            out.write(",".join(map(str,max_v)) + "\n")
        print("Base term list saved to scale_vector_" + scale_vector_filename + ".csv")
    save_as_csv(input_data, os.path.splitext(params.input_file)[0] + "_scaled" + ("_z" if params.z else "") + ".csv")
