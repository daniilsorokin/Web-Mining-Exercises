'''
Created on May 20, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

from urllib.request import urlopen
from bs4 import BeautifulSoup

class Crawler:
    queue = ["http://en.wikipedia.org/wiki/Elon_Musk"]
    
    def openUrl(self, url):
        with urlopen(url) as d:
            soup = BeautifulSoup(d.read())
#             print(d.read().decode('utf-8'))
            for link in soup.find_all('a'):
                if link.has_attr('href'):
                    print(link.get('href'))

if __name__ == '__main__':
    Crawler().openUrl("http://en.wikipedia.org/wiki/Elon_Musk")