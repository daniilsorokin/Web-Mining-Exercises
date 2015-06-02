'''
Created on Jun 1, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

import os, codecs, re, argparse
from nltk.probability import FreqDist
from collections import defaultdict

my_encoding = "utf-8"

class DocumentCorpus:
    def __init__(self):
        self._documents = []
        
    def load_from_folder(self, folder_name):
        for f_name in os.listdir(folder_name):
            with codecs.open(folder_name + f_name, "r", encoding=my_encoding) as f:
                self._documents.append( (f.read().strip(), f_name) )
        print("Loaded {} documents.".format(len(self._documents)))
    
    def save_to_folder(self, folder_name):
        if not os.path.exists(folder_name): os.makedirs(folder_name)
        for document in self._documents:
            with codecs.open(folder_name + document[1], "w", encoding=my_encoding) as out:
                out.write(document[0])
        print("Saved to " + folder_name)
    
    def print_stat(self):
        lens = [len(doc[0]) for doc in self._documents]
        avg_doc_len = sum(lens) / len(self._documents)
        max_len = max(lens)
        min_len = min(lens)
        print("{} documents.".format(len(self._documents)))
        print("Avg. length: {} \n Max length: {} \n Min length: {}".format(avg_doc_len,max_len,min_len))
    
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l',action='store_true', help = "Save statistics to file.")
    parser.add_argument('-s',type=int, help = "Remove files shorter than the number. The length is calculate after preprocessing.", default=1)
    parser.add_argument('input_folder', type=str, help = "Corpus input.")
    parser.add_argument('output_folder', type=str, help = "Save to.")
    
    params = parser.parse_args()
    
    
    save_statistics = params.l
    
    corpus = DocumentCorpus()
    corpus.load_from_folder(params.input_folder)
    corpus.print_stat()
    distribution = corpus.get_overlaps()
    
#     # Development code
#     sorted_dist = distribution.most_common()
# 
#     no_more_1000 = [el for el in sorted_dist if el[1] > 1000]
#     avg_len_no_1000 = sum([len(el[0]) for el in no_more_1000]) / len(no_more_1000)
#     no_more_1 = [el for el in sorted_dist if el[1] > 1]
#     avg_len_no_1 = sum([len(el[0]) for el in no_more_1]) / len(no_more_1)
#     no_eq_1 = [el for el in sorted_dist if el[1] == 1]
#     avg_len_no_eq_1 = sum([len(el[0]) for el in no_eq_1]) / len(no_eq_1)
#     
#     print("Unique lines: {}".format( len(distribution) )) 
#     print("Line duplicates:")
#     print("{} - frequency > 1000, avg. length = {}".format(len(no_more_1000), avg_len_no_1000))
#     print("{} - frequency > 1, avg. length = {}".format(len(no_more_1), avg_len_no_1))
#     print("{} - frequency = 1, avg. length = {}".format(len(no_eq_1), avg_len_no_eq_1))    


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
    
