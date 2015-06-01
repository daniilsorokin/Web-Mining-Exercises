'''
Created on Jun 1, 2015

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''

from urllib.parse import urljoin,urldefrag

def get_content_from_soup(soup):
    if soup:
        for tag in soup(["script", "style"]):
            tag.extract()
        return soup.get_text()
    else:
        ""   

def get_urls_from_soup(soup):
    return [url.get('href').strip() for url in soup.find_all('a') if url.has_attr('href')] if soup else []

def canonize_and_filter_urls(base, urls, constraints = {"javascript","mailto"}):
    return [urljoin(base, urldefrag(url)[0]) for url in urls  
            if not url.lower().split(":",2)[0] in constraints]

