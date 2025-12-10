#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explore Page
Visualize individual fruits and their patterns
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import data_api

st.set_page_config(page_title="Explore", layout="wide")

st.title("Explore Fruits")

st.markdown("""
Select one or more fruits to explore their patterns through interactive visualizations.
""")

# Load data
@st.cache_data
def load_data():
    return data_api.load_data()

datasource_df, timeseries_df = load_data()

# ============================================================================
# FRUIT SELECTOR AND SCATTERPLOT
# ============================================================================

st.header("Fruit Positions & Mean Values")

# Create a multiselect widget for choosing fruits
all_fruits = data_api.get_all_fruit_names(datasource_df)

# Add "Select All" option
fruit_options = ["Select All"] + all_fruits

selected_options = st.multiselect(
    "Select fruits to analyze:",
    options=fruit_options,
    default=["Select All"]
)

# Handle "Select All" logic
if "Select All" in selected_options:
    selected_fruits = all_fruits
else:
    selected_fruits = selected_options

if len(selected_fruits) > 0:
    # Filter the datasource dataframe to only show selected fruits
    filtered_datasource = data_api.filter_by_fruit_names(datasource_df, selected_fruits)
    
    # Calculate mean value for each fruit
    mean_values = data_api.calculate_mean_values(timeseries_df)
    filtered_with_means = filtered_datasource.merge(mean_values, on='id', how='left')

    # Defaults to keep variables bound even when we short-circuit
    exclude_zeros = False
    mean_range = (0.0, 0.0)

    if filtered_with_means.empty:
        st.warning("No data available for the selected fruits.")
        filtered_fruit_names = []
    else:
        # Create filter options
        st.subheader("Filters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Filter for non-zero values only
            exclude_zeros = st.checkbox(
                "Exclude fruits with zero values",
                value=False,
                help="Only show fruits that have at least some non-zero data points"
            )
        
        with col2:
            # Get mean value range for the selected fruits
            min_mean = filtered_with_means['mean_value'].min()
            max_mean = filtered_with_means['mean_value'].max()
            
            if pd.isna(min_mean) or pd.isna(max_mean):
                st.warning("Mean values are unavailable for the selected fruits.")
                mean_range = (0.0, 0.0)
            elif min_mean == max_mean:
                st.info(f"Mean value: {min_mean:.2f} (no range to filter)")
                mean_range = (float(min_mean), float(max_mean))
            else:
                # Create a range slider for mean values
                mean_range = st.slider(
                    "Filter by Mean Value Range",
                    min_value=float(min_mean),
                    max_value=float(max_mean),
                    value=(float(min_mean), float(max_mean)),
                    step=float(0.01),
                    help="Select the range of mean values to display"
                )

        # Apply filters
        if exclude_zeros:
            # Get fruits that have non-zero values
            merged_data_temp = data_api.get_timeseries_for_fruits(
                timeseries_df,
                datasource_df,
                selected_fruits
            )
            fruits_with_nonzero = merged_data_temp[merged_data_temp['value'] != 0]['name'].unique().tolist()
            filtered_with_means = filtered_with_means[filtered_with_means['name'].isin(fruits_with_nonzero)]
        
        # Filter by mean value range
        filtered_with_means = filtered_with_means[
            (filtered_with_means['mean_value'] >= mean_range[0]) &
            (filtered_with_means['mean_value'] <= mean_range[1])
        ]
        
        # Display the filtered data
        st.subheader(f"Selected Fruits: {len(filtered_with_means)}")
        st.dataframe(filtered_with_means)
        
        # Create an interactive scatterplot using Plotly
        st.subheader("Scatterplot: X vs Y Coordinates")
        fig = px.scatter(
            filtered_with_means,
            x='x',
            y='y',
            size='mean_value',
            color='name',
            hover_data=['name', 'x', 'y', 'mean_value'],
            title='Fruit Positions (X, Y Coordinates) - Size = Mean Value',
            labels={'x': 'X Coordinate', 'y': 'Y Coordinate', 'mean_value': 'Mean Value'},
            width=800,
            height=600,
            size_max=50
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Get filtered fruit names for time series analysis
        filtered_fruit_names = filtered_with_means['name'].tolist()
    
    # ============================================================================
    # TIME-SERIES VISUALIZATION
    # ============================================================================
    
    st.header("Time-Series Analysis")
    
    if len(filtered_fruit_names) > 0:
        # Get timeseries data for filtered fruits with names merged in
        merged_data = data_api.get_timeseries_for_fruits(
            timeseries_df,
            datasource_df,
            filtered_fruit_names
        )
        
        # Show some stats about the time range
        st.write(f"**Time range:** {merged_data['timestamp'].min()} to {merged_data['timestamp'].max()}")
        st.write(f"**Total data points:** {len(merged_data):,}")
        
        # Create line chart showing values over time
        st.subheader("Value Over Time")
        
        fig_timeseries = px.line(
            merged_data,
            x='timestamp',
            y='value',
            color='name',
            title='Fruit Values Over Time',
            labels={'timestamp': 'Date', 'value': 'Value', 'name': 'Fruit'},
            hover_data=['name', 'value']
        )
        
        fig_timeseries.update_layout(
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig_timeseries, use_container_width=True)
        
        # Show distribution of values
        st.subheader("Value Distribution")
        
        fig_hist = px.histogram(
            merged_data,
            x='value',
            color='name',
            title='Distribution of Values',
            labels={'value': 'Value', 'count': 'Frequency'},
            nbins=50,
            barmode='overlay',
            opacity=0.7
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No fruits match the selected filters.")
else:
    st.warning("Please select at least one fruit to display the chart.")

# ============================================================================
# ZERO-VALUE PATTERN DETECTION
# ============================================================================

st.header("Zero-Value Pattern Detection")

st.markdown("""
Understanding when and how fruits go to zero is critical for prediction.
""")

if len(selected_fruits) > 0:
    # Get all timeseries data for selected fruits
    merged_all = data_api.get_timeseries_for_fruits(
        timeseries_df,
        datasource_df,
        selected_fruits
    )
    
    # Analyze zero patterns
    zero_patterns = data_api.analyze_zero_patterns(merged_all)
    
    st.subheader("Zero Pattern Statistics")
    st.dataframe(zero_patterns)
    
    st.markdown("""
    **What this shows:**
    - **Zero Count**: How many data points are zero
    - **Zero %**: Percentage of all data points that are zero
    - **Zero Sequences**: How many separate sequences of consecutive zeros
    - **Avg Seq Length**: Average length of a zero sequence (in days)
    - **Max Seq Length**: Longest zero sequence observed
    """)
    
    # Visualize zero sequence lengths
    st.subheader("Zero Sequence Patterns")
    
    fig_zero = px.bar(
        zero_patterns,
        x='Fruit',
        y=['Zero Count', 'Zero Sequences'],
        barmode='group',
        title='Zero Occurrences and Sequences per Fruit',
        labels={'value': 'Count', 'variable': 'Metric'}
    )
    st.plotly_chart(fig_zero, use_container_width=True)

else:
    st.info("Select fruits above to see zero-value patterns.")

# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================

st.header("Correlation Analysis")

st.markdown("""
Which fruits move together? Correlation analysis reveals dependencies and relationships.
""")

if len(selected_fruits) > 1:
    # Get all timeseries data
    merged_all = data_api.get_timeseries_for_fruits(
        timeseries_df,
        datasource_df,
        selected_fruits
    )
    
    # Calculate correlation matrix
    corr_matrix = data_api.calculate_correlation_matrix(merged_all)
    
    st.subheader("Correlation Matrix")
    
    st.markdown("""
    **Interpretation:**
    - **+1.0**: Perfect positive correlation (move together)
    - **0.0**: No correlation (independent)
    - **-1.0**: Perfect negative correlation (move oppositely)
    """)
    
    # Display as heatmap using scatter-based approach
    import plotly.graph_objects as go
    
    # Create a simple scatter-based heatmap with clear text
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=corr_matrix.values.round(2),
        texttemplate='%{text:.2f}',
        textfont={"size": 12},
        hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    fig_heatmap.update_layout(
        title='Fruit Correlation Heatmap',
        height=650,
        width=750,
        xaxis={'tickangle': -45},
        yaxis={'autorange': 'reversed'},
        margin={'b': 150}
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.subheader("Correlation Matrix (Table)")
    st.dataframe(corr_matrix.round(3))
    
    # Find strongest correlations
    st.subheader("Strongest Relationships")
    
    # Get upper triangle of correlation matrix (avoid duplicates and self-correlation)
    corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_pairs.append({
                'Fruit 1': corr_matrix.columns[i],
                'Fruit 2': corr_matrix.columns[j],
                'Correlation': corr_matrix.iloc[i, j]
            })
    
    corr_df = pd.DataFrame(corr_pairs).sort_values('Correlation', ascending=False, key=abs)
    
    st.dataframe(corr_df)
    
else:
    st.info("Select at least 2 fruits to see correlation analysis.")
