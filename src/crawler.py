'''
Created on May 20, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

from urllib.request import urlopen
from urllib.parse import urljoin,urldefrag

from bs4 import BeautifulSoup

class Crawler:
    def __init__(self, u_limit):
        self._queue = set()
        self._urls_visited = 0
        self._limit = u_limit
    
    def run(self):
        while self._urls_visited < self._limit and len(self._queue) > 0:
            current_url = self._queue.pop()
            soup = self._openUrl(current_url)
            self._urls_visited += 1
            urls = self._get_urls_from_soup(soup)
            urls = self._canonize_links(current_url, urls)
            self.add_to_queue(urls)
            self._log(current_url, urls)
        
    def add_to_queue(self, urls):
        self._queue.update(urls)

    def get_statistics(self):
        return None;
    
    def _log(self, visited_url, extracted_urls):
        print("{}: {} -> {}".format(self._urls_visited, visited_url, len(extracted_urls)))
        
    def _openUrl(self, url):
        with urlopen(url) as d:
            soup = BeautifulSoup(d.read())
        return soup

    def _get_urls_from_soup(self, soup):
        return {url.get('href') for url in soup.find_all('a') if url.has_attr('href')}

    def _canonize_links(self, base, urls):
        return {urljoin(base, urldefrag(url)[0]) for url in urls}
    
if __name__ == '__main__':
    crawler = Crawler(10)
    crawler.add_to_queue({"http://en.wikipedia.org/wiki/Elon_Musk"})
    crawler.run() 