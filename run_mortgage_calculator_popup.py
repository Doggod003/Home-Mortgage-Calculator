#for people viewing this I put spacers in because I have horrible OCD and Im new to this
from fpdf import FPDF
import tempfile
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from buttons import reset_year_filter
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from sidebar import render_sidebar

st.set_page_config(page_title="Mortgage Calculator", layout="wide")

def load_local_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS at the beginning of the app
load_local_css("assets/tabs.css")  # or "styles/tabs.css" if you used styles/
with open("assets/tabs.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#---------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------------------
# Simulate HOA and Maintenance
# ------------------------------------------------------------------------------------------
def simulate_hoa_and_maintenance(months, base_hoa=100, base_maint=150, annual_inflation=0.03):
    hoa_list = []
    maint_list = []
    for m in range(months):
        inflation_factor = (1 + annual_inflation) ** (m / 12)

        hoa = base_hoa * inflation_factor
        maintenance = base_maint * inflation_factor

        # Simulate major maintenance spikes every 5 or 10 years
        if m % 60 == 0 and m != 0:
            maintenance += 2000 * (0.75 + 0.5 * (m % 120 == 0))

        hoa_list.append(round(hoa, 2))
        maint_list.append(round(maintenance, 2))

    return hoa_list, maint_list

# ----------------------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------------------
st.set_page_config(page_title="Mortgage Calculator", layout="centered")
st.title("🏡 Mortgage Calculator")

if "history" not in st.session_state:
    st.session_state.history = []
#----
#sidebar   
#----    
render_sidebar()

if st.session_state.get("confirmed") and "inputs" in st.session_state:
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
else:
    st.warning("Please confirm your loan setup using the sidebar.")
    st.stop()  # Prevents the rest of the script from executing
    loan_amount = home_price - down_payment
    monthly_interest = interest_rate / 100 / 12
    total_months = loan_term_years * 12
    down_payment_percent = (down_payment / home_price) * 100

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

    st.session_state.history.append({
        "Home Price": home_price,
        "Loan Amount": loan_amount,
        "Interest Rate": interest_rate,
        "Monthly Payment": round(df_monthly["Payment"].iloc[0], 2),
        "Years to Payoff": f"{years}y {months}m",
        "Total Interest": round(df_monthly['Interest'].sum(), 2)
    })
    
    # ----------------------------
    # Tabs
    # ----------------------------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Payment",
        "💡 Affordable?",
        "📋 Table",
        "📈 Analysis",
        "📊 Compare",
        "📂 Archive",
        "💾 Export"
        
        
    ])

    with tab1:
      
        min_year = int(df_monthly["Month"].min() / 12)
        max_year = int(df_monthly["Month"].max() / 12)
        
        # Show the reset button from the external file
        reset_year_filter(min_year, max_year)
        
        # Use the year_range from session state
        year_range = st.session_state.year_range
        month_start = year_range[0] * 12
        month_end = (year_range[1] + 1) * 12 - 1
        filtered_df = df_monthly[(df_monthly["Month"] >= month_start) & (df_monthly["Month"] <= month_end)]
        st.markdown('<div class="chart-kpi"><h3>📊 Monthly Payment Breakdown</h3></div>', unsafe_allow_html=True)        
        with st.expander("📌 Full Payment Breakdown", expanded=True):
            st.write(f"**Loan Amount:** ${loan_amount:,.2f}")
            st.write(f"**Principal & Interest:** ${monthly_principal_interest:,.2f}")
            st.write(f"**Property Tax:** ${monthly_property_tax:,.2f}")
            st.write(f"**Insurance:** ${monthly_insurance:,.2f}")
            if initial_pmi_monthly > 0:
                st.write(f"**PMI (Initial):** ${initial_pmi_monthly:,.2f}")
            st.write(f"**HOA (Initial):** ${base_hoa:,.2f}")
            st.write(f"**Maintenance (Initial):** ${base_maint:,.2f}")
            total_monthly_payment = monthly_principal_interest + monthly_property_tax + monthly_insurance + initial_pmi_monthly + base_hoa + base_maint
            st.markdown(f"### 👉 Total Monthly Payment: **${total_monthly_payment:,.2f}**")
        with st.expander("📌 Key Loan Metrics"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Monthly Payment", f"${total_monthly_payment:,.0f}")
            col2.metric("Time to Payoff", f"{years}y {months}m")
            col3.metric("Total Interest", f"${df_monthly['Interest'].sum():,.0f}")
           



    with tab2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)  # Start wrapper
        st.markdown('<div class="chart-kpi"><h3>💡 Affordability Check</h3></div>', unsafe_allow_html=True)
        with st.expander("📈 Debt-to-Income (DTI) Analysis", expanded=True):
            payment_to_income = (total_monthly_payment / monthly_income) * 100
            st.write(f"Your mortgage payment is **{payment_to_income:.2f}%** of your monthly income.")
            if payment_to_income > 36:
                st.error("🚨 Exceeds 36% — risky debt-to-income ratio.")
            elif payment_to_income > 28:
                st.warning("⚠️ Above 28% — higher than recommended for housing.")
            else:
                st.success("✅ Affordable based on income.")
            df_monthly["DTI %"] = (df_monthly["Payment"] / monthly_income) * 100
            fig_dti = go.Figure()
            fig_dti.add_trace(go.Scatter(
                x=df_monthly["Month"],
                y=df_monthly["DTI %"],
                mode='lines+markers',
                name='DTI %',
                line=dict(color='darkblue')
            ))
            fig_dti.update_layout(
                title="DTI Over Time",
                xaxis_title="Month",
                yaxis_title="DTI (%)",
                template="plotly_white",
                legend=dict(x=1.05, y=1),
                margin=dict(r=80)
            )
            
            st.plotly_chart(fig_dti, use_container_width=True)            
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="chart-kpi"><h3>📋 Monthly Amortization Schedule</h3></div>', unsafe_allow_html=True)

        with st.expander("📅 Amortization Table", expanded=True):
            gb = GridOptionsBuilder.from_dataframe(df_monthly.head(360))
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_default_column(resizable=True, filter=True, sortable=True)
            gridOptions = gb.build()
            AgGrid(
                df_monthly.head(360),
                gridOptions=gridOptions,
                enable_enterprise_modules=False,
                theme="material",  # Options: "streamlit", "alpine", "material", "balham", etc.
                fit_columns_on_grid_load=True,
                height=400,
            )
    
    with tab4: #TAB 4 
        min_year = int(df_monthly["Month"].min() / 12)
        max_year = int(df_monthly["Month"].max() / 12)
        year_range = st.slider("Select Year Range", min_year, max_year, (min_year, max_year))
        month_start = year_range[0] * 12
        month_end = (year_range[1] + 1) * 12 - 1
        filtered_df = df_monthly[(df_monthly["Month"] >= month_start) & (df_monthly["Month"] <= month_end)]
    # 📈 Balance Timeline
        
        st.markdown('<div class="chart-kpi"><h3>📈 Balance Timeline</h3></div>', unsafe_allow_html=True)
        with st.expander("📉 Balance Over Time", expanded=True):
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=filtered_df["Month"],
                y=filtered_df["Balance"],
                mode='lines+markers',
                name='Balance',
                line=dict(color='blue')
            ))
            fig1.update_layout(
                xaxis_title="Month",
                yaxis_title="Balance ($)",
                template="plotly_white",
                legend=dict(x=1.05, y=1),
                margin=dict(r=120)
            )
            st.plotly_chart(fig1, use_container_width=True)

    # 📊 Principal vs Interest
        st.markdown('<div class="chart-kpi"><h3>📊 Principal vs Interest</h3></div>', unsafe_allow_html=True)
        with st.expander("📊 Principal vs Interest", expanded=True):
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=filtered_df["Month"],
                y=filtered_df["Principal"],
                mode='lines+markers',
                name='Principal',
                line=dict(color='green')
            ))
            fig2.add_trace(go.Scatter(
                x=filtered_df["Month"],
                y=filtered_df["Interest"],
                mode='lines+markers',
                name='Interest',
                line=dict(color='red')
            ))
            fig2.update_layout(
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                template="plotly_white",
                legend=dict(x=1.05, y=1),
                margin=dict(r=120)
            )
            st.plotly_chart(fig2, use_container_width=True)

    # 🏠 HOA & Maintenance
        st.markdown('<div class="chart-kpi"><h3>🏠 HOA & Maintenance Over Time</h3></div>', unsafe_allow_html=True)
        with st.expander("🏠 HOA & Maintenance", expanded=True):
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=filtered_df["Month"],
                y=filtered_df["HOA"],
                mode='lines+markers',
                name='HOA',
                line=dict(color='purple')
            ))
            fig3.add_trace(go.Scatter(
                x=filtered_df["Month"],
                y=filtered_df["Maintenance"],
                mode='lines+markers',
                name='Maintenance',
                line=dict(color='orange')
            ))
            fig3.update_layout(
                xaxis_title="Month",
                yaxis_title="Monthly Cost ($)",
                template="plotly_white",
                legend=dict(x=1.05, y=1),
                margin=dict(r=120)
            )
            st.plotly_chart(fig3, use_container_width=True)

    with tab5:
        st.markdown('<div class="chart-kpi"><h3>📊 Side-by-Side Loan Comparison</h3></div>', unsafe_allow_html=True)
        st.info("This section will allow you to compare two mortgage scenarios side by side.")
    
        st.markdown("""
        **Coming Next:**
        - Two parallel input panels for Loan A and Loan B
        - Independent amortization for each
        - Comparison table of monthly payment, interest, payoff time, DTI
        - Optional: side-by-side charting
        """)

    with tab5:
        st.markdown('<div class="chart-kpi"><h3>📊 Side-by-Side Loan Comparison</h3></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🅰️ Loan A")
            with st.expander("🅰️ Loan A Inputs"):
                home_price_a = st.number_input("Home Price (A)", value=300000, key="price_a")
                down_payment_a = st.number_input("Down Payment (A)", value=60000, key="down_a")
                interest_a = st.number_input("Interest Rate % (A)", value=6.5, key="rate_a")
                term_a = st.selectbox("Term (A)", [15, 30], index=1, key="term_a")
                income_a = st.number_input("Monthly Income (A)", value=6000, key="income_a")
        
        with col2:
            st.markdown("### 🅱️ Loan B")
            with st.expander("🅱️ Loan B Inputs"):    
                home_price_b = st.number_input("Home Price (B)", value=325000, key="price_b")
                down_payment_b = st.number_input("Down Payment (B)", value=65000, key="down_b")
                interest_b = st.number_input("Interest Rate % (B)", value=6.0, key="rate_b")
                term_b = st.selectbox("Term (B)", [15, 30], index=1, key="term_b")
                income_b = st.number_input("Monthly Income (B)", value=6000, key="income_b")
        
        def calc_mortgage(p, r, n):
            r_month = r / 12 / 100
            n_months = n * 12
            return p / n_months if r_month == 0 else p * (r_month * (1 + r_month)**n_months) / ((1 + r_month)**n_months - 1)
    
        loan_amt_a = home_price_a - down_payment_a
        loan_amt_b = home_price_b - down_payment_b
    
        monthly_a = calc_mortgage(loan_amt_a, interest_a, term_a)
        monthly_b = calc_mortgage(loan_amt_b, interest_b, term_b)
    
        st.markdown("### 🔍 Loan Comparison Summary")
        with st.expander("📊 Comparison Summary"):    
            comparison = {
                "Metric": [
                    "Home Price", "Loan Amount", "Interest Rate", "Term (years)",
                    "Monthly Payment", "DTI % (Monthly / Income)"
                ],
                "Loan A": [
                    f"${home_price_a:,.2f}", f"${loan_amt_a:,.2f}", f"{interest_a:.2f}%", f"{term_a}",
                    f"${monthly_a:,.2f}", f"{(monthly_a / income_a * 100):.2f}%"
                ],
                "Loan B": [
                    f"${home_price_b:,.2f}", f"${loan_amt_b:,.2f}", f"{interest_b:.2f}%", f"{term_b}",
                    f"${monthly_b:,.2f}", f"{(monthly_b / income_b * 100):.2f}%"
                ]
            }
        
            df_compare = pd.DataFrame(comparison)
            st.dataframe(df_compare, use_container_width=True)    
       

    
with tab6:
    st.markdown('<div class="chart-kpi"><h3>📂 Archive</h3></div>', unsafe_allow_html=True)
    with st.expander("📁 View Saved Calculations", expanded=True):
        if st.session_state.history:
            df_history = pd.DataFrame(st.session_state.history)

            gb = GridOptionsBuilder.from_dataframe(df_history)
            gb.configure_pagination()
            gb.configure_default_column(groupable=True, value=True, editable=False)
            gb.configure_selection(selection_mode="single", use_checkbox=True)
            grid_options = gb.build()

            grid_response = AgGrid(
                df_history,
                gridOptions=grid_options,
                height=400,
                theme="streamlit",
                fit_columns_on_grid_load=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED
            )

            selected = grid_response['selected_rows']

            if selected:
                selected_data = selected[0]

                pdf_data = {
                    "Home Price": selected_data.get("Home Price"),
                    "Loan Amount": selected_data.get("Loan Amount"),
                    "Interest Rate": selected_data.get("Interest Rate"),
                    "Loan Term": selected_data.get("Loan Term"),
                    "P&I": selected_data.get("P&I"),
                    "Tax": selected_data.get("Tax"),
                    "Insurance": selected_data.get("Insurance"),
                    "PMI": selected_data.get("PMI"),
                    "HOA": selected_data.get("HOA"),
                    "Maintenance": selected_data.get("Maintenance"),
                    "Total Payment": selected_data.get("Total Payment"),
                    "DTI": selected_data.get("DTI"),
                    "Payoff Time": selected_data.get("Payoff Time"),
                    "Total Paid": selected_data.get("Total Paid"),
                    "Total Interest": selected_data.get("Total Interest"),
                }

                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="🏡 Mortgage Report", ln=True, align="C")

                for key, value in pdf_data.items():
                    pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

                pdf_output = "/tmp/mortgage_report.pdf"
                pdf.output(pdf_output)

                with open(pdf_output, "rb") as f:
                    st.download_button(
                        label="📥 Download Selected Report as PDF",
                        data=f,
                        file_name="mortgage_report.pdf",
                        mime="application/pdf"
                    )
            else:
                st.info("No calculations saved yet.")

    with tab7:
        csv = df_monthly.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="monthly_amortization.csv", mime="text/csv")
        pdf_data = {
        "Home Price": home_price,
        "Loan Amount": loan_amount,
        "Interest Rate": interest_rate,
        "Loan Term": loan_term_years,
        "P&I": round(monthly_principal_interest, 2),
        "Tax": round(monthly_property_tax, 2),
        "Insurance": round(monthly_insurance, 2),
        "PMI": round(initial_pmi_monthly, 2),
        "HOA": round(base_hoa, 2),
        "Maintenance": round(base_maint, 2),
        "Total Payment": round(total_monthly_payment, 2),
        "DTI": round((total_monthly_payment / monthly_income) * 100, 2),
        "Payoff Time": f"{years}y {months}m",
        "Total Paid": round(df_monthly['Payment'].sum(), 2),
        "Total Interest": round(df_monthly['Interest'].sum(), 2),
    }

    pdf_path = generate_pdf_summary(pdf_data)
    
    with tab7:
        with open(pdf_path, "rb") as file:
            st.download_button(
                label="📄 Download PDF Report",
                data=file,
                file_name="Mortgage_Summary.pdf",
                mime="application/pdf"
            )




