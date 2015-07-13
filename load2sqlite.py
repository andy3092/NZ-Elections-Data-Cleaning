#!/usr/bin/env python

from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import os
import sqlite3

"""
Script to clean and load election data in an sqlite database
"""


# Constants
# Dictionary for renaming columns for setting up the schemea
HEADER_DICT = {'Unnamed: 0': 'Suburb',
               'Unnamed: 1': 'Voting_Place', 
               'ACT New Zealand': 'ACT',
               'Aotearoa Legalise Cannabis Party': 'ALCP', 
               'Ban1080': 'Ban1080', 
               'Conservative': 'Conservative',
               'Democrats for Social Credit': 'Social_Credit', 
               'Focus New Zealand': 'Focus_NZ', 
               'Green Party': 'Green_Party',
               'Internet MANA': 'Internet_Mana',
               'Labour Party': 'Labour',
               'M\xc4\x81ori Party': 'Maori_Party',
               'National Party': 'National',
               'New Zealand First Party': 'NZ_First',
               'NZ Independent Coalition': 'NZ_Independant',
               'The Civilian Party': 'Civilian_Party',
               'United Future': 'United_Future',
               'Total Valid Party Votes': 'Valid',
               'Informal Party Votes': 'Informal'}

#def load_csv(filename):
#    df = pd.read_csv('csv/e9_part8_party_13.csv', skiprows=2)
    

def load_csv (file_name):
    #file_name = 'csv/e9_part8_party_18.csv'
    # Get the Electorate Number
    electorate_num = int(file_name.split('_')[-1].rstrip('.csv'))

    # Skip first two rows and the last 18 lines of the file
    df = pd.read_csv(file_name, skiprows=2, skipfooter=18)

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

def write_to_sql():
    pass

if __name__ == '__main__':
    dir = 'csv'
    filter = '.csv'
    csv_files = [os.path.join(dir, f) for f in os.listdir(dir) if filter in f]
    appended_data = []
    for csv_file in csv_files:
        data = load_csv(csv_file)
        appended_data.append(data)
    results = pd.concat(appended_data)
        
        
