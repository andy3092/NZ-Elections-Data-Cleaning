#!/usr/bin/env python

from pandas import DataFrame, Series
import pandas as pd
import numpy as np

"""
Script to clean and load election data in an sqlite database
"""

def load_csv(filename):
    df = pd.read_csv('csv/e9_part8_party_13.csv', skiprows=2)
    

if __name__ == '__main__':
    file_name = 'csv/e9_part8_party_1.csv'
    # Get the Electorate Number
    electorate_num = int(file_name.split('_')[-1].rstrip('.csv'))

    # Skip first two rows and the last 18 lines of the file
    df = pd.read_csv(file_name, skiprows=2, skipfooter=18)

    # drop the row 'Voting places where less than 6 votes were taken'
    filter = 'Voting places where less than 6 votes were taken'
    df = df[df['Unnamed: 1'] != filter]
    
    # Add  a column with the electrate number
    df['num'] = electorate_num

    # fill forward and do not include the last 5 rows as it does not apply
    last5rows_index = len(df) - 5
    df.loc[:last5rows_index, 'Unnamed: 0'] = df['Unnamed: 0'].fillna(method='ffill')
    #df['Unnamed: 0'] = df['Unnamed: 0'].fillna(method='ffill')
    #df.loc[last5rows_index:, 'Unnamed: 0'] = np.nan

