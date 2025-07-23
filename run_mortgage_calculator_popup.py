import streamlit as st
import pandas as pd

# Constants
PMI_RATE_30 = 0.0055
PMI_RATE_15 = 0.003
MAX_AMORTIZATION_MONTHS = 1200

def calculate_monthly_payment(loan_amount: float, interest_rate: float, total_months: int) -> float:
    monthly_interest = interest_rate / 100 / 12
    if monthly_interest == 0:
        return loan_amount / total_months
    return loan_amount * (monthly_interest * (1 + monthly_interest) ** total_months) / \
           ((1 + monthly_interest) ** total_months - 1)

def calculate_pmi(loan_amount: float, down_payment_percent: float, loan_term_years: int) -> float:
    if down_payment_percent < 20:
        pmi_rate = PMI_RATE_30 if loan_term_years == 30 else PMI_RATE_15
        return (loan_amount * pmi_rate) / 12
    return 0

def amortization_schedule(loan_amount: float, monthly_payment: float, monthly_interest: float,
                          extra_payment: float) -> pd.DataFrame:
    balance = loan_amount
    month = 1
    cumulative_interest = 0
    cumulative_principal = 0
    schedule = []

    while balance > 0 and month <= MAX_AMORTIZATION_MONTHS:
        interest_payment = balance * monthly_interest
        principal_payment = monthly_payment - interest_payment
        total_principal = principal_payment + extra_payment
        if total_principal > balance:
            total_principal = balance
            principal_payment = balance
            total_payment = balance + interest_payment
        else:
            total_payment = monthly_payment + extra_payment
        balance -= total_principal
        cumulative_interest += interest_payment
        cumulative_principal += total_principal
        schedule.append({
            'Month': month,
            'Payment': round(total_payment, 2),
            'Principal': round(total_principal, 2),
            'Interest': round(interest_payment, 2),
            'Cumulative Principal': round(cumulative_principal, 2),
            'Cumulative Interest': round(cumulative_interest, 2),
            'Balance': round(balance, 2)
        })
        month += 1
    return pd.DataFrame(schedule)

# Streamlit Inputs and UI remain mostly unchanged, but use functions:
home_price = st.sidebar.number_input("Home Price ($)", min_value=10000, value=300000, step=1000)
down_payment = st.sidebar.number_input("Down Payment ($)", min_value=0, value=60000, step=1000)
loan_term_years = st.sidebar.selectbox("Loan Term (years)", [15, 30], index=1)
interest_rate = st.sidebar.number_input("Interest Rate (%)", min_value=0.0, value=6.5, step=0.1)
property_tax_rate = st.sidebar.number_input("Property Tax Rate (%)", min_value=0.0, value=1.2, step=0.1)
annual_insurance = st.sidebar.number_input("Annual Home Insurance ($)", min_value=0, value=1200, step=100)
monthly_income = st.sidebar.number_input("Monthly Income ($)", min_value=0, value=6000, step=100)
extra_payment_percent = st.sidebar.slider("Extra % of Income Toward Loan Payoff", 0, 50, 10)

# Validation
if home_price > 0 and down_payment >= 0 and down_payment < home_price and interest_rate > 0 and monthly_income > 0:
    loan_amount = home_price - down_payment
    total_months = loan_term_years * 12
    monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, total_months)
    monthly_interest = interest_rate / 100 / 12
    down_payment_percent = (down_payment / home_price) * 100
    monthly_property_tax = (home_price * (property_tax_rate / 100)) / 12
    monthly_insurance = annual_insurance / 12
    pmi_monthly = calculate_pmi(loan_amount, down_payment_percent, loan_term_years)
    total_monthly_payment = monthly_payment + monthly_property_tax + monthly_insurance + pmi_monthly

    # Affordability and schedule
    extra_payment = (extra_payment_percent / 100) * monthly_income
    df_monthly = amortization_schedule(loan_amount, monthly_payment, monthly_interest, extra_payment)

    # Rest of Streamlit UI output...
else:
    st.warning("Please enter valid values for all fields to calculate your mortgage.")
