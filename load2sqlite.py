#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
import sqlite3

"""
Script to clean and load election data in an sqlite database
"""


# Constants
# Dictionary for renaming columns for setting up the schemea
HEADER_DICT = {u'Unnamed: 0': u'Suburb',
               u'Unnamed: 1': u'Voting_Place', 
               u'ACT New Zealand': u'ACT',
               u'Aotearoa Legalise Cannabis Party': u'ALCP', 
               u'Ban1080': u'Ban1080', 
               u'Conservative': u'Conservative',
               u'Democrats for Social Credit': u'Social_Credit', 
               u'Focus New Zealand': u'Focus_NZ', 
               u'Green Party': u'Green_Party',
               u'Internet MANA': u'Internet_Mana',
               u'Labour Party': u'Labour',
               #u'M\xc4\x81ori Party': u'Maori_Party',
               u'Māori Party': u'Maori_Party',
               u'National Party': u'National',
               u'New Zealand First Party': u'NZ_First',
               u'NZ Independent Coalition': u'NZ_Independant',
               u'The Civilian Party': u'Civilian_Party',
               u'United Future': u'United_Future',
               u'Total Valid Party Votes': u'Valid',
               u'Informal Party Votes': u'Informal'}

#def load_csv(filename):
#    df = pd.read_csv('csv/e9_part8_party_13.csv', skiprows=2)
    

def changeencode(data, cols):
    '''
    Small function to encode Unicode caracters. 
    '''
    for col in cols:
        data[col] = data[col].str.encode('utf-8')
    return data 

def load_csv (file_name):
    #file_name = 'csv/e9_part8_party_18.csv'
    # Get the Electorate Number
    electorate_num = int(file_name.split('_')[-1].rstrip('.csv'))

    # Skip first two rows and the last 18 lines of the file
    df = pd.read_csv(file_name, skiprows=2, skipfooter=18, encoding='UTF-8')

    # Rename the columns with the HEADER_DICT
    # Clean out any macrons
    df = df.rename(columns=HEADER_DICT)

    # drop the row 'Voting places where less than 6 votes were taken'
    filter = 'Voting places where less than 6 votes were taken'
    df = df[df['Voting_Place'] != filter]
    
    # Add  a column with the electrate number
    df['ElectID'] = electorate_num

    # forward fill the first column 
    # exclude the last 5 rows as it does not apply
    last5rows = len(df) - 5
    df.loc[:last5rows, 'Suburb'] = df['Suburb'].fillna(method='ffill')

    # Reoder the columns so ElecID is the first coulmn
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    return df[cols]

def create_party_table(con, table_name, columns):
    '''
    Takes a list of parties and 
    creates an sql table
    returns a connection to the table.
    '''
    int_cols = ', '.join([col + ' INTEGER' for col in columns])

    query = """
    CREATE TABLE IF NOT EXISTS """ + table_name + """
    (ID INTEGER, ElectID INTEGER, Suburb VARCHAR(50), 
    Voting_Place VARCHAR(255), """ + int_cols + """
    );
    """
    con.execute(query)
    con.commit()

def write_to_sql(con, table_name, df):
    output = df.itertuples()
    data = tuple(output)
    wildcards = ','.join(['?'] * (len(df.columns) + 1))
    insert_sql = 'INSERT INTO %s VALUES (%s)' % (table_name, wildcards)
    con.executemany(insert_sql, data)
    con.commit()

if __name__ == '__main__':
    dir = 'csv'
    filter = '.csv'
    csv_files = [os.path.join(dir, f) for f in os.listdir(dir) if filter in f]
    appended_data = []
    for csv_file in csv_files:
        data = load_csv(csv_file)
        appended_data.append(data)
    results = pd.concat(appended_data)
    
    engine = create_engine('sqlite:///my_db.sqlite')
    results.to_sql('party', engine, if_exists='replace', index_label='id')
    engine.dispose() # do not want to rely on the garbage disposal.

    
        
