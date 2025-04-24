#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(page_title="JW Growth Dashboard", layout="wide")

# --- Load and Clean Data ---
db_path = "jw_stats.db"
conn = sqlite3.connect(db_path)

query = """
SELECT 
    year AS Year,
    worldwide_worldwide_memorial_attendance AS Memorial_Attendance,
    average_publishers_preaching_each_month AS Publishers,
    average_bible_studies_each_month AS Studies
FROM yearly_stats;
"""

df = pd.read_sql_query(query, conn)
conn.close()

# Clean and convert columns
def clean_column(col):
    if col.dtype == object:
        return pd.to_numeric(col.str.replace(',', ''), errors='coerce') / 1_000_000
    else:
        return col / 1_000_000

df["Publishers"] = clean_column(df["Publishers"])
df["Studies"] = clean_column(df["Studies"])
df["Memorial_Attendance"] = clean_column(df["Memorial_Attendance"])
df["Other_Attendees"] = df["Memorial_Attendance"] - df["Publishers"] - df["Studies"]
df["Year"] = df["Year"].astype(int)

# --- Sidebar: Filter Years ---
min_year, max_year = df["Year"].min(), df["Year"].max()
year_range = st.slider("Select year range", min_year, max_year, (min_year, max_year))
filtered_df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

# --- Plot Function ---
def plot_growth(data):
    categories = ["Publishers", "Studies", "Other_Attendees"]
    colors = {
        "Publishers": "#9ccfd8",
        "Studies": "#f6c177",
        "Other_Attendees": "#eb6f92"
    }

    fig = go.Figure()
    bottom = pd.Series([0]*len(data), index=data.index)

    for cat in categories:
        fig.add_trace(go.Bar(
            x=data["Year"],
            y=data[cat],
            name=cat.replace('_', ' '),
            marker_color=colors[cat],
            base=bottom
        ))
        bottom += data[cat]

    fig.update_layout(
        title="Growth Potential: Publishers, Studies & Other Memorial Attendees",
        xaxis_title="Year",
        yaxis_title="Millions",
        barmode='stack',
        template='plotly_dark',
        height=600,
        legend=dict(title='', orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )
    return fig

# --- Table Function ---
def display_table(data):
    # Clean header names
    cleaned_headers = [col.replace('_', ' ').title() for col in data.columns]

    display_df = data[["Year", "Publishers", "Studies", "Other_Attendees", "Memorial_Attendance"]].round(1)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(display_df.columns),
            fill_color='#262730',  # darker header background
            font=dict(color='white', size=18, family="Arial", weight="bold"),
            align=['center', 'center', 'center', 'center', 'center'],
            height=35  # row height for header
        ),
        cells=dict(
            values=[display_df[col] for col in display_df.columns],
            fill_color='#1e1e1e',  # match dark mode background
            font=dict(color='white', size=16, family="Arial"),
            align=['center', 'center', 'center', 'center', 'center'],
            height=30  # row height for cells
        )
    )])

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig

# --- App Layout ---
st.title("JW Growth Potential Overview")

# Show Chart
st.plotly_chart(plot_growth(filtered_df), use_container_width=True)

# Show Data Table
st.subheader("Data Table (Millions)")
st.plotly_chart(display_table(filtered_df), use_container_width=True)
