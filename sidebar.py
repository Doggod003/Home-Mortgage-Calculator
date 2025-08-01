import streamlit as st

def render_sidebar():
    st.sidebar.header("Loan Setup")

    home_price = st.sidebar.number_input("Home Price ($)", min_value=10000, value=300000, step=1000)
    loan_type = st.sidebar.selectbox("Loan Type Preset", ["Conventional (20%)", "FHA (3.5%)", "VA (0%)", "Custom"])

    if loan_type == "Conventional (20%)":
        default_down_percent = 20.0
        default_interest = 6.5
        default_term = 30
    elif loan_type == "FHA (3.5%)":
        default_down_percent = 3.5
        default_interest = 6.0
        default_term = 30
    elif loan_type == "VA (0%)":
        default_down_percent = 0.0
        default_interest = 6.25
        default_term = 30
    else:
        default_down_percent = 10.0
        default_interest = 6.5
        default_term = 30

    down_payment_percent_input = st.sidebar.number_input("Down Payment (% of Home Price)", 0.0, 100.0, value=default_down_percent, step=0.5)
    loan_term_years = st.sidebar.selectbox("Loan Term (years)", [15, 30], index=0 if default_term == 15 else 1)
    interest_rate = st.sidebar.number_input("Interest Rate (%)", min_value=0.0, value=default_interest, step=0.1)
    property_tax_rate = st.sidebar.number_input("Property Tax Rate (%)", min_value=0.0, value=1.2, step=0.1)
    annual_insurance = st.sidebar.number_input("Annual Home Insurance ($)", min_value=0, value=1200, step=100)
    monthly_income = st.sidebar.number_input("Monthly Income ($)", min_value=0, value=6000, step=100)
    extra_payment_percent = st.sidebar.slider("Extra % of Income Toward Loan Payoff", 0, 50, 10)
    pmi_drops_off = st.sidebar.checkbox("PMI drops off at 20% equity", value=True)
    base_hoa = st.sidebar.number_input("Monthly HOA Fee ($)", min_value=0, value=100, step=50)
    base_maint = st.sidebar.number_input("Monthly Maintenance Estimate ($)", min_value=0, value=150, step=50)

    # Button to confirm
    confirmed = st.sidebar.button("✅ Confirm Inputs")
    if confirmed:
        st.session_state.confirmed = True
        st.session_state.inputs = {
            "home_price": home_price,
            "loan_type": loan_type,
            "down_payment_percent": down_payment_percent_input,
            "loan_term_years": loan_term_years,
            "interest_rate": interest_rate,
            "property_tax_rate": property_tax_rate,
            "annual_insurance": annual_insurance,
            "monthly_income": monthly_income,
            "extra_payment_percent": extra_payment_percent,
            "pmi_drops_off": pmi_drops_off,
            "base_hoa": base_hoa,
            "base_maint": base_maint,
        }

    # Reset Button (optional)
    if st.sidebar.button("🔄 Reset Inputs"):
        st.session_state.confirmed = False
        st.experimental_rerun()
