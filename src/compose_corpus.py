'''
Created on Jun 1, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

import os, codecs, re, argparse, random, math
from nltk.probability import FreqDist
from collections import defaultdict

my_encoding = "utf-8"

class DocumentCorpus:
    def __init__(self, documents=None):
        self._documents = documents if documents else []
        self._corpus_name = "no_name"
        
    def load_from_folder(self, folder_name, class_name = ""):
        """ Adds documents from the specified folder into the corpus. """
        for f_name in os.listdir(folder_name):
            with codecs.open(folder_name + f_name, "r", encoding=my_encoding) as f:
                self._documents.append( (f.read().strip(), create_document_name(f_name, class_name)) )
        print("Loaded {} documents.".format(len(self._documents)))
        self._corpus_name = folder_name.split(os.sep)[-2]
        return self._documents
    
    def load_from_folders(self, folder_name):
        for f_folder_name in os.listdir(folder_name):
            self.load_from_folder(folder_name + f_folder_name + os.sep, f_folder_name)
    
    def save_to_folder(self, folder_name):
        if not os.path.exists(folder_name): os.makedirs(folder_name)
        for document in self._documents:
            with codecs.open(folder_name + document[1], "w", encoding=my_encoding) as out:
                out.write(document[0])
        print("Saved to " + folder_name)
        
    def split_train_test(self, test_ratio = 0.5):
        random.shuffle(self._documents)
        _middle_id = math.ceil(len(self._documents) * test_ratio) 
        return DocumentCorpus(self._documents[:_middle_id]), DocumentCorpus(self._documents[_middle_id:])
    
    def get_classes_dist(self):
        _classes = [get_document_class(doc[1]) for doc in self._documents]
        return FreqDist(_classes)
    
    def print_stat(self):
        lens = [len(doc[0]) for doc in self._documents]
        avg_doc_len = sum(lens) / len(self._documents) if len(self._documents) > 0 else 0
        max_len = max(lens)
        min_len = min(lens)
        print("{} documents.".format(len(self._documents)))
        print("Avg. length: {} \n Max length: {} \n Min length: {}".format(avg_doc_len,max_len,min_len))
        print("Classes: " + str(self.get_classes_dist().most_common()))
    
    def remove_empty_lines(self):
        self._documents = [ (self._remove_empty_lines_in_doc(doc[0]),doc[1]) for doc in self._documents]
        
    def remove_numbers_and_links(self):
        self._documents = [ (self._remove_numbers_and_links_from_document(doc[0]), doc[1] ) for doc in self._documents]
        
    def remove_overlaps(self, line_freq , lines_dist):
        lines_to_remove = {el[0] for el in lines_dist.most_common() if el[1] > line_freq}
        self._documents = [ (self._remove_lines_from_document(doc[0], lines_to_remove), doc[1]) for doc in self._documents]
        print("Repeating lines removed.")
        
    def cut_by_length(self, length):
        self._documents = [doc for doc in self._documents if len(doc[0]) >= length]

    def get_overlaps(self):
        all_lines = []
        for document in self._documents:
            lines = [line.strip() for line in document[0].split("\n")]
            all_lines.extend(lines)
        
        distribution = FreqDist(all_lines)
        if "" in distribution: del distribution[""]
        return distribution
        
    def _remove_empty_lines_in_doc(self, document):
        return re.sub("\n+","\n", document)
            
    def _remove_lines_from_document(self, document, lines_to_remove):
        return "\n".join([line.strip() for line in document.split("\n") if not line.strip() in lines_to_remove])
    
    def _remove_numbers_and_links_from_document(self, document):
        return "\n".join([line.strip() for line in document.split("\n") if not re.match('[\d\.\-\s]+$|https?://[^\s<>"]+$|www\.[^\s<>"]+$', line.strip()) ])
    
def create_document_name(document_name, class_name):
    return (class_name.strip() + "_"  if len(class_name) > 0 else "") + document_name.strip();

def get_document_class(document_name):
    return document_name.split("_",2)[0]

def get_classes(documents):
    return {get_document_class(doc[1]) for doc in documents}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',action='store_true', help = "Clean up documents.")
    parser.add_argument('-f',action='store_true', help = "Classes are separated into folders.")
    parser.add_argument('-l',action='store_true', help = "Save statistics to file.")
    parser.add_argument('-s',type=int, help = "Remove files shorter than the give length in characters. The length is calculate after preprocessing.", default=0)
    parser.add_argument('input_folder', type=str, help = "Corpus input.")
    parser.add_argument('output_folder', type=str, help = "Save to.")
    
    params = parser.parse_args()
    
    save_statistics = params.l
    clean_up_document = params.p
    
    corpus = DocumentCorpus()
    if params.f:
        corpus.load_from_folders(params.input_folder)
    else:    
        corpus.load_from_folder(params.input_folder)
    corpus.print_stat()
    
    distribution = corpus.get_overlaps()
    if clean_up_document:
        corpus.remove_overlaps(1,distribution)
        corpus.remove_empty_lines()
        corpus.remove_numbers_and_links()

    if save_statistics:
        with codecs.open("lines_freq_distributions.csv", "w", encoding=my_encoding) as out:
            out.write("line_length,freq,text\n")
            for k,v in distribution.most_common():
                out.write("{},{},\"{}\"\n".format(len(k),v,k))
        with codecs.open("lines_freq_bins.csv", "w", encoding=my_encoding) as out:
            back_dist = defaultdict(int)
            back_dist_length = defaultdict(int)
            for k,v in distribution.most_common():
                back_dist[v] += 1
                back_dist_length[v] += len(k)
            out.write("freq,bin_size,avg_length\n")
            for i in sorted(set(distribution.values())):
                bin_size = back_dist[i]
                avg_length = back_dist_length[i] / float(bin_size)
                out.write("{},{},{}\n".format(i,bin_size,avg_length))     
            
    
    lens = [len(doc[0]) for doc in corpus._documents]
#     for doc in [doc for doc in corpus._documents if len(doc) > 23 and len(doc) < 60]:
#         print(doc)
    if save_statistics:
        with codecs.open("document_length_dist.csv", "w", encoding=my_encoding) as out:
            out.write("id,length\n")
            for i,v in enumerate(sorted(lens,reverse=True)):
                out.write("{},{}\n".format(i,v))    

    corpus.print_stat()
    corpus.cut_by_length(params.s)
    corpus.print_stat()
    corpus.save_to_folder(params.output_folder)
    
