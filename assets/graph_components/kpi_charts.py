import plotly.graph_objects as go
import streamlit as st

def plot_balance_graph(df_monthly):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_monthly["Month"],
        y=df_monthly["Balance"],
        mode='lines+markers',
        name='Remaining Balance',
        line=dict(color="#4CAF50")
    ))

    fig.update_layout(
        title="📉 Mortgage Balance Over Time",
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        font=dict(color="#333"),
        margin=dict(l=40, r=40, t=50, b=40),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_principal_vs_interest(df_monthly):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_monthly["Month"],
        y=df_monthly["Principal"],
        mode='lines',
        name='Principal',
        line=dict(color="#2e8b57")
    ))
    fig.add_trace(go.Scatter(
        x=df_monthly["Month"],
        y=df_monthly["Interest"],
        mode='lines',
        name='Interest',
        line=dict(color="#ff6347")
    ))

    fig.update_layout(
        title="📊 Principal vs. Interest Over Time",
        xaxis_title="Month",
        yaxis_title="Payment Amount ($)",
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        font=dict(color="#333"),
        margin=dict(l=40, r=40, t=50, b=40),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)
