'''
Created on July 04, 2015

This script reads log files that are produce by the Crawler script and produces 
a directed URL links graph for downloaded pages.

@author: Daniil Sorokin<sorokin@ukp.informatik.tu-darmstadt.de>
'''
import argparse
import codecs
import os
import random
from urllib.parse import unquote

my_encoding = 'utf-8'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',type=str, help = "Remove the given prefix from every url.",
                        default=None)  
    parser.add_argument('-n',type=int, help = "Limit a number of outgoing links per node.", default=-1)
    parser.add_argument('extracted_links',  type=argparse.FileType('r', encoding=my_encoding), help = "File containing a list of extracted links.")
    parser.add_argument('visited_links', type=argparse.FileType('r', encoding=my_encoding), help = "File containing a list of visited links.")
    params = parser.parse_args()
    
    visited_urls = {unquote(line.strip().split(",")[1]):set() for line in params.visited_links}
    
    for line in params.extracted_links:
        columns = line.strip().split(",")
        extracted_url = unquote(columns[1])
        source_url = unquote(columns[2])
        if not source_url == extracted_url and source_url in visited_urls and extracted_url in visited_urls:
            visited_urls[source_url].add(extracted_url)
    
    if params.n > 0:
        for parent in visited_urls.keys():
            if params.n < len(visited_urls[parent]):
                visited_urls[parent] = random.sample(visited_urls[parent], params.n)
    
    output_name = os.path.basename(params.visited_links.name) + ".graph"
    with codecs.open(output_name, "w", encoding=my_encoding) as out:    
        for parent, children in visited_urls.items():
            if params.p: parent = parent.replace(params.p, "")
            for child in children:
                if params.p: child = child.replace(params.p, "")
                out.write("\"{}\" -> \"{}\"\n".format(parent, child))
          
    
