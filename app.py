import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta


st.set_page_config(page_title="Spending Tracker", layout="wide")


df = pd.read_csv("https://docs.google.com/spreadsheets/d/1-Ga1e6arSzIkzLd0-aMe2o0NPhjVj0xpUCOeoKAO_Qk/export?format=csv")
today_dt = datetime.now()
df["Submission time"] = pd.to_datetime(df["Submission time"]) + pd.Timedelta(hours=7)
df["Date"] = df["Submission time"].dt.date


with st.sidebar:
    st.title("Settings")
    selected = st.pills("Period:", ["Today", "This Week", "This Month"], default="Today")


start_date = today_dt.date()
if selected == "This Week":
    start_date = today_dt.date() - timedelta(days=today_dt.weekday())
elif selected == "This Month":
    start_date = today_dt.date().replace(day=1)

filtered_df = df[df['Submission time'].dt.date >= start_date]
bar_prepare = filtered_df.groupby("Category")["Amounts"].sum().sort_values(ascending=False).reset_index()

daily_spend = df.set_index("Submission time").groupby("Category").resample("D")["Amounts"].sum().reset_index()
daily_spend_table = daily_spend.groupby("Category")["Amounts"].mean().round(2)
daily_food =  daily_spend[daily_spend["Category"]=="Food & Lifestyle"]
daily_food_plot = daily_food.set_index("Submission time")
col_t, col_m = st.columns([2, 1])
with col_t:
    st.title(f"📊 {selected}'s Spending")
with col_m:

    st.metric(label="Total Spend", value=f"{filtered_df['Amounts'].sum():,.0f} THB")

st.divider()

left_chart, right_table = st.columns([1.5, 1]) 

with left_chart:
    # --- Bar Chart (Existing) ---
    fig = px.bar(
        bar_prepare,
        x="Category",
        y="Amounts",
        text_auto='.2s', 
    )
    fig.update_traces(marker_line_color='black', marker_line_width=1)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=False, showticklabels=False, title=""), 
        margin=dict(l=0, r=0, t=30, b=0),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- IMPROVED LINE CHART SECTION ---
    
    # 1. Prepare Data dynamically based on selection
    if selected == "Today":
        # If today, group by Hour
        line_data = filtered_df.set_index("Submission time").resample("h")["Amounts"].sum().reset_index()
        x_axis_title = "Time"
        hover_format = "%H:%M" # Format: 14:00
    else:
        # If Week/Month, group by Date
        line_data = filtered_df.groupby("Date")["Amounts"].sum().reset_index()
        x_axis_title = "Date"
        hover_format = "%d %b" # Format: 10 Feb

    # 2. Create Plotly Area Chart (Looks better than simple line)
    if not line_data.empty:
        fig_line = px.area(
            line_data, 
            x=line_data.columns[0], # Date or Time column
            y="Amounts",
            markers=True,
            title="Spending Trend"
        )
        
        # 3. Style to match your aesthetic
        fig_line.update_traces(
            line_color='#636EFA', # Streamlit Red or pick your own
            marker_line_color='black',
            marker_line_width=1
        )
        fig_line.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(showgrid=False, showticklabels=False, title=""),
            margin=dict(l=0, r=0, t=40, b=0),
            height=300,
            hovermode="x unified" # Shows tooltip nicely
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No spending data for this period to plot.")
with right_table:
    st.markdown("### Category Summary")
    summary = filtered_df.groupby("Category")["Amounts"].agg(["sum", "mean"]).round(0)
    st.dataframe(summary, use_container_width=True)
    st.markdown("### Spending Per Day")
    st.dataframe(daily_spend_table.sort_values(ascending=False),use_container_width=True)
# --- Bottom Section ---
st.markdown("### Transaction History")
st.dataframe(
    df[["Submission time", "Category", "Amounts", "Note"]].tail(10).sort_values("Submission time", ascending=False),
    use_container_width=True,
    hide_index=True
)