import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
df = pd.read_csv("https://docs.google.com/spreadsheets/d/1-Ga1e6arSzIkzLd0-aMe2o0NPhjVj0xpUCOeoKAO_Qk/export?format=csv")
today_dt = datetime.now()
df["Submission time"] = pd.to_datetime(df["Submission time"])
df["MonthYear"] = df["Submission time"].dt.strftime("%b-%Y")
df["Date"] = df["Submission time"].dt.date
bar_plot = df.groupby("Category")["Amounts"].sum()

if 'time_range' not in st.session_state:
    st.session_state.time_range = "Today"
selected = st.session_state.time_range
start_date = today_dt.date()
selected = st.pills("Filter by period:", ["Today", "This Week", "This Month"], default="Today")
if selected == "This Week":
    start_date = today_dt.date() - timedelta(days=today_dt.weekday())
elif selected == "This Month":
    start_date = today_dt.date().replace(day=1)

filtered_df = df[
    (df['Submission time'].dt.date >= start_date)
    ]
bar_prepare = filtered_df.groupby("Category")["Amounts"].sum().sort_values(ascending=False).reset_index()
fig = px.bar(
    bar_prepare,
    x="Category",
    y="Amounts",
    title = f"{selected}'s Spending",
    color="Category",
    text_auto = True
)

st.plotly_chart(fig)

st.divider()
line_chart = filtered_df.set_index("Submission time")["Amounts"]
st.line_chart(line_chart)
st.divider()
executive_summary = filtered_df.groupby("Category").Amounts.sum().sort_values(ascending=False)
st.write(executive_summary)
st.divider()
st.write(df[["Submission time","Category","Amounts","Note"]].tail(5))