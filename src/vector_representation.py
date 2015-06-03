'''
Created on Jun 2, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import codecs, math, argparse, os
from nltk.probability import FreqDist
from nltk.tokenize import regexp_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import defaultdict
from compose_corpus import DocumentCorpus, get_document_class, get_classes
from pyparsing import LineStart


pattern_words = "\w[\w\-0-9']+"
my_encoding = 'utf-8'

class StemmedCorpus(DocumentCorpus):
    def __init__(self, documents=None, language="german"):
        DocumentCorpus.__init__(self, documents)
        with codecs.open("stopwords/" + language, "r", encoding=my_encoding) as f:
            self._stopwords = [sw.strip() for sw in f.readlines()]
        self._stemmer = SnowballStemmer(language)
        self._stemmed_documents = []
    
    def preprocess_documents(self):
        self._stemmed_documents = [ (self._stemm_tokens(self._remove_stopword(self._tokenize_document(doc[0]))), doc[1] ) for doc in self._documents]
    
    def compute_base_terms(self):
        base_terms = defaultdict(int)
        for doc_stems, _ in self._stemmed_documents:
            for term in set(doc_stems):
                base_terms[term] += 1
        n = len(self._stemmed_documents)
        base_terms = [(bt, math.log( n / df )) for bt, df in base_terms.items()]
        return base_terms
#         return {term for doc in self._stemmed_documents for term in doc[0]}

    def compute_vectors(self, base_terms):
        vectors = []
        for doc_stems, doc_name in self._stemmed_documents:
            vector = [ (doc_stems.count(bt) / len(doc_stems) * idf) for bt, idf in base_terms ]
            vectors.append( (vector, doc_name) )
        return vectors        

    def _tokenize_document(self, document):
        return regexp_tokenize(document, pattern_words)
    
    def _remove_stopword(self, tokens):
        return [token for token in tokens if token not in self._stopwords]
    
    def _stemm_tokens(self, tokens):
        return [self._stemmer.stem(token) for token in tokens]

def filter_base_terms(base_terms, n):
    return sorted(base_terms,  key = lambda x: x[1])[:n]

def save_as_csv(vectors, file_name):
    with codecs.open(file_name, "w", encoding=my_encoding) as out:
        for vector, doc_name in vectors:
            out.write(get_document_class(doc_name) + "," + ",".join(map(str,vector)) + "\n")
    print("Vectors saved to " + file_name)    

def save_as_libsvm(vectors, file_name):
    classes = { clss: str(i)  for i, clss in enumerate(sorted(get_classes(vectors))) }
    print("Class mapping: " + str(classes))
    with codecs.open(file_name, "w", encoding=my_encoding) as out:
        for vector, doc_name in vectors:
            vs = [ str(i+1) + ":" + str(v) for i, v in enumerate(vector) if v > 0]
            out.write(classes[get_document_class(doc_name)] + " " + " ".join(vs) + "\n")
    print("Vectors saved to " + file_name)    


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s',action='store_true', help = "Save filtered base terms to file.")
    parser.add_argument('-n',type=int, help = "Number of most frequent base terms to keep.", default=10)
    parser.add_argument('-b', type=argparse.FileType('r', encoding=my_encoding),  
                        help = "Read a list of base terms from file. Should be in " + my_encoding + ". Options -s and -n ignored.")
    
    parser.add_argument('input_folder', type=str, help = "Corpus input.")
    parser.add_argument('output_folder', type=str, help = "Save to.")
    
    params = parser.parse_args()
    if not os.path.exists(params.output_folder): os.makedirs(params.output_folder)
    
    corpus = StemmedCorpus()
    corpus.load_from_folder(params.input_folder)
    corpus.preprocess_documents()
    
    if params.b:
        columns = [line.strip().split(",", 2) for line in params.b.readlines()[1:]]
        base_terms = [ (bt, float(idf)) for bt, idf in columns ]
        params.b.close()
        print("Base terms read from file: " + str(len(base_terms)))
    else:
        base_terms = corpus.compute_base_terms()
        print("Base terms extracted: " + str(len(base_terms)))
        base_terms = filter_base_terms(base_terms, params.n)
        print("Base terms filtered: " + str(len(base_terms)))
        if params.s:
            with codecs.open("selected_base_terms.txt", "w", encoding=my_encoding) as out:
                out.write("bf,idf\n")
                for bt, idf in base_terms: 
                    out.write("{},{}\n".format(bt, idf))
            print("Base term list saved to selected_base_terms.txt")
#     print(base_terms)
    vectors = corpus.compute_vectors(base_terms)
    save_as_libsvm(vectors, params.output_folder + "vectors_n" + str(len(base_terms)) + ".data")