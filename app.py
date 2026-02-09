import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# --- Config ---
st.set_page_config(page_title="Spending Tracker", layout="wide")

# --- Data Loading (เหมือนเดิม) ---
df = pd.read_csv("https://docs.google.com/spreadsheets/d/1-Ga1e6arSzIkzLd0-aMe2o0NPhjVj0xpUCOeoKAO_Qk/export?format=csv")
today_dt = datetime.now()
df["Submission time"] = pd.to_datetime(df["Submission time"]) + pd.Timedelta(hours=7)
df["Date"] = df["Submission time"].dt.date

# --- Sidebar / Filter ---
with st.sidebar:
    st.title("Settings")
    selected = st.pills("Period:", ["Today", "This Week", "This Month"], default="Today")

# --- Filter Logic ---
start_date = today_dt.date()
if selected == "This Week":
    start_date = today_dt.date() - timedelta(days=today_dt.weekday())
elif selected == "This Month":
    start_date = today_dt.date().replace(day=1)

filtered_df = df[df['Submission time'].dt.date >= start_date]
bar_prepare = filtered_df.groupby("Category")["Amounts"].sum().sort_values(ascending=False).reset_index()

# --- Header Section ---
col_t, col_m = st.columns([2, 1])
with col_t:
    st.title(f"📊 {selected}'s Spending")
with col_m:
    # แสดงตัวเลขรวมแบบตัวหนาและใหญ่
    st.metric(label="Total Spend", value=f"{filtered_df['Amounts'].sum():,.0f} THB")

st.divider()

# --- Main Dashboard Layout ---
left_chart, right_table = st.columns([1.5, 1]) # แบ่งฝั่งกราฟกับตาราง Summary

with left_chart:
    # ปรับแต่ง Fig ให้มินิมอล
    fig = px.bar(
        bar_prepare,
        x="Category",
        y="Amounts",
        text_auto='.2s', # ย่อหลักพันเป็น k ให้ดูสะอาด
    )
    
    fig.update_traces(
        marker_color='whitesmoke', # สีขาวนวล
        marker_line_color='black',
        marker_line_width=1,
        textposition='outside'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', # พื้นหลังใส
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=False, showticklabels=False, title=""), # ซ่อนแกน Y เพราะมีเลขบนแท่งแล้ว
        margin=dict(l=0, r=0, t=30, b=0),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

with right_table:
    st.markdown("### Category Summary")
    summary = filtered_df.groupby("Category")["Amounts"].agg(["sum", "mean"]).round(0)
    st.dataframe(summary, use_container_width=True) # ใช้ dataframe แทน table จะสวยและ scroll ได้

# --- Bottom Section ---
st.markdown("### Transaction History")
# ใช้ st.dataframe แทน st.table เพื่อความสวยงามและ Sort ได้
st.dataframe(
    df[["Submission time", "Category", "Amounts", "Note"]].tail(10).sort_values("Submission time", ascending=False),
    use_container_width=True,
    hide_index=True
)