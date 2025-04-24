#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import sqlite3
import plotly.graph_objects as go
import os

notebook_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
db_path = os.path.join(notebook_dir, "..", "..", "jw_stats.db")

# Connect to the database
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


# In[ ]:


# Year range and UI
year_range = [df["Year"].min(), df["Year"].max()]

year_slider = widgets.IntRangeSlider(
    value=year_range,
    min=year_range[0],
    max=year_range[1],
    step=1,
    description='Year Range:',
    continuous_update=False
)

highlight_selector = widgets.SelectMultiple(
    options=sorted(df["Year"].unique()),
    value=(2000, 2024),
    description='Highlight:',
    layout=widgets.Layout(width='50%'),
    style={'description_width': 'initial'}
)

# Plot function
def plot_growth(year_range, highlight_years):
    dff = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
    categories = ["Publishers", "Studies", "Other_Attendees"]
    colors = {
        "Publishers": "#9ccfd8",
        "Studies": "#f6c177",
        "Other_Attendees": "#eb6f92"
    }

    fig = go.Figure()
    bottom = pd.Series([0]*len(dff), index=dff.index)

    for cat in categories:
        fig.add_trace(go.Bar(
            x=dff["Year"],
            y=dff[cat],
            name=cat.replace('_', ' '),
            marker_color=colors[cat],
            offsetgroup=0,
            base=bottom
        ))
        bottom += dff[cat]

    for y in highlight_years:
        if y in dff["Year"].values:
            fig.add_vline(
                x=y,
                line_width=2,
                line_dash="dash",
                line_color="gold",
                annotation_text=f"{y}",
                annotation_position="top left"
            )

    fig.update_layout(
        title="Growth Potential: Publishers, Studies & Other Memorial Attendees",
        xaxis_title="Year",
        yaxis_title="Millions",
        barmode='stack',
        template='plotly_dark',
        height=600,
        legend=dict(title='', orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )
    fig.show()
