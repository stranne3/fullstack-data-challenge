#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd

def get_data(DATABASE) -> pd.DataFrame: 
    try:
        conn = sqlite3.connect(DATABASE)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        exit(1)

    conn.row_factory = sqlite3.Row

    query = """
        SELECT d.name, d.x, d.y, t.timestamp, t.value 
        FROM timeseries t
        JOIN datasource d ON t.datasource_id = d.id;
    """

    df = pd.read_sql_query(query, conn, parse_dates=["timestamp"])
    conn.close()

    return df






