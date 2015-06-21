'''
Created on Jun 13, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
from _collections import defaultdict

# Numeric predictions

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

# Nominal predictions

def compute_accuracy(predicted_labels, gold):
    tp_tn = 0
    for i,g in enumerate(gold):
        p = predicted_labels[i]
        if p == g: tp_tn += 1
    return  float(tp_tn) / len(gold)  

def compute_confusion_matrix(predicted_labels, gold):
    c_matrix = defaultdict(lambda : defaultdict(int))
    for i,p in enumerate(predicted_labels):
        c_matrix[gold[i]][p] += 1
    return c_matrix

def c_matrix_tostr(c_matrix):    
    clsses = list(c_matrix.keys())
    r_str = "gold" + ",".join(clsses) + "\n"
    for clss in clsses:
        r_str += clss + ","
        for clss_2 in clsses:
            r_str += str(c_matrix[clss][clss_2]) + ","
        r_str += "\n"
    return r_str

def compute_cat_tp(c_matrix):
    tp = sum(c_matrix[clss][clss] for clss in c_matrix.keys())
    return tp

def compute_cat_fp(c_matrix):
    fp = sum(c_matrix[clss1][clss2] for clss1 in c_matrix.keys() for clss2 in c_matrix.keys()) - sum(c_matrix[clss][clss] for clss in c_matrix.keys())
    return fp

def compute_cat_fn(c_matrix):
    fn = sum(c_matrix[clss1][clss2] for clss1 in c_matrix.keys() for clss2 in c_matrix.keys()) - sum(c_matrix[clss][clss] for clss in c_matrix.keys())
    return fn
            
def compute_micro_precision(predicted_labels, gold):
    clsses = set(gold)
    tp = 0
    fp = 0
    for clss in clsses:
        for i,g in enumerate(gold):
            p = predicted_labels[i]
            if g == clss and p == clss: tp += 1
            if g != clss and p == clss: fp += 1
    return float(tp / (tp + fp))
    

def compute_micro_recall(predicted_labels, gold):
    clsses = set(gold)
    tp = 0
    fn = 0
    for clss in clsses:
        for i,g in enumerate(gold):
            p = predicted_labels[i]
            if g == clss and p == clss: tp += 1
            if g == clss and p != clss: fn += 1
    return float(tp / (tp + fn))

def compute_micro_f(predicted_labels, gold):
    m_p = compute_micro_precision(predicted_labels, gold)
    m_r = compute_micro_recall(predicted_labels, gold)
    return 2*m_p*m_r / (m_p + m_r)
    
