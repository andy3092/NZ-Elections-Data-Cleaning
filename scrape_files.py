#!/usr/bin/env python2
import argparse
import fnmatch
import os
import sys
#import ipdb

from urllib2 import urlopen
from lxml.html import parse

"""
Srapes a url for links to files based on a glob pattern and downloads them and
encodes them to UTF-8 so they can easily be handled for importing into sqlite.
"""

def get_csv_urls(url, prefix=None, pattern='*party_[0-9]*.csv'):
    """
    Returns a list of csv links from a page.
    three arguments url, prefix and file_type
    Parameters
    url - to open the page where the csv file links are
    year - of general election 2002 2005 2008 2011 2014 
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
         
    # Parse the commandline arguments
    general_description = '''
    The script is used to download New Zealand election results 
    form the New Zealand Electrol Commission http://www.elections.org.nz/.
    A URL of the webpage or a year of a general election
    can be entered which will use a predefined URL for the results.
    Files are encoded to UTF-8 so they can easily be loaded into sqlite
    '''
    parser = argparse.ArgumentParser(
        description=general_description)

    pattern_help="""Pattern of the files you want to download in quotes
    uses globbing to select the files to download e.g. '*.csv' will download 
    all the csv files from the webpage.
    """
    parser.add_argument('pattern', type=str,  
                        help=pattern_help,
                        action='store')
    dir_help = '''Output directory for the downloaded files. 
    Will create the directory if it already does not exist.
    '''
    parser.add_argument('-d', '--directory',
                        help='output directory for the files', 
                        default=os.getcwd())

    group = parser.add_mutually_exclusive_group(required=True)
    url_help = 'URL of the webpage where the links to the files are'
    group.add_argument('-u', '--url', dest='url',
                       help=url_help)
    year_help = '''Year of general election held will use a predefined URL
    for the votes at each polling booth.'''
    group.add_argument('-y', '--year', dest='year',
                       choices=['2014', '2011', '2008', '2005', '2002'],
                       help=year_help)

    args = parser.parse_args()
    #print(args.directory)
    #print(args.pattern)
    #print(args.url)

    if args.directory:
        if not os.path.exists(args.directory):
            os.makedirs(args.directory)

    if args.url:        
        url = args.url

    if args.year:
        if args.year == '2014':
            url = ('http://www.electionresults.govt.nz/'
                   'electionresults_2014/e9/html/e9_part8_party_index.html')
        else:
           url = ('http://www.electionresults.govt.nz/'
                  'electionresults_XXXX/e9/html/e9_part8.html')
           url = url.replace('XXXX', args.year)
    prefix = url.rstrip(url.split("/")[-1])

    for link in get_csv_urls(url, prefix, pattern=args.pattern):
        file_name = link.split("/")[-1]

        # 2002, 2005 are in iso-8859-1 later
        # 2008 uses windows-1252
        # years 2011 and 2014 are in UTF-8. 
        # Set up the encoding for reading and writing
        year_check = ['results_2005', 'results_2002']

        if any(x in url for x in year_check):
            source_encoding = 'iso-8859-1'
        elif 'results_2008' in url:
            source_encoding = 'windows-1252'
        else:
            source_encoding = 'UTF-8'
        target_encoding = 'UTF-8'
        
        # Check if the file exists and if not open the url and write the file 
        file_name = os.path.join(args.directory, file_name)
        if not os.path.isfile(file_name):
            csv_file = urlopen(link)
            with open(file_name, 'wb') as f:
                f.write(unicode(csv_file.read(), source_encoding).encode(
                    target_encoding))
                print(file_name)
        else:
            print("%s file exists not downloading file." % (file_name))


