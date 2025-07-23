import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mortgage Calculator", layout="centered")
st.title("🏡 Mortgage Calculator with PMI")

# Sidebar Inputs
st.sidebar.header("Enter Loan Details")

home_price = st.sidebar.number_input("Home Price ($)", min_value=10000, value=300000, step=1000)
down_payment = st.sidebar.number_input("Down Payment ($)", min_value=0, value=60000, step=1000)
loan_term_years = st.sidebar.selectbox("Loan Term (years)", [15, 30], index=1)
interest_rate = st.sidebar.number_input("Interest Rate (%)", min_value=0.0, value=6.5, step=0.1)
property_tax_rate = st.sidebar.number_input("Property Tax Rate (%)", min_value=0.0, value=1.2, step=0.1)
annual_insurance = st.sidebar.number_input("Annual Home Insurance ($)", min_value=0, value=1200, step=100)

# Only calculate when inputs are valid
if home_price > 0 and down_payment >= 0 and down_payment < home_price and interest_rate > 0:
    loan_amount = home_price - down_payment
    monthly_interest = interest_rate / 100 / 12
    total_months = loan_term_years * 12
    down_payment_percent = (down_payment / home_price) * 100

    # Monthly Principal & Interest
    if monthly_interest == 0:
        monthly_principal_interest = loan_amount / total_months
    else:
        monthly_principal_interest = (
            loan_amount * (monthly_interest * (1 + monthly_interest) ** total_months)
            / ((1 + monthly_interest) ** total_months - 1)
        )

    monthly_property_tax = (home_price * (property_tax_rate / 100)) / 12
    monthly_insurance = annual_insurance / 12

    # PMI
    pmi_monthly = 0
    if down_payment_percent < 20:
        pmi_rate = 0.0055 if loan_term_years == 30 else 0.003
        pmi_monthly = (loan_amount * pmi_rate) / 12

    # Total Monthly Payment
    total_monthly_payment = (
        monthly_principal_interest
        + monthly_property_tax
        + monthly_insurance
        + pmi_monthly
    )

    # Display breakdown
    st.subheader("📊 Monthly Payment Breakdown")
    st.write(f"**Loan Amount:** ${loan_amount:,.2f}")
    st.write(f"**Principal & Interest:** ${monthly_principal_interest:,.2f}")
    st.write(f"**Property Tax:** ${monthly_property_tax:,.2f}")
    st.write(f"**Insurance:** ${monthly_insurance:,.2f}")
    st.write(f"**PMI:** ${pmi_monthly:,.2f}" if pmi_monthly > 0 else "PMI: Not required")
    st.markdown(f"### 👉 Total Monthly Payment: **${total_monthly_payment:,.2f}**")

    # Amortization table
    data = []
    for year in range(1, min(11, loan_term_years + 1)):
        annual_payment = total_monthly_payment * 12
        principal_paid = monthly_principal_interest * 12 * year
        interest_paid = (annual_payment * year) - principal_paid
        data.append({
            'Year': year,
            'Total Paid': round(annual_payment * year, 2),
            'Principal Paid': round(principal_paid, 2),
            'Interest Paid': round(interest_paid, 2)
        })

    df = pd.DataFrame(data)

    # Chart
    st.subheader("📈 Principal vs. Interest (Years 1–10)")
    st.line_chart(df.set_index("Year")[["Principal Paid", "Interest Paid"]])

    # Table
    st.subheader("📋 Amortization Table (1–10 Years)")
    st.dataframe(df)

    # CSV Export
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Download CSV", data=csv, file_name='amortization_schedule.csv', mime='text/csv')


    st.warning("Please enter all required loan details to calculate your mortgage.")
    st.subheader("💡 Affordability Check")
    payment_to_income = (total_monthly_payment / monthly_income) * 100
    st.write(f"Your mortgage payment is **{payment_to_income:.2f}%** of your monthly income.")

    if payment_to_income > 28:
        st.error("⚠️ Warning: Your mortgage exceeds the 28% recommended housing ratio.")
    elif payment_to_income > 36:
        st.error("⚠️ Warning: Your total debt may exceed the safe 36% threshold.")
    else:
        st.success("✅ Your mortgage is within a healthy income range.")

    # Early Payoff Modeling
    st.subheader("📈 Early Payoff Projection")

    balance = loan_amount
    month = 0
    extra_payment = (monthly_income * extra_payment_percent / 100)
    total_paid = 0
    total_interest = 0

    while balance > 0 and month < 1200:  # Safety limit
        interest_payment = balance * monthly_interest
        principal_payment = monthly_principal_interest - interest_payment
        total_principal_payment = principal_payment + extra_payment

        if total_principal_payment > balance:
            total_principal_payment = balance
            interest_payment = balance * monthly_interest  # Final interest adjustment

        balance -= total_principal_payment
        total_paid += total_principal_payment + interest_payment
        total_interest += interest_payment
        month += 1

    payoff_years = month // 12
    payoff_remaining_months = month % 12

    st.write(f"With {extra_payment_percent}% of your income allocated monthly:")
    st.success(f"🏁 You would pay off the loan in **{payoff_years} years and {payoff_remaining_months} months**")
    st.write(f"Total paid: **${total_paid:,.2f}**, of which interest: **${total_interest:,.2f}**")

else:
    st.warning("Please complete all inputs to view your results.")

