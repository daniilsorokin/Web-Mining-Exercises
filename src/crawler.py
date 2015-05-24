'''
Created on May 20, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

from urllib.request import urlopen
from urllib.parse import urljoin,urldefrag, urlparse

from bs4 import BeautifulSoup
import codecs
from urllib.error import HTTPError

my_encoding = "utf-8"

class Crawler:
    def __init__(self, u_limit):
        self._queue = set()
        self._servers = {}
        self._visited = set()
        self._no_urls_visited = 0
        self._log_extracted_counter = 0
        self._limit = u_limit
        
        self._content_folder = "crawler-content/"
        self._log_visited = codecs.open("crawler-logs/visited.log", "a", encoding=my_encoding)
        self._log_visited.write("id,url,urls-extracted\n")
        self._log_extracted = codecs.open("crawler-logs/extracted.log", "a", encoding=my_encoding)
        self._log_extracted.write("id,url,source-url\n")
    
    def run(self):
        while self._no_urls_visited < self._limit and len(self._queue) > 0:
            current_url = self._queue.pop()
            soup = self._openUrl(current_url)
            self._no_urls_visited += 1
            
            urls = self._get_urls_from_soup(soup)
            urls = self._canonize_links(current_url, urls)
            self.add_to_queue(urls)
            
            self._log(current_url, urls)
            self._save_content(soup, current_url)
        
        # Delete later 
        with codecs.open("crawler-logs/queue.log", "w", encoding=my_encoding) as f:
            for url in self._queue:
                f.write("{}\n".format(url))
        
        
    def add_to_queue(self, urls):
#         for server in [urlparse(url).netloc for url in urls]:
#             if server not in self._servers:
#                 self._servers[server] = None;
        self._queue.update({url for url in urls if url not in self._visited})

    def get_statistics(self):
        return None;
    
    def _log(self, visited_url, extracted_urls):
        print("{},{},{}".format(self._no_urls_visited, visited_url, len(extracted_urls)))
        self._log_visited.write("{},{},{}\n".format(self._no_urls_visited, visited_url, len(extracted_urls)))
        for url in extracted_urls:
            self._log_extracted_counter += 1
            self._log_extracted.write("{},{},{}\n".format(self._log_extracted_counter, url, visited_url))
      
    def _openUrl(self, url):
        self._visited.add(url)
        try:
            with urlopen(url) as d:
                soup = BeautifulSoup(d.read())
            return soup
        except HTTPError:
            return None

    def _get_urls_from_soup(self, soup):
        return [url.get('href') for url in soup.find_all('a') if url.has_attr('href')]

    def _canonize_links(self, base, urls):
        return [urljoin(base, urldefrag(url)[0]) for url in urls]
    
    def _save_content(self, soup, url):
        str_url = "_".join(urlparse(url)).replace("/","_")
        with codecs.open(self._content_folder + str_url, "w", encoding=my_encoding) as f:
            f.write(str(soup))
#         with codecs.open(self._content_folder + "text_"+ str_url, "w", encoding=my_encoding) as f:
#             f.write(soup.get_text())
    
if __name__ == '__main__':
    crawler = Crawler(10)
    crawler.add_to_queue({"http://en.wikipedia.org/wiki/Elon_Musk"})
    crawler.run() 