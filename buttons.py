import streamlit as st

def reset_year_filter(min_year, max_year):
    if "year_range" not in st.session_state:
        st.session_state.year_range = (min_year, max_year)

    if st.button("🔁 Reset Filter"):
        st.session_state.year_range = (min_year, max_year)
        # ✅ Set a flag to trigger rerun safely
        st.session_state.reset_triggered = True
