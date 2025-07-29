import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mortgage Calculator", layout="centered")
st.title("🏡 Mortgage Calculator with PMI, Affordability, and Payoff Modeling")

st.sidebar.header("Enter Loan Details")
home_price = st.sidebar.number_input("Home Price ($)", min_value=10000, value=300000, step=1000)
down_payment = st.sidebar.number_input("Down Payment ($)", min_value=0, value=60000, step=1000)
loan_term_years = st.sidebar.selectbox("Loan Term (years)", [15, 30], index=1)
interest_rate = st.sidebar.number_input("Interest Rate (%)", min_value=0.0, value=6.5, step=0.1)
property_tax_rate = st.sidebar.number_input("Property Tax Rate (%)", min_value=0.0, value=1.2, step=0.1)
annual_insurance = st.sidebar.number_input("Annual Home Insurance ($)", min_value=0, value=1200, step=100)
monthly_income = st.sidebar.number_input("Monthly Income ($)", min_value=0, value=6000, step=100)
extra_payment_percent = st.sidebar.slider("Extra % of Income Toward Loan Payoff", 0, 50, 10)

if home_price > 0 and down_payment >= 0 and down_payment < home_price and interest_rate > 0 and monthly_income > 0:
  
    loan_amount = home_price - down_payment
    monthly_interest = interest_rate / 100 / 12
    total_months = loan_term_years * 12
    down_payment_percent = (down_payment / home_price) * 100

    if monthly_interest == 0:
        monthly_principal_interest = loan_amount / total_months
    else:
        monthly_principal_interest = (
            loan_amount *
            (monthly_interest * (1 + monthly_interest) ** total_months) /
            ((1 + monthly_interest) ** total_months - 1)
        )

    monthly_property_tax = (home_price * (property_tax_rate / 100)) / 12
    monthly_insurance = annual_insurance / 12
#PMI
    pmi_monthly = 0
    if down_payment_percent < 20:
        pmi_rate = 0.0055 if loan_term_years == 30 else 0.003
        pmi_monthly = (loan_amount * pmi_rate) / 12
      pmi_drops_off = st.sidebar.checkbox("PMI drops off at 20% equity", value=True)


    total_monthly_payment = (
        monthly_principal_interest +
        monthly_property_tax +
        monthly_insurance +
        pmi_monthly
    )

    st.subheader("📊 Monthly Payment Breakdown")
    st.write(f"**Loan Amount:** ${loan_amount:,.2f}")
    st.write(f"**Principal & Interest:** ${monthly_principal_interest:,.2f}")
    st.write(f"**Property Tax:** ${monthly_property_tax:,.2f}")
    st.write(f"**Insurance:** ${monthly_insurance:,.2f}")
    if pmi_monthly > 0:
        st.write(f"**PMI:** ${pmi_monthly:,.2f}")
    st.markdown(f"### 👉 Total Monthly Payment: **${total_monthly_payment:,.2f}**")

    st.subheader("💡 Affordability Check")
    payment_to_income = (total_monthly_payment / monthly_income) * 100
    st.write(f"Your mortgage payment is **{payment_to_income:.2f}%** of your monthly income.")
    if payment_to_income > 36:
        st.error("🚨 Exceeds 36% — risky debt-to-income ratio.")
    elif payment_to_income > 28:
        st.warning("⚠️ Above 28% — higher than recommended for housing.")
    else:
        st.success("✅ Affordable based on income.")

    st.subheader("📋 Monthly Amortization Schedule (with Early Payoff)")

    amortization_rows = []
    balance = loan_amount
    month = 1
    cumulative_interest = 0
    cumulative_principal = 0

    while balance > 0 and month <= 1200:
        interest_payment = balance * monthly_interest
        principal_payment = monthly_principal_interest - interest_payment
        extra_payment = (extra_payment_percent / 100) * monthly_income
        total_principal = principal_payment + extra_payment

        if total_principal > balance:
            total_principal = balance
            principal_payment = balance
            total_payment = balance + interest_payment
        else:
            total_payment = monthly_principal_interest + extra_payment

        balance -= total_principal
        cumulative_interest += interest_payment
        cumulative_principal += total_principal

        amortization_rows.append({
            'Month': month,
            'Payment': round(total_payment, 2),
            'Principal': round(total_principal, 2),
            'Interest': round(interest_payment, 2),
            'Cumulative Principal': round(cumulative_principal, 2),
            'Cumulative Interest': round(cumulative_interest, 2),
            'Balance': round(balance, 2)
        })

        month += 1

    df_monthly = pd.DataFrame(amortization_rows)
    st.dataframe(df_monthly.head(360))

    st.subheader("⏱️ Payoff Summary")
    payoff_months = len(df_monthly)
    payoff_years = payoff_months // 12
    payoff_remainder = payoff_months % 12
    st.success(f"🏁 Paid off in {payoff_years} years and {payoff_remainder} months.")
    st.write(f"💸 Total paid: **${df_monthly['Payment'].sum():,.2f}**")
    st.write(f"📉 Total interest paid: **${df_monthly['Interest'].sum():,.2f}**")

    st.subheader("📈 Balance Timeline")
    st.line_chart(df_monthly.set_index("Month")[["Balance"]])

    st.subheader("📊 Principal vs Interest Over Time")
    st.line_chart(df_monthly.set_index("Month")[["Principal", "Interest"]])

    csv = df_monthly.to_csv(index=False).encode('utf-8')
    st.download_button(
        "💾 Download Full Monthly Amortization CSV",
        data=csv,
        file_name='monthly_amortization.csv',
        mime='text/csv'
    )

else:
    st.warning("Please enter valid values for all fields to calculate your mortgage.")
