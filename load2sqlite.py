#!/usr/bin/env python2

import os
import sys
import sqlite3
import glob
#import ipdb

from pandas import DataFrame, Series
import pandas as pd
#from sqlalchemy import create_engine

'''
Script to clean and load election data to an sqlite database from csv files. 
Takes a dircetory and will process all the csv files in the directory. 
Usage: load2sqlite.py [DIRECTORY] [TABLE NAME] [SQLITE DATABASE] 
       [FILTER](optional)
'''

#-----------------------------------------------------------------
# Constants
# Dictionary is loaded from a csv file this is used 
# for renaming columns and setting up the sqlite schemea
# Macrons and spaces are removed as they are never good as 
# for field names in a database.
# Load the csv as a pandas data frame then convert it to a 
# dictionary to deal with utf-8 encoding 
#-----------------------------------------------------------------
headerdf = pd.read_csv('header_lookup.csv', encoding='UTF-8', 
                       index_col='from_csv')
HEADER_DICT = headerdf.to_dict()['header_name']

def load_csv (file_name):
    '''
    Loads and cleans csv files into a pandas data frame
    Ready for writing out to an sqlite database.
    '''
    #-----------------------------------------------------------------
    # Get the Electorate Number
    #-----------------------------------------------------------------
    electorate_num = int(file_name.split('_')[-1].rstrip('.csv'))

    #-----------------------------------------------------------------
    # Skip first two rows and the last 18 lines of the file
    #-----------------------------------------------------------------
    df = pd.read_csv(file_name, skiprows=2, skipfooter=18, encoding='UTF-8', 
                     engine='python')

    #-----------------------------------------------------------------
    # Rename the columns
    # Strip out macrons and spaces as these are no good as field names
    #-----------------------------------------------------------------
    df = df.rename(columns=HEADER_DICT)     

    #-----------------------------------------------------------------
    # drop the row 'Voting places where less than 6 votes were taken'
    #-----------------------------------------------------------------
    filter = 'Voting places where less than 6 votes were taken'
    df = df[df['Voting_Place'] != filter]

    #-----------------------------------------------------------------
    # Add  a column with the electrate number
    #-----------------------------------------------------------------
    df['ElectID'] = electorate_num     

    # forward fill the first column 
    # exclude the last 5 rows as it does not apply
    last5rows = len(df) - 5
    df.loc[:last5rows, 'Suburb'] = df['Suburb'].fillna(method='ffill')

    # The Maori electorates have rows that just have a surburb name in them
    # and null values for the votes
    df = df.dropna(thresh=10) 

    #-----------------------------------------------------------------
    # Reorder the columns so ElecID is the first coulmn
    #-----------------------------------------------------------------
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    return df[cols]

def create_table_query(table_name, columns):
    '''
    Takes a list of columns of votes adds a primary key.
    Returns an sql query string 
    '''
    int_cols = ', '.join([col + ' INTEGER' for col in columns])

    return  """
    CREATE TABLE IF NOT EXISTS """ + table_name + """
    (ID INTEGER PRIMARY KEY, ElectID INTEGER, Suburb VARCHAR(50), 
    Voting_Place VARCHAR(255), """ + int_cols + """
    );
    """

def create_insert_query(table_name, df):
    '''
    Returns the query string for inserting the data into sqlite
    '''

    columns_to_insert = ','.join(df.columns)
    wildcards = ','.join(['?'] * (len(df.columns)))
    return 'INSERT INTO %s (%s) VALUES (%s);' \
                 % (table_name, columns_to_insert, wildcards)

if __name__ == '__main__':
    # Default variables
    filter = '*.csv'
    db = 'test.sqlite'
    table_name = 'party'
    dir = 'csv'

    if len(sys.argv) < 4:
        print ("Usage: load2sqlite.py [DIRECTORY] [TABLE NAME] [SQLITE DATABASE] [FILTER](optional)")
        sys.exit()
    if len(sys.argv) == 4:
        dir = sys.argv[1]
        table_name = sys.argv[2]
        db = sys.argv[3]
    elif len(sys.argv) > 4:
        dir = sys.argv[1]
        table_name = sys.argv[2]
        db = sys.argv[3]
        filter = sys.argv[4]

    csv_files = glob.glob(os.path.join(dir, filter))
    appended_data = []

    for csv_file in csv_files:
        data = load_csv(csv_file)
        appended_data.append(data)

    results = pd.concat(appended_data)

    # Orginally used sqlalchemy but no problems with primary keys
    with sqlite3.connect(db) as con:
        query = create_table_query(table_name, results.columns[3:])
        con.execute(query)
        con.commit()

        # Prepear the data from the dataframe
        output = results.itertuples(index=False)
        data = tuple(output)

        # Write it to the database
        # Possibly need to check if there is any data in the table
        # first need to tinker with the sql query.
        con.executemany(create_insert_query(table_name, results), data)
        con.commit()

