'''
Created on Jun 21, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import argparse
from vector_representation import read_vectors_from_csv
from classfiers import NBClassifier
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('train_file', type=str)
    
    params = parser.parse_args()
    
    train_data = read_vectors_from_csv(params.train_file)
    print("Building a model.")
    classifier = NBClassifier()
    classifier.train(train_data)
    means_v, variance_v = classifier.get_model()
    num_features = 20
    index = np.arange(num_features)
    bar_width = 0.05
    for i, clss in enumerate(means_v.keys()):
        plt.bar(index + (bar_width*i), means_v[clss][:num_features], width=bar_width,
                 yerr=variance_v[clss][:num_features])
    plt.show()
    
#     obs = np.array([[14452, 4073, 4287], [30864, 11439, 9887]])
#     chi2, p, dof, expected = stats.chi2_contingency(obs)
#     print(p)

    
    
    
    
