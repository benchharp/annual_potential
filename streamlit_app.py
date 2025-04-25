#!/usr/bin/env python
# coding: utf-8

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

# --- Sidebar: Filter Years and Theme ---
min_year, max_year = df["Year"].min(), df["Year"].max()
year_range = st.slider("Select year range", min_year, max_year, (min_year, max_year))
highlight_years = st.multiselect("Highlight specific years", options=df["Year"].tolist())
chart_type = st.radio("Select Chart Type", ["Stacked Bar", "Line Chart"])
theme = st.selectbox("Select Theme", ["Dark", "Light"])
template = 'plotly_dark' if theme == "Dark" else 'plotly_white'

filtered_df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

# --- Chart Functions ---
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

    for y in highlight_years:
        if y in data["Year"].values:
            fig.add_vline(x=y, line_width=2, line_dash="dash", line_color="gold")

    fig.update_layout(
        title="Growth Potential: Publishers, Studies & Other Memorial Attendees",
        xaxis_title="Year",
        yaxis_title="Millions",
        barmode='stack',
        template=template,
        height=600,
        legend=dict(title='', orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )
    return fig

def plot_line(data):
    fig = go.Figure()
    for col in ["Publishers", "Studies", "Other_Attendees"]:
        fig.add_trace(go.Scatter(x=data["Year"], y=data[col], mode='lines+markers', name=col.replace('_', ' ')))

    fig.update_layout(
        title="Trends Over Time",
        xaxis_title="Year",
        yaxis_title="Millions",
        template=template,
        height=600,
        legend=dict(title='', orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )
    return fig

# --- Table Function ---
def display_table(data):
    display_df = data[["Year", "Publishers", "Studies", "Other_Attendees", "Memorial_Attendance"]].round(1)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[col.replace('_', ' ').title() for col in display_df.columns],
            fill_color='#262730',
            font=dict(color='white', size=18),
            align='center',
            height=35
        ),
        cells=dict(
            values=[display_df[col] for col in display_df.columns],
            fill_color='#1e1e1e',
            font=dict(color='white', size=16),
            align=['left'] + ['center']*4,
            height=32
        )
    )])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig

# --- Download CSV ---
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(filtered_df)
st.download_button("Download data as CSV", csv, "growth_data.csv", "text/csv")

# --- KPI Cards ---
col1, col2, col3 = st.columns(3)
col1.metric("Avg. Publishers", f"{filtered_df['Publishers'].mean():.1f}M")
col2.metric("Avg. Bible Studies", f"{filtered_df['Studies'].mean():.1f}M")
col3.metric("Avg. Memorial Attendance", f"{filtered_df['Memorial_Attendance'].mean():.1f}M")

# --- App Layout ---
st.title("JW Growth Potential Overview")

if chart_type == "Stacked Bar":
    st.plotly_chart(plot_growth(filtered_df), use_container_width=True)
else:
    st.plotly_chart(plot_line(filtered_df), use_container_width=True)

st.subheader("Data Table (Millions)")
st.plotly_chart(display_table(filtered_df), use_container_width=True)

# --- Footer ---
st.sidebar.markdown("Made with ❤️ by [Your Name](https://linkedin.com/in/yourprofile)")


# %%
