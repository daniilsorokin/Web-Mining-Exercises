'''
Created on May 20, 2015

This module implements a simple crawler that can start from a given url and collect all urls 
and linked content iteratively. You have to specify the amount of pages to download. 
Use python3 crawler.py --help for help.
If you want to use it as an API look at the Crawler class.   

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup

import mysouputils
from identify_language import LangIdentifier

import codecs,time,re,argparse,os
import random
from collections import OrderedDict

# Parameters
my_encoding = "utf-8"
should_log = False
data_folder = "crawler-data/"
save_content_to = data_folder + "content/"
save_logs_to = data_folder + "logs/"

class PriorityQueue:
    ''' Describes a queue where elements are sorted according to a score. 
        If sort parameter is set to False the queue functions as a simple Set. 
    '''
    def __init__(self, sort_by_score=False):
        self._l_scores = OrderedDict()
        self._queue = []
        self._sort = sort_by_score
    
    def add_all(self, elements, score=None):
        self._l_scores.update([(element, score) for element in elements])
        self._queue = sorted(self._l_scores.keys(), key = lambda x: self._l_scores[x]) if self._sort else list(self._l_scores.keys())
    
    def update(self, tuples):
        self._l_scores.update(tuples)
        self._queue = sorted(self._l_scores.keys(), key = lambda x: self._l_scores[x]) if self._sort else list(self._l_scores.keys())
        
    def pop(self, rand_item = False):
        element = random.choice(self._queue) if rand_item else self._queue.pop(0)
        score = self._l_scores[element]
        del self._l_scores[element]
        return (element, score)
    
    def __len__(self):
        return len(self._queue)

class Crawler:
    ''' Main class that runs a crawler. There are only two public methods:
    run() and add_to_queue(). The latter should be used to add the starting link
    before calling run(). '''
    
    def __init__(self, server_lock=0.1, language=None):
        self._servers = {}                  # List of servers that where already visited, each mapped to a timestamp of the last visit
        self._visited = set()               # List of visited URLS
        self._log_extracted_counter = 1
        self._failed_access_counter = 0        
        self._server_lock = server_lock
        
        if language:                        # Load language identifier and substitute queue for a priority queue if there is a language given
            self._lang_focus = language
            self._langid = LangIdentifier("lang_id_data/langs/")
            self._queue = PriorityQueue(sort_by_score=True)
        else:
            self._lang_focus = None
            self._langid = None
            self._queue = PriorityQueue()
        
        if not os.path.exists(data_folder): os.makedirs(data_folder)
        if not os.path.exists(save_content_to): os.makedirs(save_content_to)
        if not os.path.exists(save_content_to + "html/"): os.makedirs(save_content_to + "html/")
        if not os.path.exists(save_content_to + "text/"): os.makedirs(save_content_to + "text/")
        if not os.path.exists(save_logs_to): os.makedirs(save_logs_to)

        self._content_folder = save_content_to
        self._log_visited = codecs.open(save_logs_to + "visited_links.log", "a", encoding=my_encoding)
        self._log_visited.write("id,url,urls-extracted\n")
        self._log_extracted = codecs.open(save_logs_to + "extracted_links.log", "a", encoding=my_encoding)
        self._log_extracted.write("id,url,source-url\n")
    
    def run(self, limit, url_prefix_filter=None, url_filters=None, random_item = False):
        self._print_stat()
        
        while len(self._visited) < limit and len(self._queue) > 0:
            current_url = self._get_from_queue(random_item)
            if should_log: print("{},{},".format(len(self._visited), current_url), end="")
            
            soup = self._openUrl(current_url)
            if soup:
                urls = mysouputils.get_urls_from_soup(soup)
                urls = mysouputils.canonize_and_filter_urls(current_url, urls)
                if url_prefix_filter: 
                    urls = [url for url in urls if url.startswith(url_prefix_filter)]
                if url_filters:
                    urls = [url for url in urls if not any(url_filter in urlparse(url).path for url_filter in url_filters)]
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
            

    def _get_from_queue(self, random_item=False):
        url = self._queue.pop(random_item)
        server = urlparse(url[0]).netloc
        collected = []
        while len(self._queue) > 0 and len(collected) < 100 and server in self._servers and time.time() - self._servers[server] < self._server_lock:
            if should_log: print("Locked: {}, try another".format(server))
            collected.append(url)
            url = self._queue.pop(random_item)
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
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-n',type=int, help = "Number of pages to download.", default=3000)
    parser.add_argument('-s',type=float, help = "Access interval to the same server (in sec.).", default=0.1)
    parser.add_argument('-l',type=str, help = "Language to focus on. Web pages in this language will be preferred.",
                        default=None)
    parser.add_argument('-p',type=str, help = "Prefix to filter out urls in the queue. Only urls that start with the given prefix will be considered.",
                        default=None)
    parser.add_argument('-f',type=str, nargs="*", help = "Filter out urls that contain given symbols in the path (not server name).",
                        default=None)
    parser.add_argument('-r',action='store_true', help = "Always choose a random link from the queue, otherwise breadth search.")    
    parser.add_argument('start', type=str, help = "Start url.")
    
    params = parser.parse_args()
    crawler = Crawler(params.s, language=params.l)
    crawler.add_to_queue([params.start], 1.0)
    crawler.run(params.n, params.p, params.f, params.r)
    end = time.perf_counter()
    print("Elapsed time: " + str(end - start)) 
