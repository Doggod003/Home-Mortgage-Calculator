import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mortgage Calculator", layout="centered")

st.title("🏡 Mortgage Calculator with PMI")

# Sidebar inputs
st.sidebar.header("Enter Loan Details")

home_price = st.sidebar.number_input("Home Price ($)", min_value=10000, value=300000, step=1000)
down_payment = st.sidebar.number_input("Down Payment ($)", min_value=0, value=60000, step=1000)
loan_term_years = st.sidebar.selectbox("Loan Term (years)", [15, 30], index=1)
interest_rate = st.sidebar.slider("Interest Rate (%)", 0.0, 10.0, 6.5, 0.1)
property_tax_rate = st.sidebar.slider("Property Tax Rate (%)", 0.0, 5.0, 1.2, 0.1)
annual_insurance = st.sidebar.number_input("Annual Home Insurance ($)", min_value=0, value=1200, step=100)

# Calculations
loan_amount = home_price - down_payment
monthly_interest = interest_rate / 100 / 12
total_months = loan_term_years * 12
down_payment_percent = (down_payment / home_price) * 100

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

# Total monthly payment
total_monthly_payment = (
    monthly_principal_interest
    + monthly_property_tax
    + monthly_insurance
    + pmi_monthly
)

# Results
st.subheader("📊 Monthly Payment Breakdown")
st.write(f"**Loan Amount:** ${loan_amount:,.2f}")
st.write(f"**Principal & Interest:** ${monthly_principal_interest:,.2f}")
st.write(f"**Property Tax:** ${monthly_property_tax:,.2f}")
st.write(f"**Insurance:** ${monthly_insurance:,.2f}")
if pmi_monthly > 0:
    st.write(f"**PMI:** ${pmi_monthly:,.2f}")
else:
    st.write("**PMI:** Not required (you put at least 20% down)")

st.markdown(f"### 👉 Total Monthly Payment: **${total_monthly_payment:,.2f}**")

# Amortization table for 1–10 years
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
fig, ax = plt.subplots()
ax.plot(df['Year'], df['Principal Paid'], label='Principal Paid', marker='o')
ax.plot(df['Year'], df['Interest Paid'], label='Interest Paid', marker='o')
ax.set_xlabel('Year')
ax.set_ylabel('Amount ($)')
ax.set_title('Principal vs. Interest Breakdown')
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Table
st.subheader("📋 Amortization Table (1–10 Years)")
st.dataframe(df)

# Export
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("💾 Download Amortization CSV", data=csv, file_name='amortization_schedule.csv', mime='text/csv')
