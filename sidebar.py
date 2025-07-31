# sidebar.py
import streamlit as st

def mortgage_sidebar():
    st.markdown("## 🔧 Loan Inputs")

    home_price_input = st.number_input("Home Price", value=300000, key="sidebar_home_price")
    down_payment_input = st.number_input("Down Payment", value=60000, key="sidebar_down_payment")
    interest_rate_input = st.number_input("Interest Rate (%)", value=6.5, key="sidebar_interest_rate")
    loan_term_input = st.selectbox("Loan Term (years)", [15, 30], index=1, key="sidebar_loan_term")

    if st.button("💾 Update Mortgage", key="sidebar_update_btn"):
        st.session_state["home_price"] = home_price_input
        st.session_state["down_payment"] = down_payment_input
        st.session_state["interest_rate"] = interest_rate_input
        st.session_state["loan_term"] = loan_term_input
        st.experimental_rerun()
