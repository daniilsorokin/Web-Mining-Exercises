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
import re
from urllib.parse import unquote
from _collections import defaultdict

my_encoding = 'utf-8'

def multi_line_it(long_str):
    i = 0
    return_str = ""
    parts = re.findall("(.+?[_\s]|.+?$)", long_str)
    for part in parts:
        if len(return_str) - i*15 > 15 :
            return_str += "\\n"
            i += 1
        return_str += part
    return return_str
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',type=str, help = "Remove the given prefix from every url.",
                        default=None)  
    parser.add_argument('-f',type=int, help = "Filter out nodes that have fewer than specified outgoing links", default=-1)
    parser.add_argument('-n',type=int, help = "Limit a number of outgoing links per node.", default=-1)
    parser.add_argument('-l',type=int, help = "Limit the final number of nodes.", default=-1)
    parser.add_argument('-a', type=argparse.FileType('r', encoding=my_encoding),  help = "Clustering assignments.")
    parser.add_argument('extracted_links',  type=argparse.FileType('r', encoding=my_encoding), help = "File containing a list of extracted links.")
    parser.add_argument('visited_links', type=argparse.FileType('r', encoding=my_encoding), help = "File containing a list of visited links.")
    params = parser.parse_args()
    
    visited_urls = {unquote(line.strip().split(",")[1]):set() for line in params.visited_links.readlines()[1:]}
    
    for line in params.extracted_links:
        columns = line.strip().split(",")
        extracted_url = unquote(columns[1])
        source_url = unquote(columns[2])
        if not source_url == extracted_url and source_url in visited_urls and extracted_url in visited_urls:
            visited_urls[source_url].add(extracted_url)

    if params.f > 0:
        keys = list(visited_urls.keys())
        for parent in keys:
            if  len(visited_urls[parent]) < params.f:
                del visited_urls[parent]
    
    if params.n > 0:
        for parent in visited_urls.keys():
            if len(visited_urls[parent]) > params.n:
                visited_urls[parent] = random.sample(visited_urls[parent], params.n)
        
    assignment = defaultdict(lambda: "No")   
    color_mapping = {"0":"#006633","1":"#3333CC","2":"#666600","3":"#99CC00","4":"#99CCFF","5":"#CCFF66","6":"#FF3366","7":"#FFCCFF","8":"#FFFFFF","9":"#B0B0B0"}
    if params.a:
        for line in params.a.readlines():
            name, cluster = line.strip().split(",",2)
            assignment[name] = cluster.strip()
        
    
    output_name = os.path.basename(params.visited_links.name) + ".graph"
    with codecs.open(output_name, "w", encoding=my_encoding) as out:    
        items =  random.sample(visited_urls.items(), params.l) if params.l > 0 else visited_urls.items()
        for parent, children in items:
            if params.p: parent = parent.replace(params.p, "")
            parent_with_n = multi_line_it(parent)
            out.write("\"{}\"[ style=filled, fillcolor=\"{}\"]\n".format(parent_with_n, color_mapping[assignment[parent]]))
            for child in children:
                if params.f < 0 or child in visited_urls:
                    if params.p: child = child.replace(params.p, "")
                    child = multi_line_it(child)
                    out.write("\"{}\" -> \"{}\"\n".format(parent_with_n, child))
          
    
