#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data API Module
Handles all database operations and data processing for the Fruit Analysis Dashboard
"""

import sqlite3
import pandas as pd
import warnings
import numpy as np

# Suppress Prophet and other library warnings
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
except ImportError:
    Prophet = None


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
    connection = sqlite3.connect(db_path)
    
    # Load the datasource table (fruit metadata with x, y coordinates)
    datasource_df = pd.read_sql_query("SELECT * FROM datasource", connection)
    
    # Load the timeseries table (time-series values for each fruit)
    timeseries_df = pd.read_sql_query("SELECT * FROM timeseries", connection)
    
    # Close the connection
    connection.close()

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


def calculate_fruit_statistics(datasource_df, timeseries_df):
    """
    Calculate comprehensive statistics for all fruits.
    
    Args:
        datasource_df (pd.DataFrame): Datasource data with fruit metadata
        timeseries_df (pd.DataFrame): Timeseries data with values
    
    Returns:
        pd.DataFrame: Statistics table with columns:
            - Fruit: Fruit name
            - Total Points: Number of measurements
            - Non-Zero Points: Active measurements
            - Zero %: Percentage of zero values
            - Min Value: Minimum non-zero value
            - Max Value: Maximum non-zero value
            - Mean Value: Average non-zero value
            - Std Dev: Standard deviation of non-zero values
    """
    fruit_stats_list = []
    
    for fruit_id in datasource_df['id'].unique():
        fruit_name = datasource_df[datasource_df['id'] == fruit_id]['name'].values[0]
        fruit_ts = timeseries_df[timeseries_df['datasource_id'] == fruit_id]
        
        total_points = len(fruit_ts)
        zero_count = (fruit_ts['value'] == 0).sum()
        non_zero_count = total_points - zero_count
        
        if non_zero_count > 0:
            non_zero_values = fruit_ts[fruit_ts['value'] > 0]['value']
            min_val = non_zero_values.min()
            max_val = non_zero_values.max()
            mean_val = non_zero_values.mean()
            std_val = non_zero_values.std()
        else:
            min_val = max_val = mean_val = std_val = 0
        
        zero_pct = (zero_count / total_points * 100) if total_points > 0 else 0
        
        fruit_stats_list.append({
            'Fruit': fruit_name,
            'Total Points': total_points,
            'Non-Zero Points': non_zero_count,
            'Zero %': f"{zero_pct:.1f}%",
            'Min Value': f"{min_val:.2f}",
            'Max Value': f"{max_val:.2f}",
            'Mean Value': f"{mean_val:.2f}",
            'Std Dev': f"{std_val:.2f}"
        })
    
    return pd.DataFrame(fruit_stats_list)


def analyze_zero_patterns(timeseries_data):
    """
    Detailed analysis of zero-value patterns for each fruit.
    
    Args:
        timeseries_data (pd.DataFrame): Timeseries data with 'name', 'timestamp', 'value' columns
    
    Returns:
        pd.DataFrame: Detailed zero pattern statistics
    """
    timeseries_data = timeseries_data.sort_values('timestamp')
    
    results = []
    
    for fruit in timeseries_data['name'].unique():
        fruit_data = timeseries_data[timeseries_data['name'] == fruit].sort_values('timestamp')
        
        # Total and zero counts
        total = len(fruit_data)
        zero_count = (fruit_data['value'] == 0).sum()
        
        # Find consecutive zero sequences
        fruit_data_reset = fruit_data.reset_index(drop=True)
        is_zero = (fruit_data_reset['value'] == 0).values
        
        # Detect sequences of zeros
        zero_sequences = []
        in_sequence = False
        seq_start = 0
        
        for idx, val in enumerate(is_zero):
            if val and not in_sequence:
                in_sequence = True
                seq_start = idx
            elif not val and in_sequence:
                in_sequence = False
                zero_sequences.append(idx - seq_start)
        
        if in_sequence:
            zero_sequences.append(len(is_zero) - seq_start)
        
        # Calculate statistics
        avg_sequence_length = sum(zero_sequences) / len(zero_sequences) if zero_sequences else 0
        max_sequence_length = max(zero_sequences) if zero_sequences else 0
        num_sequences = len(zero_sequences)
        
        results.append({
            'Fruit': fruit,
            'Total Points': total,
            'Zero Count': zero_count,
            'Zero %': round(zero_count / total * 100, 2) if total > 0 else 0,
            'Zero Sequences': num_sequences,
            'Avg Seq Length': round(avg_sequence_length, 2),
            'Max Seq Length': max_sequence_length
        })
    
    return pd.DataFrame(results)


def calculate_correlation_matrix(timeseries_data):
    """
    Calculate correlation matrix between fruits based on their values.
    
    Args:
        timeseries_data (pd.DataFrame): Timeseries data with 'name', 'timestamp', 'value' columns
    
    Returns:
        pd.DataFrame: Correlation matrix (fruits x fruits)
    """
    # Pivot to get fruits as columns, timestamps as rows
    pivot_data = timeseries_data.pivot_table(
        index='timestamp',
        columns='name',
        values='value'
    )
    
    # Calculate correlation
    correlation = pivot_data.corr()
    
    return correlation


def validate_forecast_data(timeseries_data, fruit_name):
    """
    Validate data before forecasting to provide clear error messages.
    
    Args:
        timeseries_data (pd.DataFrame): Timeseries data
        fruit_name (str): Fruit name to validate
    
    Returns:
        tuple: (is_valid, error_message, metadata)
            - is_valid (bool): Whether data is valid for forecasting
            - error_message (str): Human-readable error if invalid
            - metadata (dict): Data statistics if valid
    """
    try:
        # Filter data for specific fruit
        fruit_data = timeseries_data[timeseries_data['name'] == fruit_name].copy()
        
        if len(fruit_data) == 0:
            return False, f"No data found for fruit: {fruit_name}", {}
        
        fruit_data = fruit_data.sort_values('timestamp')
        
        # Check total data points
        total_count = len(fruit_data)
        if total_count < 20:
            return False, f"Insufficient data: only {total_count} points (need ≥20)", {}
        
        # Check non-zero data
        non_zero_count = (fruit_data['value'] > 0).sum()
        if non_zero_count == 0:
            return False, f"No non-zero values found. Cannot forecast when fruit is always 0.", {}
        
        if non_zero_count < 10:
            return False, f"Insufficient non-zero data: only {non_zero_count} points (need ≥10)", {}
        
        # Check for NaN values
        nan_count = fruit_data['value'].isna().sum()
        if nan_count == total_count:
            return False, "All values are NaN - cannot forecast", {}
        
        # Check value range
        non_zero_values = fruit_data[fruit_data['value'] > 0]['value']
        min_val = non_zero_values.min()
        max_val = non_zero_values.max()
        
        if min_val == max_val:
            return False, f"All non-zero values are identical ({min_val}). Cannot establish trend.", {}
        
        # Calculate metrics
        zero_pct = (total_count - non_zero_count) / total_count * 100
        date_range = (fruit_data['timestamp'].max() - fruit_data['timestamp'].min()).days
        
        metadata = {
            'total_points': total_count,
            'non_zero_points': non_zero_count,
            'zero_percentage': round(zero_pct, 1),
            'date_range_days': date_range,
            'value_min': round(min_val, 2),
            'value_max': round(max_val, 2),
            'value_mean': round(non_zero_values.mean(), 2)
        }
        
        return True, "", metadata
        
    except Exception as e:
        return False, f"Error validating data: {str(e)}", {}


def forecast_with_prophet(timeseries_data, fruit_name, periods=30):
    """
    Forecast future values for a fruit using Prophet with zero-value handling.
    
    This method handles the categorical nature of the data (0 vs non-zero) by:
    1. Forecasting non-zero values using Prophet on filtered data
    2. Estimating probability of non-zero values (fruit being "active")
    3. Showing THREE scenarios:
       - Pessimistic: mostly zeros (using historical zero probability)
       - Realistic: blend of on/off with trend (weighted by active probability)
       - Optimistic: assuming fruit stays "active"
    
    Args:
        timeseries_data (pd.DataFrame): Timeseries data with 'name', 'timestamp', 'value'
        fruit_name (str): Name of the fruit to forecast
        periods (int): Number of days to forecast
    
    Returns:
        tuple: (forecast_df, model, error_msg) 
            - forecast_df: Forecast dataframe or None if error
            - model: Trained Prophet model or None if error
            - error_msg: Error message if failed, empty string if successful
    """
    error_msg = ""
    
    try:
        from prophet import Prophet
    except ImportError:
        return None, None, "Prophet library not installed"
    
    try:
        # Validate input data first
        is_valid, validation_error, metadata = validate_forecast_data(timeseries_data, fruit_name)
        if not is_valid:
            return None, None, validation_error
        
        # Filter data for specific fruit
        fruit_data = timeseries_data[timeseries_data['name'] == fruit_name].copy()
        fruit_data = fruit_data.sort_values('timestamp')
        
        # Calculate activity probability
        active_count = (fruit_data['value'] > 0).sum()
        total_count = len(fruit_data)
        active_probability = active_count / total_count if total_count > 0 else 0
        
        # Separate zero and non-zero data
        non_zero_data = fruit_data[fruit_data['value'] > 0].copy()
        
        # Prepare data for Prophet
        prophet_data = pd.DataFrame({
            'ds': pd.to_datetime(non_zero_data['timestamp']),
            'y': non_zero_data['value']
        })
        
        # Remove rows with NaN values
        prophet_data = prophet_data.dropna()
        
        if len(prophet_data) < 5:
            return None, None, f"Not enough valid data points after cleaning ({len(prophet_data)} < 5)"
        
        # Initialize and fit Prophet model with error handling
        try:
            model = Prophet(
                yearly_seasonality='auto',
                weekly_seasonality='auto',
                daily_seasonality='auto',
                interval_width=0.95,
                changepoint_prior_scale=0.01,
                seasonality_prior_scale=10.0,
                seasonality_mode='additive'
            )
            
            # Suppress Prophet's verbose output
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model.fit(prophet_data)
                
        except Exception as e:
            return None, None, f"Prophet model training failed: {str(e)}"
        
        # Create future dataframe
        try:
            future = model.make_future_dataframe(periods=periods)
        except Exception as e:
            return None, None, f"Error creating forecast periods: {str(e)}"
        
        # Generate forecast
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                forecast = model.predict(future)
        except Exception as e:
            return None, None, f"Forecast generation failed: {str(e)}"
        
        # Post-process forecast to enforce constraints
        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0)
        forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=0)
        
        # Add activity information and scenarios
        forecast['active_probability'] = active_probability
        forecast['pessimistic'] = forecast['yhat'] * (1 - active_probability)
        forecast['realistic'] = forecast['yhat'] * active_probability
        forecast['optimistic'] = forecast['yhat']
        
        return forecast, model, ""
        
    except Exception as e:
        return None, None, f"Unexpected error during forecasting: {str(e)}"


def get_forecast_summary(forecast_df):
    """
    Extract key statistics from Prophet forecast with scenario analysis.
    
    Args:
        forecast_df (pd.DataFrame): Prophet forecast dataframe with scenarios
    
    Returns:
        dict: Summary statistics including three scenarios and metadata
    """
    if forecast_df is None or len(forecast_df) == 0:
        return {}
    
    # Get only future dates (exclude historical)
    try:
        future_forecast = forecast_df[forecast_df['ds'] > forecast_df['ds'].quantile(0.95)]
        
        if len(future_forecast) == 0:
            future_forecast = forecast_df.tail(7)  # Fallback to last 7 rows
        
        active_prob = future_forecast['active_probability'].iloc[0] if 'active_probability' in future_forecast.columns else 0
        
        return {
            'optimistic_mean': round(future_forecast['optimistic'].mean(), 2) if 'optimistic' in future_forecast.columns else 0,
            'realistic_mean': round(future_forecast['realistic'].mean(), 2) if 'realistic' in future_forecast.columns else 0,
            'pessimistic_mean': round(future_forecast['pessimistic'].mean(), 2) if 'pessimistic' in future_forecast.columns else 0,
            'active_probability': round(active_prob, 3),
            'forecast_range': (round(future_forecast['yhat'].min(), 2), round(future_forecast['yhat'].max(), 2)),
            'trend': 'up' if future_forecast['yhat'].iloc[-1] > future_forecast['yhat'].iloc[0] else 'down'
        }
    except Exception as e:
        return {}


def predict_zero_values(timeseries_data, fruit_name, periods=30):
    """
    Predict which future days a fruit will have zero values using historical patterns.
    
    This uses the historical distribution of active/zero days to estimate probability.
    
    Args:
        timeseries_data (pd.DataFrame): Timeseries data with 'name', 'timestamp', 'value'
        fruit_name (str): Name of the fruit to predict for
        periods (int): Number of days to forecast
    
    Returns:
        tuple: (predictions_df, error_msg)
            - predictions_df: DataFrame with columns [date, zero_probability, status]
                - date: Predicted date
                - zero_probability: % likelihood fruit will be zero (0-100)
                - status: 'Likely Zero' (>60%), 'Likely Active' (<40%), or 'Uncertain' (40-60%)
            - error_msg: Error message if failed, empty string if successful
    """
    try:
        # Filter data for specific fruit
        fruit_data = timeseries_data[timeseries_data['name'] == fruit_name].copy()

        # Control input data
        if len(fruit_data) < 20:
            return None, "Not enough historical data (need ≥20 points)"
        
        fruit_data = fruit_data.sort_values('timestamp')
        
        # Calculate historical zero probability
        total_count = len(fruit_data)
        zero_count = (fruit_data['value'] == 0).sum()
        zero_probability = (zero_count / total_count) if total_count > 0 else 0
        
        # Detect patterns: sequence length of zeros and non-zeros
        is_zero = (fruit_data['value'] == 0).values
        
        # Find sequences and their lengths
        sequences = []
        current_value = is_zero[0]
        current_len = 1
        
        for i in range(1, len(is_zero)):
            if is_zero[i] == current_value:
                current_len += 1
            else:
                sequences.append({'is_zero': current_value, 'length': current_len})
                current_value = is_zero[i]
                current_len = 1
        sequences.append({'is_zero': current_value, 'length': current_len})
        
        # Calculate average sequence length for zeros
        zero_sequences = [s['length'] for s in sequences if s['is_zero']]
        avg_zero_seq_len = sum(zero_sequences) / len(zero_sequences) if zero_sequences else 1
        
        # Generate predictions using a simple probabilistic model
        # Mix historical probability with random variation based on patterns
        predictions_list = []
        last_date = pd.to_datetime(fruit_data['timestamp'].max())
        
        np.random.seed(42)  # For reproducibility
        
        for day_offset in range(1, periods + 1):
            future_date = last_date + pd.Timedelta(days=day_offset)
            
            # Use base probability with small random variation
            # This simulates the uncertainty in predicting zero patterns
            noise = np.random.normal(0, 0.05)  # Small noise around base probability
            predicted_prob = max(0, min(1, zero_probability + noise))
            predicted_prob_pct = predicted_prob * 100
            
            # Categorize prediction
            if predicted_prob_pct > 60:
                status = "Likely Zero"
            elif predicted_prob_pct < 40:
                status = "Likely Active"
            else:
                status = "Uncertain"
            
            predictions_list.append({
                'Date': future_date.strftime('%Y-%m-%d'),
                'Zero Probability': f"{predicted_prob_pct:.1f}%",
                'Status': status
            })
        
        predictions_df = pd.DataFrame(predictions_list)
        
        return predictions_df, ""
        
    except Exception as e:
        return None, f"Error predicting zero values: {str(e)}"

