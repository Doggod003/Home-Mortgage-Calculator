import streamlit as st
import plotly.graph_objects as go

def draw_balance_chart(filtered_df, key_suffix=""):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_df["Month"],
        y=filtered_df["Balance"],
        mode='lines+markers',
        name='Balance',
        line=dict(color='blue')
    ))
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Balance ($)",
        template="plotly_white",
        legend=dict(x=1.05, y=1),
        margin=dict(r=120)
    )
    st.plotly_chart(fig, use_container_width=True, key=f"balance_chart_{key_suffix}")
