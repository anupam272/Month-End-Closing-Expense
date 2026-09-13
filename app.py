import io
from datetime import datetime, date
import os
import pandas as pd
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception:
    st.error("Supabase Connection Error! Please verify credentials in secrets.")
    st.stop()

st.set_page_config(page_title="PRISM - Month-End Cash & Expense Portal", page_icon="💷", layout="wide")

# Persistent Session via Query Params / Session State Sync
query_params = st.query_params
if "auth_user" in query_params and not st.session_state.get("authenticated", False):
    st.session_state.authenticated = True
    st.session_state.username = query_params.get("auth_user")
    st.session_state.user_role = query_params.get("auth_role", "Manager")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None

# Custom Corporate Finance Theme Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700;800&display=swap');

    .stApp { 
        background-color: #dbe4f0; 
        font-family: 'Segoe UI', -apple-system, sans-serif; 
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden !important;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    section[data-testid="stSidebar"] { 
        background-color: #e2e8f0; 
        border-right: 1px solid #cbd5e1;
    }
    section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { 
        color: #1e293b !important; 
    }

    .custom-card {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 25px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    .logo-container {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 4px 8px;
        display: inline-block;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .stTextInput > label, .stSelectbox > label, .stNumberInput > label, .stDateInput > label, .stTextArea > label, .stFileUploader > label {
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 12px !important;
    }
    
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stDateInput input, .stTextArea textarea {
        border-radius: 3px !important;
        border: 1px solid #94a3b8 !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-family: 'Segoe UI', sans-serif !important;
    }

    .stButton>button {
        background: linear-gradient(to bottom, #3b82f6, #1d4ed8);
        color: #ffffff;
        border: 1px solid #1e40af;
        border-radius: 3px;
        font-weight: 600;
        font-size: 13px;
        padding: 6px 14px;
        width: 100%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(to bottom, #2563eb, #1d4ed8);
    }

    .pos-section-title {
        color: #1e3a8a;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 15px;
        margin-bottom: 12px;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 6px;
    }
    </style>
""", unsafe_allow_html=True)

def fetch_closing_records():
    try:
        res = supabase.table("month_end_cash_tracker").select("*").order("id", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def fetch_hotel_master():
    try:
        res = supabase.table("hotel_master").select("*").execute()
        if res.data:
            return pd.DataFrame(res.data)
    except Exception:
        pass
    return pd.DataFrame()

def render_header():
    now_str = datetime.now().strftime("%d %b %Y | %I:%M:%S %p")
    
    col_logo, col_title, col_time = st.columns([1.2, 3, 1.5])
    with col_logo:
        logo_paths = [
            r"Downloads\logoprism.png",
            r"C:\Users\User\Downloads\logoprism.png",
            "logoprism.png",
            "logoprism_2.png"
        ]
        
        loaded = False
        for path in logo_paths:
            if os.path.exists(path):
                try:
                    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
                    st.image(path, width=130)
                    st.markdown('</div>', unsafe_allow_html=True)
                    loaded = True
                    break
                except Exception:
                    pass
        
        if not loaded:
            st.markdown("<h3 style='color:#1e3a8a; margin:0;'>PRISM</h3>", unsafe_allow_html=True)
            
    with col_title:
        st.markdown("<div style='text-align: center;'><span style='color: #1e3a8a; font-size: 14px; font-weight: 700; letter-spacing: 0.5px;'>Month-End Cash & Expense Portal (UK & Europe Operations)</span></div>", unsafe_allow_html=True)
    with col_time:
        st.markdown(f"<div style='text-align: right;'><span style='font-family: Segoe UI, sans-serif; font-size: 12px; font-weight: 600; color: #1e293b;'>{now_str}</span></div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 5px 0px 15px 0px; border: none; border-top: 1px solid #cbd5e1;'>", unsafe_allow_html=True)

# Sidebar Authentication & Navigation
with st.sidebar:
    st.markdown("<div style='font-family: Segoe UI, sans-serif; font-size: 15px; font-weight: 700; color: #1e3a8a; margin-bottom: 10px;'>FINANCE PORTAL NAVIGATOR</div>", unsafe_allow_html=True)
    if not st.session_state.authenticated:
        st.markdown("<div style='color: #475569; font-size: 12px;'>Please sign in to access month-end modules.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"👤 **User:** {st.session_state.username}")
        st.markdown(f"🔑 **Role:** {st.session_state.user_role}")
        st.markdown("---")
        page = st.sidebar.radio("Navigation Menu", [
            "Submit Month-End Closing", 
            "Closing Overview & Ledger", 
            "Audit & Status Management", 
            "Master Reports & Pending"
        ])
        if st.sidebar.button("🔒 End Session"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.query_params.clear()
            st.rerun()

# ----------------- FINANCE LOGIN SCREEN -----------------
if not st.session_state.authenticated:
    render_header()
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("pos_login_form"):
            st.markdown("""
                <div style='text-align: center; margin-bottom: 15px;'>
                    <h3 style='color:#1e3a8a; font-family: Segoe UI, sans-serif; margin-bottom: 5px;'>🔐 PORTAL SIGN IN</h3>
                    <p style='color:#475569; font-size: 12px;'>Enter your credentials for Month-End Cash & Expense reconciliation</p>
                </div>
            """, unsafe_allow_html=True)
            
            user_input = st.text_input("USERNAME", placeholder="e.g. admin or finance_uk")
            pass_input = st.text_input("PASSWORD", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            login_submit = st.form_submit_button("Sign In")
            
            if login_submit:
                if not user_input.strip() or not pass_input.strip():
                    st.error("⚠️ Please enter both username and password.")
                else:
                    try:
                        res = supabase.table("userstb").select("*").eq("username", user_input.strip()).execute()
                        if res.data and str(res.data[0].get("password", "")).strip() == pass_input.strip():
                            st.session_state.authenticated = True
                            st.session_state.username = res.data[0]["username"]
                            st.session_state.user_role = res.data[0].get("role", "Manager")
                            
                            st.query_params["auth_user"] = st.session_state.username
                            st.query_params["auth_role"] = st.session_state.user_role
                            st.rerun()
                        else:
                            st.error("❌ Authentication Failed: Invalid Credentials!")
                    except Exception as err:
                        st.error(f"Database Connection Error: {str(err)}")
    st.stop()

REGION_OPTIONS = ["UK", "Europe"]
POST_OPTIONS = ["General Manager", "Cluster General Manager", "Finance Manager", "Assistant Manager", "Accounts Executive", "Other"]
MONTH_OPTIONS = ["Jan'26", "Feb'26", "Mar'26", "Apr'26", "May'26", "Jun'26", "Jul'26", "Aug'26", "Sep'26", "Oct'26", "Nov'26", "Dec'26"]

# ----------------- 1. SUBMIT MONTH-END CLOSING TERMINAL -----------------
if page == "Submit Month-End Closing":
    render_header()
    
    st.markdown("<h4 style='color: #1e3a8a; font-family: Segoe UI, sans-serif; margin-bottom: 15px;'>⚡ MONTH-END CASH & EXPENSE CLOSING WIZARD</h4>", unsafe_allow_html=True)

    if "auto_hotel_name" not in st.session_state:
        st.session_state.auto_hotel_name = ""
    if "auto_region" not in st.session_state:
        st.session_state.auto_region = "UK"

    def handle_prism_id_change():
        entered_id = st.session_state.get("prism_input_val", "").strip().upper()
        if entered_id:
            master_df = fetch_hotel_master()
            if not master_df.empty and "prism_id" in master_df.columns:
                matched = master_df[master_df["prism_id"].astype(str).str.strip().str.upper() == entered_id]
                if not matched.empty:
                    st.session_state.auto_hotel_name = matched.iloc[0].get("property_name", "")
                    reg = matched.iloc[0].get("property_region", "UK")
                    if reg in REGION_OPTIONS:
                        st.session_state.auto_region = reg
                else:
                    st.session_state.auto_hotel_name = "Not Found in Hotel Master"
            st.rerun()

    with st.container():
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        
        col1_lookup, col2_lookup = st.columns(2)
        with col1_lookup:
            prism_id_input = st.text_input(
                "PRISM PROPERTY ID (AUTO-LOOKUP)", 
                placeholder="e.g. DE_SCHOO02", 
                key="prism_input_val", 
                on_change=handle_prism_id_change
            )
        with col2_lookup:
            month_year = st.selectbox("CLOSING MONTH-YEAR", MONTH_OPTIONS, index=8)

        st.markdown("<div class='pos-section-title'>🏢 PROPERTY & IDENTIFICATION DETAILS</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            hotel_name = st.text_input("HOTEL NAME", value=st.session_state.auto_hotel_name, placeholder="Auto-populated from ID")
        with col2:
            default_reg_idx = REGION_OPTIONS.index(st.session_state.auto_region) if st.session_state.auto_region in REGION_OPTIONS else 0
            region = st.selectbox("OPERATING REGION", REGION_OPTIONS, index=default_reg_idx)

        st.markdown("<div class='pos-section-title'>💰 CASH RECONCILIATION & MONTHLY EXPENSES</div>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            petty_cash_expense = st.number_input("TOTAL PETTY CASH EXPENSE (£/€)", min_value=0.0, format="%.2f", value=0.0)
        with col4:
            closing_balance = st.number_input("FINAL CLOSING CASH BALANCE (£/€)", min_value=0.0, format="%.2f", value=0.0)

        st.markdown("<div class='pos-section-title'>✍️ SIGN-OFF & MANAGEMENT AUDIT</div>", unsafe_allow_html=True)
        col5, col6 = st.columns(2)
        with col5:
            confirmed_by = st.text_input("VERIFIED BY (FULL NAME)", placeholder="e.g. John Smith")
        with col6:
            confirmed_post = st.selectbox("MANAGEMENT DESIGNATION", POST_OPTIONS)

        st.markdown("<div class='pos-section-title'>📎 SUPPORTING DOCUMENTS & REMARKS</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("UPLOAD CLOSING RECEIPT / PDF / AUDIT SHEET", type=["pdf", "png", "jpg", "jpeg", "eml"])
        notes = st.text_area("CLOSING REMARKS / VARIANCE NOTES", placeholder="Type any additional remarks or explanations here...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.button("💾 SUBMIT MONTH-END CLOSING RECORD")
        
        if submit_btn:
            if not prism_id_input.strip() or not hotel_name.strip():
                st.error("❌ Property ID and Hotel Name are mandatory.")
            else:
                url = ""
                if uploaded_file:
                    try:
                        file_bytes = uploaded_file.read()
                        file_path = f"{prism_id_input.strip().upper()}/{month_year}_{uploaded_file.name}"
                        supabase.storage.from_("month_end_attachments").upload(file_path, file_bytes)
                        url = supabase.storage.from_("month_end_attachments").get_public_url(file_path)
                    except Exception as upload_err:
                        st.warning(f"Storage Notice: {str(upload_err)}")
                
                # Payload perfectly matched with your Supabase column schema
                payload = {
                    "submitted_by": st.session_state.username,
                    "prism_id": prism_id_input.strip().upper(),
                    "hotel_name": hotel_name,
                    "region": region,
                    "month_year": month_year,
                    "petty_cash_expense": petty_cash_expense,
                    "total_monthly_expense": petty_cash_expense,
                    "closing_balance": closing_balance,
                    "closing_cash_balance": closing_balance,
                    "fine_amount": 0.0,
                    "confirmed_by": confirmed_by,
                    "confirmed_post": confirmed_post,
                    "notes": notes,
                    "attachment_url": url,
                    "mail_proof_url": url,
                    "status": "Submitted"
                }
                
                try:
                    supabase.table("month_end_cash_tracker").insert(payload).execute()
                    st.success("✅ MONTH-END CLOSING RECORDED & STORED SUCCESSFULLY IN DATABASE!")
                except Exception as db_err:
                    st.error(f"❌ Database Insertion Error: {str(db_err)}")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- 2. CLOSING OVERVIEW & LEDGER -----------------
elif page == "Closing Overview & Ledger":
    render_header()
    st.markdown("<h3 style='color:#1e3a8a; font-family: Segoe UI, sans-serif;'>📊 MONTH-END CASH & EXPENSE LEDGER OVERVIEW</h3>", unsafe_allow_html=True)
    df = fetch_closing_records()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No closing records found in ledger.")

# ----------------- 3. AUDIT & STATUS MANAGEMENT -----------------
elif page == "Audit & Status Management":
    render_header()
    st.markdown("<h3 style='color:#1e3a8a; font-family: Segoe UI, sans-serif;'>⚙️ CLOSING AUDIT & STATUS PANEL</h3>", unsafe_allow_html=True)
    df = fetch_closing_records()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No closing records available for audit.")

# ----------------- 4. MASTER REPORTS & PENDING TRACKER -----------------
elif page == "Master Reports & Pending":
    render_header()
    st.markdown("<h3 style='color:#1e3a8a; font-family: Segoe UI, sans-serif;'>📥 MASTER HOTEL REPORT & MISSING DATA TRACKER</h3>", unsafe_allow_html=True)
    
    selected_month = st.selectbox("SELECT MONTH-YEAR FOR STATUS AUDIT", MONTH_OPTIONS, index=8)
    
    properties_df = fetch_hotel_master()
    entries_df = fetch_closing_records()
    
    if not properties_df.empty:
        if not entries_df.empty and "month_year" in entries_df.columns and "prism_id" in entries_df.columns:
            month_entries = entries_df[entries_df["month_year"] == selected_month]
            submitted_ids = set(month_entries["prism_id"].astype(str).str.strip().str.upper())
        else:
            submitted_ids = set()

        report_rows = []
        for _, row in properties_df.iterrows():
            p_id = str(row.get("prism_id", "")).strip().upper()
            p_name = row.get("property_name", "")
            p_region = row.get("property_region", "")
            
            is_submitted = p_id in submitted_ids
            status_label = "Submitted ✅" if is_submitted else "Pending / Missing ❌"
            
            submitted_by = ""
            closing_balance = 0.0
            if is_submitted and not entries_df.empty:
                matched_row = month_entries[month_entries["prism_id"].astype(str).str.strip().str.upper() == p_id]
                if not matched_row.empty:
                    submitted_by = matched_row.iloc[0].get("submitted_by", "")
                    closing_balance = matched_row.iloc[0].get("closing_balance", 0.0)

            report_rows.append({
                "PRISM ID": p_id,
                "Property Name": p_name,
                "Region": p_region,
                "Month-Year": selected_month,
                "Status": status_label,
                "Closing Balance": closing_balance,
                "Submitted By": submitted_by
            })
        
        report_df = pd.DataFrame(report_rows)
        
        total_hotels = len(report_df)
        submitted_count = len(report_df[report_df["Status"] == "Submitted ✅"])
        pending_count = total_hotels - submitted_count
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Master Properties", total_hotels)
        m2.metric("Submitted Closings", submitted_count, delta=f"{int((submitted_count/total_hotels)*100)}%" if total_hotels > 0 else "0%")
        m3.metric("Pending / Missing Data", pending_count, delta=f"-{pending_count}" if pending_count > 0 else "0", delta_color="inverse")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(report_df, use_container_width=True)
        
        csv = report_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DOWNLOAD MASTER CLOSING REPORT (CSV)", csv, f"master_closing_status_report_{selected_month}.csv", "text/csv")
    else:
        st.warning("⚠️ No properties found in the 'hotel_master' table.")
