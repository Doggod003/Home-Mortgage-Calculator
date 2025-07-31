import streamlit as st

def mortgage_sidebar():
    st.markdown("## 🔧 Loan Inputs")

    home_price_input = st.number_input("Home Price", value=300000)
    down_payment_input = st.number_input("Down Payment", value=60000)
    interest_rate_input = st.number_input("Interest Rate (%)", value=6.5)
    loan_term_input = st.selectbox("Loan Term (years)", [15, 30], index=1)

    # Apply inputs only on button click
    if st.button("💾 Update Mortgage"):
        st.session_state["home_price"] = home_price_input
        st.session_state["down_payment"] = down_payment_input
        st.session_state["interest_rate"] = interest_rate_input
        st.session_state["loan_term"] = loan_term_input
        st.experimental_rerun()
