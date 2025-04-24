#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go

# Connect to the database
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

# Clean numeric columns
def clean_column(col):
    if col.dtype == object:
        return pd.to_numeric(col.str.replace(',', ''), errors='coerce') / 1_000_000
    else:
        return col / 1_000_000

df["Publishers"] = clean_column(df["Publishers"])
df["Studies"] = clean_column(df["Studies"])
df["Memorial_Attendance"] = clean_column(df["Memorial_Attendance"])
df["Other_Attendees"] = df["Memorial_Attendance"] - df["Publishers"] - df["Studies"]

# Plotting
def plot_growth():
    categories = ["Publishers", "Studies", "Other_Attendees"]
    colors = {
        "Publishers": "#9ccfd8",
        "Studies": "#f6c177",
        "Other_Attendees": "#eb6f92"
    }

    fig = go.Figure()
    bottom = pd.Series([0]*len(df), index=df.index)

    for cat in categories:
        fig.add_trace(go.Bar(
            x=df["Year"],
            y=df[cat],
            name=cat.replace('_', ' '),
            marker_color=colors[cat],
            base=bottom
        ))
        bottom += df[cat]

    fig.update_layout(
        title="Growth Potential: Publishers, Studies & Other Memorial Attendees",
        xaxis_title="Year",
        yaxis_title="Millions",
        barmode='stack',
        template='plotly_dark',
        height=600,
        legend=dict(title='', orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )

    st.plotly_chart(fig, use_container_width=True)

# Render the dashboard
st.title("Growth Potential Overview")
plot_growth()

st.subheader("Data Table")
st.dataframe(df[["Year", "Publishers", "Studies", "Other_Attendees", "Memorial_Attendance"]].round(3))
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Data as CSV", csv, "jw_stats.csv", "text/csv", key='download-csv')
