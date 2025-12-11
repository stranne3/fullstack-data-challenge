#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fullstack Fruit Analysis Dashboard
Main entry point - Home page
"""

import streamlit as st
import pandas as pd

# Import our custom data API module
import data_api

# Set page configuration - this must be the first Streamlit command
st.set_page_config(
    page_title="Fruit Analysis Dashboard",
    layout="wide"  # Uses full width of browser
)

# Title of the app
st.title("Fruit Data Analysis Dashboard")

st.markdown("""
Welcome to the Fruit Analysis Dashboard! This application helps you explore, analyze, and predict fruit value patterns.

### Navigation
Use the sidebar to navigate between pages:
- **Home** (you are here) - Overview and data summary
- **Explore** - Visualize individual fruits and their patterns
- **Compare** - Compare two fruits side-by-side
- **Oracle** - Predict future values and analyze patterns

### Features
- Interactive data visualization
- Filter and explore by fruit
- Compare multiple fruits
- Machine learning predictions
- Zero-value pattern analysis
""")

# Load the data using our API module
@st.cache_data  # This decorator caches the data so we don't reload it every time
def load_data():
    """Wrapper function for caching data from data_api module."""
    return data_api.load_data()

datasource_df, timeseries_df = load_data()

# Display basic information about the data
st.header("Data Overview")

# Create two columns for side-by-side display
col1, col2 = st.columns(2)

with col1:
    st.subheader("Datasource Table")
    st.write(f"**Shape:** {datasource_df.shape[0]} rows × {datasource_df.shape[1]} columns")
    st.write(f"**Fruits in dataset:** {len(datasource_df)}")
    st.dataframe(datasource_df)  # Interactive table

with col2:
    st.subheader("Timeseries Table")
    st.write(f"**Shape:** {timeseries_df.shape[0]} rows × {timeseries_df.shape[1]} columns")
    st.write(f"**Time period:** {timeseries_df['timestamp'].min()} to {timeseries_df['timestamp'].max()}")
    st.dataframe(timeseries_df.head(10))  # Show only first 10 rows

# Show meaningful statistics
st.header("Dataset Statistics")

# Get fruit statistics from API
fruit_stats_df = data_api.calculate_fruit_statistics(datasource_df, timeseries_df)

# Display the statistics table
st.subheader("Fruit Value Statistics")
st.dataframe(fruit_stats_df, use_container_width=True, hide_index=True)

# Display key insights
st.subheader("Key Insights")

col1, col2, col3, col4 = st.columns(4)

with col1:
    most_zeros = fruit_stats_df.loc[
        fruit_stats_df['Zero %'].str.rstrip('%').astype(float).idxmax()
    ]
    st.metric(
        "Most Sparse",
        str(most_zeros['Fruit']),
        str(most_zeros['Zero %']) + " zeros"
    )

with col2:
    least_zeros = fruit_stats_df.loc[
        fruit_stats_df['Zero %'].str.rstrip('%').astype(float).idxmin()
    ]
    st.metric(
        "Most Active",
        str(least_zeros['Fruit']),
        str(least_zeros['Zero %']) + " zeros"
    )

with col3:
    highest_mean = fruit_stats_df.loc[
        fruit_stats_df['Mean Value'].astype(float).idxmax()
    ]
    st.metric(
        "Highest Average Value",
        str(highest_mean['Fruit']),
        str(highest_mean['Mean Value'])
    )

with col4:
    total_data_points = len(timeseries_df)
    st.metric(
        "Total Measurements",
        f"{total_data_points:,}",
        f"from {len(datasource_df)} fruits"
    )
