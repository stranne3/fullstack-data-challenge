#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Oracle Page
Predictions and pattern analysis using machine learning
"""

import streamlit as st
import plotly.graph_objects as go
import data_api

st.set_page_config(page_title="Oracle", layout="wide")

st.title("Oracle - Predictions & Patterns")

st.markdown("""
Use machine learning to forecast future fruit values and uncover hidden patterns.
""")

# Load data
@st.cache_data
def load_data():
    return data_api.load_data()

datasource_df, timeseries_df = load_data()

# ============================================================================
# FORECASTING WITH PROPHET
# ============================================================================

st.header("Time-Series Forecasting")

st.markdown("""
This forecasting model is designed for fruit data where availability is categorical (on/off):

**Three Scenarios:**
- **Optimistic** (green): Fruit stays active the entire forecast period (best case)
- **Realistic** (orange): Blend of on/off based on historical activity rate (expected)
- **Pessimistic** (red): Fruit follows historical on/off pattern (conservative)

**How it works:**
- Estimates the **activity probability** from historical data (% of days fruit is non-zero)
- Forecasts the trend when fruit IS active using only non-zero values
- Multiplies by the activity probability for realistic and pessimistic scenarios

This approach respects the categorical nature of your data and shows a range of likely outcomes.
""")

# Create two columns for fruit selection and forecast parameters
col1, col2, col3 = st.columns(3)

with col1:
    fruit_to_forecast = st.selectbox(
        "Select fruit to forecast:",
        options=data_api.get_all_fruit_names(datasource_df)
    )

with col2:
    forecast_periods = st.slider(
        "Forecast days ahead:",
        min_value=7,
        max_value=90,
        value=30,
        step=7
    )

with col3:
    run_forecast = st.button("Run Forecast", type="primary")

if run_forecast:
    with st.spinner(f"Forecasting {fruit_to_forecast} for {forecast_periods} days..."):
        try:
            # Get timeseries data for the fruit
            fruit_data = data_api.get_timeseries_for_fruits(
                timeseries_df,
                datasource_df,
                [fruit_to_forecast]
            )
            
            if fruit_data is None or len(fruit_data) == 0:
                st.error(f"No data available for {fruit_to_forecast}")
            else:
                # Validate data before forecasting
                is_valid, validation_error, metadata = data_api.validate_forecast_data(
                    fruit_data,
                    fruit_to_forecast
                )
                
                if not is_valid:
                    st.error(f"Cannot forecast {fruit_to_forecast}: {validation_error}")
                    if metadata:
                        st.info("Data Statistics:")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Points", metadata.get('total_points', 'N/A'))
                        with col2:
                            st.metric("Non-Zero Points", metadata.get('non_zero_points', 'N/A'))
                        with col3:
                            st.metric("Zero %", f"{metadata.get('zero_percentage', 0):.1f}%")
                else:
                    # Run forecast
                    forecast_df, model, error_msg = data_api.forecast_with_prophet(
                        fruit_data,
                        fruit_to_forecast,
                        periods=forecast_periods
                    )
                    
                    if forecast_df is not None and error_msg == "":
                        st.success(f"Forecast complete for {fruit_to_forecast}!")
                        
                        # Show data quality info
                        with st.expander("Data Quality", expanded=False):
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Total Points", metadata.get('total_points', 'N/A'))
                            with col2:
                                st.metric("Non-Zero Points", metadata.get('non_zero_points', 'N/A'))
                            with col3:
                                st.metric("Zero %", f"{metadata.get('zero_percentage', 0):.1f}%")
                            with col4:
                                st.metric("Date Range", f"{metadata.get('date_range_days', 0)} days")
                        
                        # Extract historical and forecast data
                        historical_data = fruit_data[fruit_data['name'] == fruit_to_forecast].copy()
                        historical_data = historical_data.sort_values('timestamp')
                        
                        # Create forecast visualization
                        st.subheader(f"Forecast: {fruit_to_forecast}")
                        
                        fig = go.Figure()
                        
                        # Add historical data
                        fig.add_trace(go.Scatter(
                            x=historical_data['timestamp'],
                            y=historical_data['value'],
                            mode='lines',
                            name='Historical',
                            line=dict(color='#1f77b4', width=2)
                        ))
                        
                        # Add forecast
                        forecast_future = forecast_df[forecast_df['ds'] > historical_data['timestamp'].max()]
                        
                        # Add three scenario lines
                        fig.add_trace(go.Scatter(
                            x=forecast_future['ds'],
                            y=forecast_future['optimistic'],
                            mode='lines',
                            name='Optimistic (Stays Active)',
                            line=dict(color='#2ca02c', width=2, dash='solid')
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=forecast_future['ds'],
                            y=forecast_future['realistic'],
                            mode='lines',
                            name='Realistic (Blended)',
                            line=dict(color='#ff7f0e', width=3, dash='solid')
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=forecast_future['ds'],
                            y=forecast_future['pessimistic'],
                            mode='lines',
                            name='Pessimistic (Follows History)',
                            line=dict(color='#d62728', width=2, dash='dash')
                        ))
                        
                        # Add confidence interval for optimistic scenario
                        fig.add_trace(go.Scatter(
                            x=forecast_future['ds'].tolist() + forecast_future['ds'].tolist()[::-1],
                            y=forecast_future['yhat_upper'].tolist() + forecast_future['yhat_lower'].tolist()[::-1],
                            fill='toself',
                            fillcolor='rgba(44, 160, 44, 0.1)',
                            line=dict(color='rgba(255,255,255,0)'),
                            showlegend=True,
                            name='Optimistic Range'
                        ))
                        
                        fig.update_layout(
                            title=f'{fruit_to_forecast} - Historical Data and Forecast',
                            xaxis_title='Date',
                            yaxis_title='Value',
                            hovermode='x unified',
                            height=500,
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show forecast summary
                        st.subheader("Forecast Summary - Three Scenarios")
                        
                        summary = data_api.get_forecast_summary(forecast_df)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                "Optimistic Mean",
                                f"{summary['optimistic_mean']:.2f}",
                                help="If fruit stays active entire period"
                            )
                        
                        with col2:
                            st.metric(
                                "Realistic Mean",
                                f"{summary['realistic_mean']:.2f}",
                                help="Blended with historical activity rate"
                            )
                        
                        with col3:
                            st.metric(
                                "Pessimistic Mean",
                                f"{summary['pessimistic_mean']:.2f}",
                                help="Conservative - follows historical pattern"
                            )
                        
                        with col4:
                            active_pct = summary['active_probability'] * 100
                            st.metric(
                                "Activity Rate",
                                f"{active_pct:.1f}%",
                                help="% of days fruit is active (non-zero)"
                            )
                        
                        # Show forecast table
                        st.subheader("Forecast Details")
                        
                        forecast_table = forecast_future[[
                            'ds', 'optimistic', 'realistic', 'pessimistic'
                        ]].copy()
                        
                        forecast_table.columns = ['Date', 'Optimistic', 'Realistic', 'Pessimistic']
                        forecast_table['Date'] = forecast_table['Date'].dt.strftime('%Y-%m-%d')
                        forecast_table = forecast_table.round(2)
                        
                        st.dataframe(forecast_table, use_container_width=True)
                    else:
                        st.error(f"Forecast failed: {error_msg if error_msg else 'Unknown error'}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.info("Please try again or select a different fruit.")

else:
    st.info("Click 'Run Forecast' to generate predictions for the selected fruit.")
