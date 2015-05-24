'''
Created on May 20, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

from urllib.request import urlopen
from urllib.parse import urljoin,urldefrag, urlparse
from urllib.error import HTTPError
from bs4 import BeautifulSoup

import codecs
import time
import re

my_encoding = "utf-8"
should_log = False

class Crawler:
    def __init__(self, u_limit, u_server_lock):
        self._queue = set()
        self._servers = {}
        self._visited = set()
        self._log_extracted_counter = 1
        self._limit = u_limit
        self._server_lock = u_server_lock
        
        self._content_folder = "crawler-content/"
        self._log_visited = codecs.open("crawler-logs/visited.log", "a", encoding=my_encoding)
        self._log_visited.write("id,url,urls-extracted\n")
        self._log_extracted = codecs.open("crawler-logs/extracted.log", "a", encoding=my_encoding)
        self._log_extracted.write("id,url,source-url\n")
    
    def run(self):
        self._print_stat()
        while len(self._visited) < self._limit and len(self._queue) > 0:
            current_url = self._get_from_queue()
            if should_log: print("{},{},".format(len(self._visited), current_url), end="")

            soup = self._openUrl(current_url)
            urls = self._get_urls_from_soup(soup)
            urls = self._canonize_and_filter_links(current_url, urls)
            self.add_to_queue(urls)
            if should_log: print("{}".format(len(urls)))
                
            self._log(current_url, urls)
            self._save_content(soup, current_url, len(self._visited))
            if len(self._visited) % 100 == 0: self._print_stat()
                
        
    def add_to_queue(self, urls):
        self._queue.update(url for url in urls if url not in self._visited)

    def _get_from_queue(self, with_lock=True):
        url = self._queue.pop()
        server = urlparse(url).netloc
        collected = []
        while len(collected) < 100 and server in self._servers and time.time() - self._servers[server] < self._server_lock:
            if should_log: print("Locked: {}, try another".format(server))
            collected.append(url)
            url = self._queue.pop()
            server = urlparse(url).netloc
        self._servers[server] = time.time();
        self._queue.update(collected)
        return url
        
        
    def _print_stat(self):
        print("No_visited: {}, Queue_size: {}".format(len(self._visited), len(self._queue)))    
    
    def _log(self, visited_url, extracted_urls):
        try:
            self._log_visited.write("{},{},{}\n".format(len(self._visited), visited_url, len(extracted_urls)))
            for url in extracted_urls:
                self._log_extracted.write("{},{},{}\n".format(self._log_extracted_counter, url, visited_url))
                self._log_extracted_counter += 1
        except:
            print("Can't log. Problem: " + visited_url)
            
    def _openUrl(self, url):
        self._visited.add(url)
        try:
            with urlopen(url) as d:
                soup = BeautifulSoup(d.read())
            return soup
        except:
            return None

    def _get_urls_from_soup(self, soup):
        return [url.get('href') for url in soup.find_all('a') if url.has_attr('href')] if soup else []

    def _canonize_and_filter_links(self, base, urls):
        return [urljoin(base, urldefrag(url)[0]) for url in urls if not 
                (url.lower().startswith("javascript:") or url.lower().startswith("mailto:"))]
    
    def _save_content(self, soup, url, url_id):
        try:
            str_url = re.sub("\W","_", urlparse(url).netloc + "_" + str(url_id))
            with codecs.open(self._content_folder + str_url, "w", encoding=my_encoding) as f:
                f.write(str(soup))
        except:
            print("Can't save content. Problem: " + url)
    
if __name__ == '__main__':
    start = time.perf_counter()
    crawler = Crawler(3500, 30.0)
    crawler.add_to_queue({"http://en.wikipedia.org/wiki/Elon_Musk"})
    crawler.run()
    end = time.perf_counter()
    print("Elapsed time: " + str(end - start)) 