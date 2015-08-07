#!/usr/bin/env python2
import argparse
import fnmatch
import os
import sys
import ipdb

from urllib2 import urlopen
from lxml.html import parse

"""
Srapes a url for links to files based on a glob pattern and downloads them.
"""

def get_csv_urls(url, prefix=None, pattern='*party_[0-9]*.csv'):
    """
    Returns a list of csv links from a page.
    three arguments url, prefix and file_type
    Parameters
    url - to open the page where the csv file links are
    prefix - prefix to add to the links collected in case of relative path names
             default is None
    pattern - glob pattern for files you want to download e.g. *party_??.csv
    """
    parsed = parse(urlopen(url))
    doc = parsed.getroot()
    # Grab the links 
    links = doc.findall('.//a')
    # Get all the files based on the glob pattern hrefs from the webpage
    csv_hrefs = fnmatch.filter([ lnk.get('href') for lnk in links ], pattern)

    if prefix:
        return  [ prefix + href for href in csv_hrefs]
    return csv_hrefs

if __name__ == '__main__':
    #url = "http://www.electionresults.govt.nz/electionresults_XXXX/e9/html/e9_part8.html"             

         
    # Parse the commandline arguments
    parser = argparse.ArgumentParser(
        description="For downloading files listed in a webpage")

    parser.add_argument('pattern', type=str,  
                        metavar='pattern of files to download must be in quotes', 
                        action='store')
    parser.add_argument('url', action='store')
    parser.add_argument('-d', '--directory', dest='directory',
                        metavar='output directory', default=os.getcwd())

    args = parser.parse_args()
    print(args.directory)
    print(args.pattern)
    print(args.url)
    #sys.exit()
    prefix = args.url.rstrip(args.url.split("/")[-1])

    for link in get_csv_urls(args.url, prefix):
        file_name = link.split("/")[-1]
        csv_file = urlopen(link)
        # Open our file
        with open(file_name, 'w') as f:
            f.write(csv_file.read())
        print(file_name)


