# NZ-Elections-Data-Cleaning

## Breif Description
These scripts can be used to download and clean New Zealand election results 
data and load them into sqlite. Use the scrape_files.py to download the files
and then the load2sqlite.py to load the files into an sqlite database.

##scrape_files.py

This script is used to download New Zealand election results form the New
Zealand Electrol Commission http://www.elections.org.nz/. A URL of the webpage
or a year of a general election can be entered which will use a predefined URL
for the results. Files are encoded to UTF-8 so they can easily be loaded into
sqlite. 
```
usage: scrape_files.py [-h] [-d DIRECTORY]
                       (-u URL | -y {2014,2011,2008,2005,2002})
                       pattern

positional arguments:
  pattern               Pattern of the files you want to download in quotes
                        uses globbing to select the files to download e.g.
                        '*.csv' will download all the csv files from the
                        webpage.

optional arguments:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        output directory for the files
  -u URL, --url URL     URL of the webpage where the links to the files are
  -y {2014,2011,2008,2005,2002}, --year {2014,2011,2008,2005,2002}
                        Year of general election held will use a predefined
                        URL for the votes at each polling booth.
```

##load2sqlite.py

The script is used to parse and clean csv files from the New Zealand Electoral
Commission so they can be loaded into a table in an sqlite database for use
within a GIS. If the table exits in the sqlite database it will get
overwritten. The -a or --append option can be used to append data to a table.
```
usage: load2sqlite.py [-h] [-a] [-e]
                      {2014,2011,2008,2005,2002} table database
                      [filenames [filenames ...]]

positional arguments:
  {2014,2011,2008,2005,2002}
                        The year of the election for the data. The layout for
                        different years varies.
  table                 output table name for the data
  database              file name of the sqlite database to be used
  filenames             A list of files you want to load into the sqlite
                        database. Wildcards can also be used e.g. *.csv.

optional arguments:
  -h, --help            show this help message and exit
  -a, --append          append data to an existing table
  -e, --by_electorate   Groups the data into electorates
```





