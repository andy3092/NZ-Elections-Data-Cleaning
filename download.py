#!/usr/bin/env python2
import ipdb
import fnmatch
import sys
from urllib2 import urlopen
from lxml.html import parse

"""
Simple download script to download csv files from a webpage
"""

def get_csv_urls(url, prefix=None, filter='*party_[0-9]*.csv'):
    """
    Returns a list of csv links from a page.
    three arguments url, prefix and file_type
    Parameters
    url - to open the page where the csv file links are
    prefix - prefix to add to the links collected in case of relative path names
             default is None
    filter - wildcard for files you want to download e.g. *party_??.csv
    """
    parsed = parse(urlopen(url))
    doc = parsed.getroot()
    # Grab the links 
    links = doc.findall('.//a')
    # Get all the csv hrefs from the webpage
    csv_hrefs = fnmatch.filter([ lnk.get('href') for lnk in links ], filter)

    if prefix:
        return  [ prefix + href for href in csv_hrefs]
    return csv_hrefs

if __name__ == '__main__':
    url = "http://www.electionresults.govt.nz/electionresults_XXXX/e9/html/e9_part8.html"             
    prefix = 'http://www.electionresults.govt.nz/electionresults_XXXX/e9/html/'

    if len(sys.argv) < 2:
        print ("Usage: download.py [2002|2008|2014] {FILES TO DOWNLOAD}")
        sys.exit()
    elif len(sys.argv) == 2:
        year = sys.argv[1]
    else:
        year = sys.argv[1]
        filter = sys.argv[2]

    if year == '2014':
        url = url.replace('e9_part8.html','e9_part8_party_index.html')

    url = url.replace('XXXX', year)
    prefix = prefix.replace('XXXX', year)         
         
    for link in get_csv_urls(url, prefix):
        file_name = link.split("/")[-1]
        csv_file = urlopen(link)
        # Open our file
        with open(file_name, 'w') as f:
            f.write(csv_file.read())
        print(file_name)


