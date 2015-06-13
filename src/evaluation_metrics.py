'''
Created on Jun 13, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

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

def compute_f(clss, predictions, gold,  t=0.5):
    return compute_tp(clss, predictions, gold, t) / (compute_tp(clss, predictions, gold, t) + compute_fn(clss, predictions, gold, t) + 0.0001)


def compute_accuracy(predicted_labels, gold):
    tp_tn = 0
    for i,g in enumerate(gold):
        p = predicted_labels[i]
        if p == g: tp_tn += 1
    return  float(tp_tn) / len(gold)  

def compute_micro_precision(predictions, gold, t=0.5):
    pass

def compute_micro_recall(predictions, gold, t=0.5):
    pass

def compute_micro_f(predictions, gold, t=0.5):
    pass
