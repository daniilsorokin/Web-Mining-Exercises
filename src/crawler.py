'''
Created on May 20, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

from urllib.request import urlopen
from urllib.parse import urlparse
# from urllib.error import HTTPError
from bs4 import BeautifulSoup

import mysouputils
from identify_language import LangIdentifier

import codecs,time,re

# Parameters
my_encoding = "utf-8"
should_log = False
data_folder = "crawler-data/"
save_content_to = data_folder + "content/"
save_logs_to = data_folder + "logs/"

class PriorityQueue:
    def __init__(self, sort=False):
        self._l_scores = {}
        self._queue = []
        self._sort = sort
    
    def add_all(self, elements, score=0.0):
        self._l_scores.update([(element, score) for element in elements])
        self._queue = sorted(self._l_scores.keys(), key = lambda x: self._l_scores[x]) if self._sort else set(self._l_scores.keys())
    
    def update(self, tuples):
        self._l_scores.update(tuples)
        self._queue = sorted(self._l_scores.keys(), key = lambda x: self._l_scores[x]) if self._sort else set(self._l_scores.keys())
        
    def pop(self):
        element = self._queue.pop()
        score = self._l_scores[element]
        del self._l_scores[element]
        return (element, score)
    
    def __len__(self):
        return len(self._queue)

class Crawler:
    ''' Main class that runs a crawler. There are only two public methods:
    rub() and add_to_queue(). The latter should be used to add the starting link
    before calling run(). '''
    
    def __init__(self, u_limit, u_server_lock, u_language=None, url_prefix_filter=None):
        self._queue = set()
        self._servers = {}
        self._visited = set()
        self._log_extracted_counter = 1
        self._failed_access_counter = 0
        
        self._limit = u_limit
        self._server_lock = u_server_lock
        if u_language:
            self._lang_focus = u_language
            self._langid = LangIdentifier("lang_id_data/langs/")
            self._queue = PriorityQueue(sort=True)
        else:
            self._lang_focus = None
            self._langid = None
            self._queue = PriorityQueue()
        self._url_prefix_filter = url_prefix_filter
        
        self._content_folder = save_content_to
        self._log_visited = codecs.open(save_logs_to + "visited_links.log", "a", encoding=my_encoding)
        self._log_visited.write("id,url,urls-extracted\n")
        self._log_extracted = codecs.open(save_logs_to + "extracted_links.log", "a", encoding=my_encoding)
        self._log_extracted.write("id,url,source-url\n")
    
    def run(self):
        self._print_stat()
        
        while len(self._visited) < self._limit and len(self._queue) > 0:
            current_url = self._get_from_queue()
            if should_log: print("{},{},".format(len(self._visited), current_url), end="")
            
            soup = self._openUrl(current_url)
            if soup:
                urls = mysouputils.get_urls_from_soup(soup)
                urls = mysouputils.canonize_and_filter_urls(current_url, urls)
                if self._url_prefix_filter: 
                    urls = [url for url in urls if url.startswith(self._url_prefix_filter)]
                if self._lang_focus:
                    l_score = self._langid.get_score(mysouputils.get_content_from_soup(soup), "de")                    
                    self.add_to_queue(urls,l_score) 
                else:
                    self.add_to_queue(urls)
                   
                if should_log: print("{}".format(len(urls)))
                
                self._log(current_url, urls)
                url_id = len(self._visited)
                self._save_content(soup, current_url, url_id)
                
            if len(self._visited) % 100 == 0: self._print_stat()
        
    def add_to_queue(self, urls, score=0.0):
        self._queue.add_all([url for url in urls if url not in self._visited], score)
            

    def _get_from_queue(self):
        url = self._queue.pop()
        server = urlparse(url[0]).netloc
        collected = []
        while len(self._queue) > 0 and len(collected) < 100 and server in self._servers and time.time() - self._servers[server] < self._server_lock:
            if should_log: print("Locked: {}, try another".format(server))
            collected.append(url)
            url = self._queue.pop()
            server = urlparse(url[0]).netloc
        self._servers[server] = time.time();
        self._queue.update(collected)
        return url[0]
        
    def _openUrl(self, url):
        self._visited.add(url)
        try:
            with urlopen(url, timeout=5) as d:
                soup = BeautifulSoup(d.read())
            return soup
        except:
            self._failed_access_counter += 1
            return None

    def _print_stat(self):
        print("No_visited: {}, Queue_size: {}, Failed access: {}".format(len(self._visited), len(self._queue), self._failed_access_counter))    
    
    def _log(self, visited_url, extracted_urls):
        try:
            self._log_visited.write("{},{},{}\n".format(len(self._visited), visited_url, len(extracted_urls)))
            for url in extracted_urls:
                self._log_extracted.write("{},{},{}\n".format(self._log_extracted_counter, url, visited_url))
                self._log_extracted_counter += 1
        except:
            print("Can't log. Problem: " + visited_url)
            
    def _save_content(self, soup, url, url_id, save_text=True):
        try:
            str_url = re.sub("\W","_", urlparse(url).netloc + "_" + str(url_id))
            with codecs.open(self._content_folder + "html/" + str_url, "w", encoding=my_encoding) as f:
                f.write(str(soup))
            if save_text:
                with codecs.open(self._content_folder + "text/" + str_url, "w", encoding=my_encoding) as f:
                    f.write(mysouputils.get_content_from_soup(soup))                
        except:
            print("Can't save content. Problem: " + url)
            
    
if __name__ == '__main__':
    start = time.perf_counter()
    crawler = Crawler(3000, 0.1, url_prefix_filter="http://www.faz.net/aktuell/politik/ausland/")
    crawler.add_to_queue({"http://www.faz.net/"}, 1.0)
    crawler.run()
    end = time.perf_counter()
    print("Elapsed time: " + str(end - start)) 
