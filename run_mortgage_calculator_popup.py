from fpdf import FPDF
import tempfile
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from buttons import reset_year_filter
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from sidebar import render_sidebar

# Set Streamlit page config
st.set_page_config(page_title="Mortgage Calculator", layout="wide")

# Load CSS
def load_local_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_local_css("assets/tabs.css")

# PDF class
class MortgagePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Mortgage Summary Report", ln=True, align="C")
        self.ln(10)

    def section_title(self, title):
        self.set_font("Arial", "B", 11)
        self.cell(0, 10, title, ln=True)
        self.ln(1)

    def section_body(self, text):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 8, text)
        self.ln()

def generate_pdf_summary(summary_data):
    pdf = MortgagePDF()
    pdf.add_page()

    pdf.section_title("Loan Overview")
    overview = (
        f"Home Price: ${summary_data['Home Price']:,}\n"
        f"Loan Amount: ${summary_data['Loan Amount']:,}\n"
        f"Interest Rate: {summary_data['Interest Rate']}%\n"
        f"Loan Term: {summary_data['Loan Term']} years\n"
    )
    pdf.section_body(overview)

    pdf.section_title("Monthly Payment Breakdown")
    payment = (
        f"Principal & Interest: ${summary_data['P&I']:,}\n"
        f"Property Tax: ${summary_data['Tax']:,}\n"
        f"Insurance: ${summary_data['Insurance']:,}\n"
        f"PMI: ${summary_data['PMI']:,}\n"
        f"HOA: ${summary_data['HOA']:,}\n"
        f"Maintenance: ${summary_data['Maintenance']:,}\n"
        f"Total Monthly: ${summary_data['Total Payment']:,}"
    )
    pdf.section_body(payment)

    pdf.section_title("Affordability Check")
    pdf.section_body(f"DTI (Debt-to-Income Ratio): {summary_data['DTI']:.2f}%")

    pdf.section_title("Payoff Summary")
    payoff = (
        f"Time to Payoff: {summary_data['Payoff Time']}\n"
        f"Total Paid: ${summary_data['Total Paid']:,}\n"
        f"Total Interest Paid: ${summary_data['Total Interest']:,}"
    )
    pdf.section_body(payoff)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

def simulate_hoa_and_maintenance(months, base_hoa=100, base_maint=150, annual_inflation=0.03):
    hoa_list = []
    maint_list = []
    for m in range(months):
        inflation_factor = (1 + annual_inflation) ** (m / 12)
        hoa = base_hoa * inflation_factor
        maintenance = base_maint * inflation_factor
        if m % 60 == 0 and m != 0:
            maintenance += 2000 * (0.75 + 0.5 * (m % 120 == 0))
        hoa_list.append(round(hoa, 2))
        maint_list.append(round(maintenance, 2))
    return hoa_list, maint_list

# Title
st.title("🏡 Mortgage Calculator")

if "history" not in st.session_state:
    st.session_state.history = []

# Render sidebar
render_sidebar()

# Ensure inputs exist
if not st.session_state.get("confirmed") or "inputs" not in st.session_state:
    st.warning("Please confirm your loan setup using the sidebar.")
    st.stop()

# Load user inputs
inputs = st.session_state.inputs

home_price = inputs["home_price"]
down_payment_percent = inputs["down_payment_percent"]
down_payment = home_price * (down_payment_percent / 100)
interest_rate = inputs["interest_rate"]
loan_term_years = inputs["loan_term_years"]
property_tax_rate = inputs["property_tax_rate"]
annual_insurance = inputs["annual_insurance"]
monthly_income = inputs["monthly_income"]
extra_payment_percent = inputs["extra_payment_percent"]
pmi_drops_off = inputs["pmi_drops_off"]
base_hoa = inputs["base_hoa"]
base_maint = inputs["base_maint"]

loan_amount = home_price - down_payment
monthly_interest = interest_rate / 100 / 12
total_months = loan_term_years * 12

monthly_principal_interest = (
    loan_amount *
    (monthly_interest * (1 + monthly_interest) ** total_months) /
    ((1 + monthly_interest) ** total_months - 1)
) if monthly_interest > 0 else loan_amount / total_months

monthly_property_tax = (home_price * (property_tax_rate / 100)) / 12
monthly_insurance = annual_insurance / 12
pmi_rate = 0.0055 if loan_term_years == 30 else 0.003
initial_pmi_monthly = (loan_amount * pmi_rate) / 12 if down_payment_percent < 20 else 0

hoa_schedule, maint_schedule = simulate_hoa_and_maintenance(1200, base_hoa, base_maint)

amortization_rows = []
balance = loan_amount
month = 1
cumulative_interest = 0
cumulative_principal = 0

while balance > 0 and month <= 1200:
    monthly_hoa = hoa_schedule[month - 1]
    monthly_maintenance = maint_schedule[month - 1]
    interest_payment = balance * monthly_interest
    principal_payment = monthly_principal_interest - interest_payment
    extra_payment = (extra_payment_percent / 100) * monthly_income
    total_principal = principal_payment + extra_payment

    if total_principal > balance:
        total_principal = balance
        principal_payment = balance
        total_payment = balance + interest_payment + monthly_hoa + monthly_maintenance
    else:
        total_payment = (
            monthly_principal_interest +
            extra_payment +
            monthly_hoa +
            monthly_maintenance
        )

    balance -= total_principal
    cumulative_interest += interest_payment
    cumulative_principal += total_principal

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
        'HOA': round(monthly_hoa, 2),
        'Maintenance': round(monthly_maintenance, 2),
        'Cumulative Principal': round(cumulative_principal, 2),
        'Cumulative Interest': round(cumulative_interest, 2),
        'Balance': round(balance, 2)
    })

    month += 1

df_monthly = pd.DataFrame(amortization_rows)
payoff_months = len(df_monthly)
years = payoff_months // 12
months = payoff_months % 12

# Add to archive
st.session_state.history.append({
    "Home Price": home_price,
    "Loan Amount": loan_amount,
    "Interest Rate": interest_rate,
    "Monthly Payment": round(df_monthly["Payment"].iloc[0], 2),
    "Years to Payoff": f"{years}y {months}m",
    "Total Interest": round(df_monthly['Interest'].sum(), 2)
})
