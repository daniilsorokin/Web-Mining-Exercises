'''
Created on Jun 2, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import codecs, math, argparse, os
from nltk.tokenize import regexp_tokenize
from nltk.stem import SnowballStemmer, WordNetLemmatizer
from nltk.tag import pos_tag
from collections import defaultdict
from compose_corpus import DocumentCorpus, get_document_class, get_classes


pattern_words = "[A-Za-z][\w\-']*"
my_encoding = 'utf-8'

class StemmedCorpus(DocumentCorpus):
    def __init__(self, documents=None, language="german"):
        DocumentCorpus.__init__(self, documents)
        with codecs.open("stopwords/" + language, "r", encoding=my_encoding) as f:
            self._stopwords = [sw.strip() for sw in f.readlines()]
        self._stemmer = SnowballStemmer(language)
        self._lemmatizer = WordNetLemmatizer()
        self._stemmed_documents = []
    
    def preprocess_documents(self, lemmatize=False, remove_stopwords = True):
        _highest_func = self._lemmatize_tokens if lemmatize else self._stemm_tokens
        _second_highest_func = self._remove_stopword if remove_stopwords else lambda x: x
        self._stemmed_documents = [ (_highest_func(_second_highest_func(self._tokenize_document(doc[0].lower()))), doc[1] ) for doc in self._documents]

    def _tokenize_document(self, document):
        return regexp_tokenize(document, pattern_words)
    
    def _remove_stopword(self, tokens):
        return [token for token in tokens if token not in self._stopwords]
    
    def _stemm_tokens(self, tokens):
        return [self._stemmer.stem(token) for token in tokens]

    def _lemmatize_tokens(self, tokens):
        return [self._lemmatizer.lemmatize(token, trans_tag(tag)) for token, tag in pos_tag(tokens)]
    

def get_bigrams(tokens):
    bigrams = []
    for i, token in enumerate(tokens[1:]):
        bigrams.append( tokens[i-1] + "_" + token )
    return bigrams

def trans_tag(tag):
    if tag[0] == 'J': return 'a'
    if tag[0] == 'V': return 'v'
    return 'n'
    
def idf_weight_log(n, df):
    return math.log(1 + (n / (1 + df)) )

def tf_weight_log(ft, dl):
    ft = ft + 1
    return math.log(1 + ft)

def tf_weight_log_norm(ft, dl):
    ft = ft + 1
    return math.log(1 + (ft/ (1 + dl)) )

def mi(bt, p_clss_dict, token_dict, clss_token_dict, clss_n_tokens_dict, n_tokens):
    mi = 0.0
    for clss in p_clss_dict.keys():
        p_clss_token = float ( (clss_token_dict[clss][bt] + 1) / clss_n_tokens_dict[clss])
        p_clss = p_clss_dict[clss]
        p_token = float(token_dict[bt]/n_tokens)
        pmi = p_clss_token * math.log(p_clss_token / (p_clss * p_token))
        mi += pmi
    return mi
    
def compute_base_terms(tokenized_documents):
    bts_df = defaultdict(int)
    bts_f = defaultdict(float)
    bts_clss_f = defaultdict(lambda : defaultdict(int))
    p_clss = defaultdict(float)
    clss_n_t = defaultdict(int)
    tokens_n = 0
    for tokens, doc_name in tokenized_documents:
        clss = get_document_class(doc_name)
        tokens_n += len(tokens)
        clss_n_t[clss] += len(tokens) 
        p_clss[clss] += 1
        for bt in set(tokens):
            bts_df[bt] += 1
            cnt = tokens.count(bt)
            bts_f[bt] += cnt  
            bts_clss_f[clss][bt] += cnt
        bigrams = get_bigrams(tokens)
        for bt in set(bigrams):
            bts_df[bt] += 1
            cnt = bigrams.count(bt)
            bts_f[bt] += cnt  
            bts_clss_f[clss][bt] += cnt
    n = len(tokenized_documents)
    p_clss = {clss: float(cnt/n)  for clss, cnt in p_clss.items()}    
    base_terms = [( bt, idf_weight_log(n, df), mi(bt, p_clss, bts_f, bts_clss_f, clss_n_t, tokens_n) ) for bt, df in bts_df.items()]
    return base_terms

def filter_base_terms(base_terms, n):
    return sorted(base_terms,  key = lambda x: x[1])[:n]

def filter_base_terms_with_mi(base_terms, n, norm_with_idf = False):
    return sorted(base_terms,  key = lambda x: (x[1] * x[2] if norm_with_idf else x[2]), reverse=True)[:n]


def compute_vectors(tokenized_documents, base_terms, tf_weight=tf_weight_log):
    vectors = []
    for tokens, doc_name in tokenized_documents:
        bigrams = get_bigrams(tokens)
        tokens = tokens + bigrams
        vector = [ tf_weight(tokens.count(bt), len(tokens)) * idf for bt, idf, _ in base_terms ]
        vectors.append( (vector, doc_name) )
    return vectors            

def save_as_csv(vectors, file_name, save_names=True):
    with codecs.open(file_name, "w", encoding=my_encoding) as out:
        for vector, doc_name in vectors:
            out.write( (doc_name if save_names else get_document_class(doc_name)) + "," + ",".join(map(str,vector)) + "\n")
    print("Vectors saved to " + file_name)    

def save_as_libsvm(vectors, file_name):
    classes = { clss: str(i)  for i, clss in enumerate(sorted(get_classes(vectors))) }
    print("Class mapping: " + str(classes))
    with codecs.open(file_name, "w", encoding=my_encoding) as out:
        for vector, doc_name in vectors:
            vs = [ str(i+1) + ":" + str(v) for i, v in enumerate(vector) if v > 0]
            out.write(classes[get_document_class(doc_name)] + " " + " ".join(vs) + "\n")
    print("Vectors saved to " + file_name)    

def read_vectors_from_csv(file_name):
    data = []
    with codecs.open(file_name, "r", encoding=my_encoding) as doc_file:
        for line in doc_file.readlines():
            columns = line.split(",")
            doc_name = columns[0]
            vector = [float(el) for el in columns[1:]]
            data.append( (vector, doc_name) )
    return data


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action='store_true', help = "Save filtered base terms to file.")
    parser.add_argument('-l', action='store_true', help = "Normalize frequency values by document length.")
    parser.add_argument('-w', action='store_true', help = "Lemmatize tokens.")
    parser.add_argument('-r', action='store_false', help = "Keep stopwords.")
    parser.add_argument('-n', type=int, help = "Number of base terms to keep.", default=10)
    parser.add_argument('-m', action='store_true', help = "Sort by mutual information, not by frequency.")
    parser.add_argument('-b', type=argparse.FileType('r', encoding=my_encoding),  
                        help = "Read a list of base terms from file. Should be in " + my_encoding + ". Options -s, -m and -n ignored.")
    
    parser.add_argument('input_folder', type=str, help = "Corpus input.")
    parser.add_argument('output_folder', type=str, help = "Save to.")
    
    params = parser.parse_args()
    if not os.path.exists(params.output_folder): os.makedirs(params.output_folder)
    
    corpus = StemmedCorpus(language="english")
    corpus.load_from_folder(params.input_folder)
    corpus.preprocess_documents(lemmatize=params.w, remove_stopwords=params.r)
    
#     with codecs.open("tokens.log", "w", encoding="utf-8") as out:
#         for tokens, doc_name in corpus._stemmed_documents:
#             out.write(str(tokens) + "\n")
    
    if params.b:
        columns = [line.strip().split(",", 2) for line in params.b.readlines()[1:]]
        base_terms = [ (bt, float(idf), float(mi)) for bt, idf, mi in columns ]
        params.b.close()
        print("Base terms read from file: " + str(len(base_terms)))
    else:
        base_terms = compute_base_terms(corpus._stemmed_documents)
        print("Base terms extracted: " + str(len(base_terms)))
        base_terms = filter_base_terms_with_mi(base_terms, params.n)  if params.m else filter_base_terms(base_terms, params.n)
        print("Base terms filtered: " + str(len(base_terms)))
        if params.s:
            base_terms_file_name = "selected_base_terms_n" + str(len(base_terms)) + ("_lemmas" if params.w else "_stems") + ("_wsw" if params.r else "") + ("_mi" if params.m else "_idf") + ".txt"
            with codecs.open(base_terms_file_name, "w", encoding=my_encoding) as out:
                out.write("bf,idf,mi\n")
                for bt, idf, mi in base_terms: 
                    out.write("{},{},{}\n".format(bt, idf, mi))
            print("Base term list saved to " + base_terms_file_name)

    vectors = compute_vectors(corpus._stemmed_documents, base_terms, tf_weight = tf_weight_log_norm if params.l else tf_weight_log)
    save_as_csv(vectors, params.output_folder + corpus._corpus_name +  "_n" + str(len(base_terms)) + ("_lemmas" if params.w else "_stems") + ("_wsw" if params.r else "") + ("_tfnorm" if params.l else "") + ".csv")
    
    
    
    