#!/usr/bin/env python2

import os
import sys
import sqlite3
import glob
import argparse

from pandas import DataFrame, Series
import pandas as pd

'''
Pupose:
To clean and load New Zealand election party vote results to an 
sqlite database from a csv files. The script uses the file header_lookup.csv
to rename the party names and will expect to find it in same directory as 
this script. The script only parses the party vote at this stage.
Whould not take too much more effort to do the candidate results for each
electroate. 

usage: load2sqlite.py [-h] [-a] [-e]
                      {2014,2011,2008,2005,2002} table database
                      [filenames [filenames ...]]

Author Andrew Rae
Date August 2015
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

def load_csv (file_name, year, by_electorate=False):
    '''
    Loads and cleans csv files into a pandas data frame
    Ready for writing out to an sqlite database.
    '''
    year_check = ['2002', '2005', '2008']

    skipheader = 2
    special_vote_rows = ('BEFORE|Special Votes|Hospital Votes|'
                         'Votes Allowed|Total$')

    if year == '2014':
        filter = 'Voting places where less than 6 votes were taken'
    else:
        filter = 'Polling places where less than 6 votes were taken'

    #-----------------------------------------------------------------
    # Get the Electorate Number
    #-----------------------------------------------------------------
    electorate_num = int(file_name.split('_')[-1].rstrip('.csv'))

    #-----------------------------------------------------------------
    # Skip first two rows and the last 18 lines of the file
    #-----------------------------------------------------------------
    df = pd.read_csv(file_name, skiprows=skipheader, encoding='UTF-8')

    #-----------------------------------------------------------------
    # Rename the columns
    # Strip out macrons and spaces as these are no good as field names
    #-----------------------------------------------------------------
    df = df.rename(columns=HEADER_DICT)     
    vote_columns = df.columns[2:]

    #-----------------------------------------------------------------
    # drop the row 'Voting places where less than 6 votes were taken'
    #-----------------------------------------------------------------
    df = df[df['Voting_Place'] != filter]

    # The Maori electorates have rows that just have a surburb name in them
    # and null values for the votes will also sort out the footer and 
    # clean that up
    df = df.dropna(thresh=10)
    
    # forward fill the first column 
    # exclude the last rows that refer to special votes as they do not apply
    # note use the - operator to reverse the selection
    
    include_rows = len(df[-df['Voting_Place'].str.contains(
        special_vote_rows)])
    df.loc[:include_rows, 'Suburb'] = df['Suburb'].fillna(method='ffill')

    #-----------------------------------------------------------------
    # Add  a the electrate number
    # and the electorate name to the dataframe
    #-----------------------------------------------------------------
    df['ElectID'] = electorate_num
    elect = df.tail(1).Voting_Place.iloc[0].replace(' Total', '')
    df['Electorate'] = elect
    
    #-----------------------------------------------------------------
    # Reorder the columns so ElecID is the first then Electorate
    #-----------------------------------------------------------------
    cols = df.columns.tolist()
    cols.insert(0, cols.pop())
    cols.insert(0, cols.pop())

    #---------------------------------------------------------------
    # Remove the total from the table
    # Save it first to do a check that all votes tally
    # When returning the results for booths.
    #---------------------------------------------------------------
    total_votes = df.tail(1)
    if by_electorate:
        #total_votes = total_votes.drop('Voting_Place', 1)
        #total_votes = total_votes.drop('Suburb', 1)
        cols.remove('Voting_Place')
        cols.remove('Suburb')
        return total_votes[cols]

    df = df.drop(df.tail(1).index)

    #-----------------------------------------------------------------
    # Do a sanity check test that the votes in the dataframe
    # equal the taotal.
    #----------------------------------------------------------------
    error_msg = "Total does not match: %i %s" % (electorate_num, elect)
    df[vote_columns] = df[vote_columns].astype(int)
    total_votes[vote_columns] = total_votes[vote_columns].astype(int)
    assert(all(total_votes[vote_columns] == 
               df[vote_columns].sum())), error_msg
    
    return df[cols]

def create_table_query(table_name, columns, by_electorate=False):
    '''
    Takes a list of columns of votes adds a primary key.
    Returns an sql query string 
    '''
    if by_electorate:
        suburb_place = ''
    else:
        suburb_place = 'Suburb VARCHAR(50), Voting_Place VARCHAR(255), '

    int_cols = ', '.join([col + ' INTEGER' for col in columns])

    return  ('CREATE TABLE IF NOT EXISTS %s'
    '(ID INTEGER PRIMARY KEY, ElectID INTEGER, Electorate VARCHAR(50), %s'
    '%s);') % (table_name, suburb_place, int_cols)

def create_insert_query(table_name, df):
    '''
    Returns the query string for inserting the data into sqlite
    '''

    columns_to_insert = ','.join(df.columns)
    wildcards = ','.join(['?'] * (len(df.columns)))
    return 'INSERT INTO %s (%s) VALUES (%s);' \
                 % (table_name, columns_to_insert, wildcards)

if __name__ == '__main__':

    # Parse the commandline arguments
    general_description = '''
    The script is used to parse and clean csv files from the New Zealand 
    Electoral Commission so they can be loaded into a table in an sqlite 
    database for use within a GIS. If the table exits in the sqlite
    database it will get overwritten.
    '''
    parser = argparse.ArgumentParser(
        description=general_description)

    year_help = '''The year of the election for the data. 
    The layout for different years varies.'''
    parser.add_argument('year',
                       choices=['2014', '2011', '2008', '2005', '2002'],
                       help=year_help)

    
    parser.add_argument('table',
                        help='output table name for the data')

    parser.add_argument('database',
                         help='file name of the sqlite database to be used')

    filename_help="""A list of files you want to load into
    the sqlite database. Wildcards can also be used e.g. *.csv.
    """
    parser.add_argument('filenames',  
                        help=filename_help,
                        nargs='*')
    
    parser.add_argument('-a', '--append', action='store_true',
                        help='append data to an existing table')

    parser.add_argument('-e', '--by_electorate', action='store_true',
                        help='Groups the data into electorates')

    args = parser.parse_args()
    db = args.database
    table_name = args.table
    csv_files = args.filenames
    append = args.append
    year = args.year
    by_electorate = args.by_electorate

    appended_data = []

    for csv_file in csv_files:
        data = load_csv(csv_file, year, by_electorate)
        appended_data.append(data)

    results = pd.concat(appended_data)

    if by_electorate:
        vote_columns = results.columns[2:]
    else:
        vote_columns = results.columns[4:]

    # Orginally used sqlalchemy but no problems with primary keys
    # Drop the table first if it exists then recreate an empty table.
    with sqlite3.connect(db) as con:
        if not append:
            query = "DROP TABLE IF EXISTS %s;" % (table_name)
            con.execute(query)
            query = create_table_query(table_name, vote_columns, 
                                       by_electorate)
            con.execute(query)
            con.commit()

        # Prepear the data from the dataframe
        output = results.itertuples(index=False)
        data = tuple(output)

        # Write it to the database
        # first need to tinker with the sql query.
        
        con.executemany(create_insert_query(table_name, results), data)
        con.commit()

