'''
Created on Jun 3, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import argparse, codecs
my_encoding = 'utf-8'

def compute_tp(clss, predictions, gold, t=0.5):
    tp = 0
    for i,g in enumerate(gold):
        prediction = 0 if predictions[i] >= t else 1
        if g == clss and prediction == clss: tp += 1
    return  tp

def compute_fp(clss, predictions, gold, t=0.5):
    fp = 0
    for i,g in enumerate(gold):
        prediction = 0 if predictions[i] >= t else 1
        if prediction == clss and not g == clss: fp += 1
    return  fp
     
def compute_fn(clss, predictions, gold, t=0.5):
    fn = 0
    for i,g in enumerate(gold):
        prediction = 0 if predictions[i] >= t else 1
        if g == clss and not prediction == clss: fn += 1
    return  fn     

def compute_tn(clss, predictions, gold, t=0.5):
    tn = 0
    for i,g in enumerate(gold):
        prediction = 0 if predictions[i] >= t else 1
        if not g == clss and not prediction == clss: tn += 1
    return  tn

     
def compute_precision(clss, predictions, gold, t=0.5):
    return compute_tp(clss, predictions, gold, t) / (compute_tp(clss, predictions, gold, t) + compute_fp(clss, predictions, gold, t) + 0.0001)

def compute_recall(clss, predictions, gold,  t=0.5):
    return compute_tp(clss, predictions, gold, t) / (compute_tp(clss, predictions, gold, t) + compute_fn(clss, predictions, gold, t) + 0.0001)

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
    