import streamlit as st
import pandas as pd
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(
    page_title="PRISM - Financial Reconciliation Portal",
    page_icon="🏢",
    layout="wide"
)

# --- MOCK HOTEL MASTER ---
@st.cache_data
def get_hotels():
    return pd.DataFrame([
        {"prism_id": "DEFRAM001", "property_name": "Sunday Hotel Saarbrücken Süd", "region": "Europe"},
        {"prism_id": "DE_DSN001", "property_name": "Sunday Schwarzbachtal Hideaway Resort", "region": "Europe"},
        {"prism_id": "UK_CARD001", "property_name": "Cardiff Hotel & Suites", "region": "UK"},
        {"prism_id": "UK_WALT001", "property_name": "Walton Hall Country House", "region": "UK"}
    ])

hotel_df = get_hotels()

# --- INITIAL DATASTORE ---
if "records_df" not in st.session_state:
    st.session_state.records_df = pd.DataFrame([
        {
            "prism_id": "DEFRAM001",
            "property_name": "Sunday Hotel Saarbrücken Süd",
            "region": "Europe",
            "month_year": "2026-07",
            "closing_cash_balance": 78881.53,
            "total_monthly_expense": 2065.83,
            "confirmed_by": "Lisa Gachot (GM)",
            "submitted_at": "2026-08-04 13:42:00"
        }
    ])

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("# **PRISM**")
    st.caption("Financial Reconciliation Portal")
    st.divider()
    menu = st.radio("NAVIGATION", ["Submit Monthly Record", "View Balances & Expenses"])

current_time = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
st.caption(f"📅 {current_time}")

# ==============================================================================
# 1. SIMPLE ENTRY FORM
# ==============================================================================
if menu == "Submit Monthly Record":
    st.markdown("### 📝 Record Month-End Closing & Expense")
    
    with st.form("simple_entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        
        with c1:
            hotel_id = st.text_input("Hotel / PRISM ID * (e.g. DEFRAM001)").strip().upper()
            month_year = st.text_input("Month-Year (YYYY-MM) *", value="2026-07")
            confirmed_by = st.text_input("Confirmed By (Name/Role)", value="Lisa Gachot (GM)")

        with c2:
            closing_cash = st.number_input("Closing Cash Balance (€/£) *", min_value=0.0, format="%.2f", value=78881.53)
            monthly_expense = st.number_input("Total Monthly Expense (€/£) *", min_value=0.0, format="%.2f", value=2065.83)
            mail_file = st.file_uploader("Attach Mail Proof / Screenshot *", type=["png", "jpg", "pdf", "msg"])
            
        submit = st.form_submit_button("Save Record", type="primary")
        
        if submit:
            matched = hotel_df[hotel_df["prism_id"] == hotel_id]
            if matched.empty:
                st.error("Invalid Hotel ID! Please check and try again.")
            else:
                h_name = matched.iloc[0]["property_name"]
                h_region = matched.iloc[0]["region"]
                
                new_entry = {
                    "prism_id": hotel_id,
                    "property_name": h_name,
                    "region": h_region,
                    "month_year": month_year,
                    "closing_cash_balance": closing_cash,
                    "total_monthly_expense": monthly_expense,
                    "confirmed_by": confirmed_by,
                    "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.records_df = pd.concat([pd.DataFrame([new_entry]), st.session_state.records_df], ignore_index=True)
                st.success(f"Successfully recorded data for {h_name} ({month_year})!")

# ==============================================================================
# 2. RECORDS & SUMMARY DASHBOARD
# ==============================================================================
elif menu == "View Balances & Expenses":
    st.markdown("### 📊 Monthly Closing & Expense Summary")
    
    f1, f2 = st.columns(2)
    with f1:
        sel_region = st.selectbox("Filter by Region", ["All", "Europe", "UK"])
    with f2:
        sel_month = st.selectbox("Filter by Month", ["All"] + list(st.session_state.records_df["month_year"].unique()))

    df = st.session_state.records_df.copy()
    if sel_region != "All":
        df = df[df["region"] == sel_region]
    if sel_month != "All":
        df = df[df["month_year"] == sel_month]

    m1, m2, m3 = st.columns(3)
    m1.metric("Properties Reported", len(df))
    m2.metric("Total Closing Cash", f"€ {df['closing_cash_balance'].sum():,.2f}")
    m3.metric("Total Expenses", f"€ {df['total_monthly_expense'].sum():,.2f}")

    st.write("<br>", unsafe_allow_html=True)
    
    st.dataframe(
        df[["prism_id", "property_name", "region", "month_year", "closing_cash_balance", "total_monthly_expense", "confirmed_by", "submitted_at"]],
        use_container_width=True,
        hide_index=True
    )
