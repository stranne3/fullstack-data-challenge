#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compare Page
Compare two fruits side-by-side
"""

import streamlit as st
import plotly.express as px
import data_api

st.set_page_config(page_title="Compare", layout="wide")

st.title("Compare Two Fruits")

st.markdown("""
Select two different fruits to see a detailed side-by-side comparison.
""")

# Load data
@st.cache_data
def load_data():
    return data_api.load_data()

datasource_df, timeseries_df = load_data()

# Create two columns for selecting two fruits to compare
comp_col1, comp_col2 = st.columns(2)

with comp_col1:
    fruit1 = st.selectbox(
        "Select first fruit:",
        options=data_api.get_all_fruit_names(datasource_df),
        key="fruit1_select"
    )

with comp_col2:
    fruit2 = st.selectbox(
        "Select second fruit:",
        options=data_api.get_all_fruit_names(datasource_df),
        key="fruit2_select"
    )

# Only compare if two different fruits are selected
if fruit1 != fruit2:
    st.subheader(f"Comparing: {fruit1} vs {fruit2}")
    
    # Get timeseries data for both fruits
    comparison_data = data_api.get_timeseries_for_fruits(
        timeseries_df,
        datasource_df,
        [fruit1, fruit2]
    )
    
    # Create side-by-side comparison: line chart
    st.write("**Time-Series Comparison**")
    fig_compare = px.line(
        comparison_data,
        x='timestamp',
        y='value',
        color='name',
        title=f'{fruit1} vs {fruit2} Over Time',
        labels={'timestamp': 'Date', 'value': 'Value'},
        markers=True
    )
    fig_compare.update_layout(hovermode='x unified', height=400)
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # Create comparison stats table
    st.write("**Statistical Comparison**")
    
    comparison_stats = comparison_data.groupby('name')['value'].describe().round(4)
    st.dataframe(comparison_stats)
    
    # Show zero value comparison
    st.write("**Zero Value Comparison**")
    
    zero_comp = data_api.calculate_zero_statistics(comparison_data)
    st.dataframe(zero_comp)
    
    # Create box plot for distribution comparison
    st.write("**Value Distribution Comparison**")
    fig_box = px.box(
        comparison_data,
        x='name',
        y='value',
        title='Value Distribution by Fruit',
        labels={'name': 'Fruit', 'value': 'Value'}
    )
    st.plotly_chart(fig_box, use_container_width=True)
    
else:
    st.warning("Please select two different fruits to compare.")
