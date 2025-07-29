import streamlit as st
import pandas as pd

#!!!! Page settings!!!!!!!!!!!!
st.set_page_config(page_title="Mortgage Calculator", layout="centered")
st.title("🏡 Mortgage Calculator with PMI, Affordability, and Payoff Modeling")

# !!!!!!!!!!!Sidebar Inputs!!!!!!!!!!!!!!!
st.sidebar.header("Loan Setup")

# Home price input
home_price = st.sidebar.number_input("Home Price ($)", min_value=10000, value=300000, step=1000)

# Loan type selection
loan_type = st.sidebar.selectbox("Loan Type Preset", [
    "Conventional (20%)",
    "FHA (3.5%)",
    "VA (0%)",
    "Custom"
])

# Apply preset defaults
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

# Editable inputs based on preset
down_payment_percent_input = st.sidebar.number_input("Down Payment (% of Home Price)", 0.0, 100.0, value=default_down_percent, step=0.5)
down_payment = home_price * (down_payment_percent_input / 100)

loan_term_years = st.sidebar.selectbox("Loan Term (years)", [15, 30], index=0 if default_term == 15 else 1)
interest_rate = st.sidebar.number_input("Interest Rate (%)", min_value=0.0, value=default_interest, step=0.1)

# Additional required inputs
property_tax_rate = st.sidebar.number_input("Property Tax Rate (%)", min_value=0.0, value=1.2, step=0.1)
annual_insurance = st.sidebar.number_input("Annual Home Insurance ($)", min_value=0, value=1200, step=100)
monthly_income = st.sidebar.number_input("Monthly Income ($)", min_value=0, value=6000, step=100)
extra_payment_percent = st.sidebar.slider("Extra % of Income Toward Loan Payoff", 0, 50, 10)
pmi_drops_off = st.sidebar.checkbox("PMI drops off at 20% equity", value=True)













# !!!!!!!!!!!!!!!Validate inputs!!!!!!!!!!!!!
if home_price > 0 and down_payment >= 0 and down_payment < home_price and interest_rate > 0 and monthly_income > 0:

    #!!!!!!!!!!!!!!!!! Core calculations!!!!!!!!!!!!!!!!
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

    # !!!!!!!!!!!!!!!!PMI setup!!!!!!!!!!!!!!!!
    pmi_rate = 0.0055 if loan_term_years == 30 else 0.003
    initial_pmi_monthly = (loan_amount * pmi_rate) / 12 if down_payment_percent < 20 else 0

    # !!!!!!!!!!!!!Total initial monthly payment!!!!!!!!!!!!!!!!!
    total_monthly_payment = (
        monthly_principal_interest +
        monthly_property_tax +
        monthly_insurance +
        initial_pmi_monthly
    )

    # !!!!!!!!!!!!!!!!📊 Monthly Breakdown!!!!!!!!!!!
    st.subheader("📊 Monthly Payment Breakdown")
    st.write(f"**Loan Amount:** ${loan_amount:,.2f}")
    st.write(f"**Principal & Interest:** ${monthly_principal_interest:,.2f}")
    st.write(f"**Property Tax:** ${monthly_property_tax:,.2f}")
    st.write(f"**Insurance:** ${monthly_insurance:,.2f}")
    if initial_pmi_monthly > 0:
        st.write(f"**PMI:** ${initial_pmi_monthly:,.2f}")
    st.markdown(f"### 👉 Total Monthly Payment: **${total_monthly_payment:,.2f}**")

    # !!!!!!!!!!!!!💡 Affordability Check!!!!!!!!!!!!!!!!!
    st.subheader("💡 Affordability Check")
    payment_to_income = (total_monthly_payment / monthly_income) * 100
    st.write(f"Your mortgage payment is **{payment_to_income:.2f}%** of your monthly income.")
    if payment_to_income > 36:
        st.error("🚨 Exceeds 36% — risky debt-to-income ratio.")
    elif payment_to_income > 28:
        st.warning("⚠️ Above 28% — higher than recommended for housing.")
    else:
        st.success("✅ Affordable based on income.")

    # !!!!!!!!!!!!!!!!!!📋 Amortization Schedule!!!!!!!!!!!!!!!!!
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

        # !!!!!!!!!!!!PMI logic: drop at 20% equity!!!!!!!!!!!!!!!!
        current_pmi = 0
        if initial_pmi_monthly > 0:
            equity_percent = (cumulative_principal + down_payment) / home_price * 100
            if not pmi_drops_off or equity_percent < 20:
                current_pmi = initial_pmi_monthly

        amortization_rows.append({
            'Month': month,
            'Payment': round(total_payment + current_pmi, 2),
            'Principal': round(total_principal, 2),
            'Interest': round(interest_payment, 2),
            'PMI': round(current_pmi, 2),
            'Cumulative Principal': round(cumulative_principal, 2),
            'Cumulative Interest': round(cumulative_interest, 2),
            'Balance': round(balance, 2)
        })

        month += 1

    df_monthly = pd.DataFrame(amortization_rows)
    st.dataframe(df_monthly.head(360))

    # !!!!!!!!!!!!!!!!!⏱️ Payoff Summary!!!!!!!!!!!!!!!
    st.subheader("⏱️ Payoff Summary")
    payoff_months = len(df_monthly)
    years = payoff_months // 12
    months = payoff_months % 12
    st.success(f"🏁 Paid off in {years} years and {months} months.")
    st.write(f"💸 Total paid: **${df_monthly['Payment'].sum():,.2f}**")
    st.write(f"📉 Total interest paid: **${df_monthly['Interest'].sum():,.2f}**")

    # !!!!!!!!!!!!!!!📈 Charts!!!!!!!!!!!!!!!
    st.subheader("📈 Balance Timeline")
    st.line_chart(df_monthly.set_index("Month")[["Balance"]])

    st.subheader("📊 Principal vs Interest Over Time")
    st.line_chart(df_monthly.set_index("Month")[["Principal", "Interest", "PMI"]])

    # !!!!!!!!!!!!!!!!!💾 Download CSV!!!!!!!!!!!!!!
    csv = df_monthly.to_csv(index=False).encode('utf-8')
    st.download_button(
        "💾 Download Full Monthly Amortization CSV",
        data=csv,
        file_name='monthly_amortization.csv',
        mime='text/csv'
    )

else:
    st.warning("Please enter valid values for all fields to calculate your mortgage.")
