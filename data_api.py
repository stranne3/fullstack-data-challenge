#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data API Module
Handles all database operations and data processing for the Fruit Analysis Dashboard
"""

import sqlite3
import pandas as pd


def load_data(db_path="db.sqlite"):
    """
    Connects to SQLite database and loads both tables into pandas DataFrames.
    
    Args:
        db_path (str): Path to the SQLite database file
    
    Returns:
        tuple: (datasource_df, timeseries_df)
            - datasource_df: DataFrame with fruit metadata (id, name, x, y)
            - timeseries_df: DataFrame with time-series data (datasource_id, timestamp, value)
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    
    # Load the datasource table (fruit metadata with x, y coordinates)
    datasource_df = pd.read_sql_query("SELECT * FROM datasource", conn)
    
    # Load the timeseries table (time-series values for each fruit)
    timeseries_df = pd.read_sql_query("SELECT * FROM timeseries", conn)
    
    # Close the connection
    conn.close()
    
    return datasource_df, timeseries_df


def calculate_mean_values(timeseries_df):
    """
    Calculate the mean value for each fruit from timeseries data.
    
    Args:
        timeseries_df (pd.DataFrame): Timeseries data with columns [datasource_id, timestamp, value]
    
    Returns:
        pd.DataFrame: DataFrame with columns [id, mean_value]
    """
    mean_values = timeseries_df.groupby('datasource_id')['value'].mean().reset_index()
    mean_values.columns = ['id', 'mean_value']
    return mean_values


def merge_datasource_with_mean(datasource_df, timeseries_df):
    """
    Merge datasource data with calculated mean values from timeseries.
    
    Args:
        datasource_df (pd.DataFrame): Datasource data
        timeseries_df (pd.DataFrame): Timeseries data
    
    Returns:
        pd.DataFrame: Datasource data with additional 'mean_value' column
    """
    mean_values = calculate_mean_values(timeseries_df)
    return datasource_df.merge(mean_values, on='id', how='left')


def filter_by_fruit_names(datasource_df, fruit_names):
    """
    Filter datasource DataFrame to only include specified fruit names.
    
    Args:
        datasource_df (pd.DataFrame): Full datasource data
        fruit_names (list): List of fruit names to include
    
    Returns:
        pd.DataFrame: Filtered datasource data
    """
    return datasource_df[datasource_df['name'].isin(fruit_names)]


def get_timeseries_for_fruits(timeseries_df, datasource_df, fruit_names):
    """
    Get timeseries data for specific fruits, merged with fruit names.
    
    Args:
        timeseries_df (pd.DataFrame): Full timeseries data
        datasource_df (pd.DataFrame): Datasource data for fruit lookup
        fruit_names (list): List of fruit names to include
    
    Returns:
        pd.DataFrame: Timeseries data with fruit names, filtered to selected fruits
    """
    # Filter datasource to get IDs of selected fruits
    filtered_datasource = filter_by_fruit_names(datasource_df, fruit_names)
    selected_ids = filtered_datasource['id'].tolist()
    
    # Filter timeseries to only include selected fruits
    filtered_timeseries = timeseries_df[timeseries_df['datasource_id'].isin(selected_ids)]
    
    # Merge with datasource to get fruit names
    merged_data = filtered_timeseries.merge(
        datasource_df[['id', 'name']],
        left_on='datasource_id',
        right_on='id'
    )
    
    # Convert timestamp to datetime
    merged_data['timestamp'] = pd.to_datetime(merged_data['timestamp'])
    
    return merged_data


def calculate_zero_statistics(timeseries_data):
    """
    Analyze when values are zero for each fruit.
    
    Args:
        timeseries_data (pd.DataFrame): Timeseries data with 'name' and 'value' columns
    
    Returns:
        pd.DataFrame: Statistics about zero values per fruit
    """
    # Count zeros for each fruit
    zero_counts = timeseries_data[timeseries_data['value'] == 0].groupby('name').size()
    total_counts = timeseries_data.groupby('name').size()
    
    # Calculate percentage of zeros
    zero_percentages = (zero_counts / total_counts * 100).fillna(0)
    
    # Create a dataframe for display
    zero_analysis = pd.DataFrame({
        'Fruit': zero_percentages.index,
        'Zero Count': zero_counts.reindex(zero_percentages.index, fill_value=0),
        'Total Count': total_counts.reindex(zero_percentages.index),
        'Zero Percentage': zero_percentages.round(2).values
    })
    
    return zero_analysis


def get_all_fruit_names(datasource_df):
    """
    Get a list of all fruit names from the datasource.
    
    Args:
        datasource_df (pd.DataFrame): Datasource data
    
    Returns:
        list: List of all fruit names
    """
    return datasource_df['name'].tolist()
