#!/usr/bin/env python

from urllib2 import urlopen
from lxml.html import parse

"""
Simple download script to download csv files from a webpage
"""

def get_csv_urls(url, prefix=None, file_type='csv'):
    """
    Returns a list of csv links from a page.
    three arguments url, prefix and file_type
    url - to open the page where the csv file links are
    prefix - prefix to add to the links collected in case of relative path names
             default is None
    file_type - file type you want download default is csv
    """
    parsed = parse(urlopen(url))
    doc = parsed.getroot()
    # Grab the links 
    links = doc.findall('.//a')
    # Get all the csv hrefs from the webpage
    csv_hrefs = [ lnk.get('href') for lnk in links if file_type in lnk.get('href')]
    
    if prefix:
        return  [ prefix + href for href in csv_hrefs]
    return csv_hrefs

if __name__ == '__main__':
    url = "http://www.electionresults.govt.nz/electionresults_2014/e9/html/e9_part8_party_index.html"
    prefix = 'http://www.electionresults.govt.nz/electionresults_2014/e9/html/'
    for link in get_csv_urls(url, prefix):
        file_name = link.split("/")[-1]
        csv_file = urlopen(link)
        # Open our file
        with open(file_name, 'w') as f:
            f.write(csv_file.read())
        print(file_name)


