'''
Created on Jun 1, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

import os, codecs, re
from nltk.probability import FreqDist

my_encoding = "utf-8"

class DocumentCorpus:
    def __init__(self, name):
        self._name = name
        self._documents = []
        
    def load_from_folder(self, folder_name):
        for f_name in os.listdir(folder_name):
            with codecs.open(folder_name + f_name, "r", encoding=my_encoding) as f:
                self._documents.append(f.read())
                
    def remove_empty_lines(self):
        self._documents = [self._remove_empty_lines_in_doc(doc) for doc in self._documents]
        
    def get_overlaps(self):
        all_lines = []
        for document in self._documents:
            lines = [line.strip() for line in document.split("\n")]
            all_lines.extend(lines)
        
        distribution = FreqDist(all_lines)
        return distribution
        
    def _remove_empty_lines_in_doc(self, document):
        return re.sub("\n+","\n", document)


if __name__ == '__main__':
    corpus = DocumentCorpus("inland")
    corpus.load_from_folder("classification-dataset/inland/text/")
#     corpus.remove_empty_lines()
    print(len([el for el in corpus.get_overlaps().most_common() if el[1] > 10]))