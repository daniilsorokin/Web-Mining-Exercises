'''
Created on Jun 3, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import argparse, codecs
from evaluation_metrics import *
my_encoding = 'utf-8'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', type=argparse.FileType('r', encoding=my_encoding), help = "Input file with libSVM predictions.")
    parser.add_argument('goldfile', type=argparse.FileType('r', encoding=my_encoding), help = "Input file with gold labels.")
    
    params = parser.parse_args()
    
    gold_labels = [int(line.strip().split(" ", 2)[0])  for line in params.goldfile.readlines()]
    
    # Compute everything from the perspective of class "0" - Ausland
    predictions = [line.strip().split(" ", 3)  for line in params.inputfile.readlines()[1:]]
    predictions = [ float(p1) for _, p1, _ in predictions ]
    thresholds = sorted(set(predictions), reverse=True)
    
    out = codecs.open("confusion-matrix-t05.csv", "w", encoding=my_encoding)
    out.write("{ },Gold 'Ausland', Gold 'Inland'\n")
    out.write("SVM 'Ausland',{} (TP),{} (FP)\n".format(compute_tp(0,predictions, gold_labels), compute_fp(0,predictions, gold_labels)))
    out.write("SVM 'Inland',{} (FN),{} (TN)\n".format(compute_fn(0,predictions, gold_labels), compute_tn(0,predictions, gold_labels)))
    out.close()
    print("Confusion matrix in confusion-matrix-t05.csv")
    
    out = codecs.open("recall-precision-curve.csv", "w", encoding=my_encoding)
    out.write("Threshold,Recall,Precision\n")
    for threshold in thresholds:
        p = compute_precision(0,predictions, gold_labels, threshold )
        r = compute_recall(0,predictions, gold_labels, threshold )
        if p == r: print(p)
        out.write("{},{},{}\n".format(threshold,r,p))
    out.close()
    print("Results in recall-precision-curve.csv")
    