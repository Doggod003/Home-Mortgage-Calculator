def run_mortgage_calculator():
    print("🏡 Welcome to the Mortgage Calculator!\n")

    # User input
    home_price = float(input("Enter the home price ($): "))
    down_payment = float(input("Enter the down payment amount ($): "))
    loan_term_years = int(input("Enter the loan term (15 or 30 years): "))
    interest_rate = float(input("Enter the annual interest rate (%): "))
    property_tax_rate = float(input("Enter the property tax rate (% of home price): "))
    annual_insurance = float(input("Enter the annual home insurance cost ($): "))

    # Basic calculations
    loan_amount = home_price - down_payment
    down_payment_percent = (down_payment / home_price) * 100
    monthly_interest = interest_rate / 100 / 12
    total_months = loan_term_years * 12

    # Monthly principal + interest
    if monthly_interest == 0:
        monthly_principal_interest = loan_amount / total_months
    else:
        monthly_principal_interest = (
            loan_amount
            * (monthly_interest * (1 + monthly_interest) ** total_months)
            / ((1 + monthly_interest) ** total_months - 1)
        )

    # Monthly property tax and insurance
    monthly_property_tax = (home_price * (property_tax_rate / 100)) / 12
    monthly_insurance = annual_insurance / 12

    # PMI calculation
    pmi_monthly = 0
    if down_payment_percent < 20:
        if loan_term_years == 30:
            pmi_rate = 0.0055  # 0.55% annually
        elif loan_term_years == 15:
            pmi_rate = 0.003  # 0.30% annually
        else:
            pmi_rate = 0.0055  # Default to 30-year rate
        pmi_monthly = (loan_amount * pmi_rate) / 12

    # Total monthly payment
    total_monthly_payment = (
        monthly_principal_interest
        + monthly_property_tax
        + monthly_insurance
        + pmi_monthly
    )

    # Output results
    print("\n📊 Mortgage Breakdown:")
    print(f"Loan Amount: ${loan_amount:,.2f}")
    print(f"Monthly Principal & Interest: ${monthly_principal_interest:,.2f}")
    print(f"Monthly Property Tax: ${monthly_property_tax:,.2f}")
    print(f"Monthly Insurance: ${monthly_insurance:,.2f}")
    if pmi_monthly > 0:
        print(f"Monthly PMI (Private Mortgage Insurance): ${pmi_monthly:,.2f}")
    else:
        print("PMI: Not required (You put at least 20% down)")
    print(f"\n👉 Total Monthly Mortgage Payment: ${total_monthly_payment:,.2f}")


# Run the calculator
if __name__ == "__main__":
    run_mortgage_calculator()
