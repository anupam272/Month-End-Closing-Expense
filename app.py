import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client, Client
import streamlit.components.v1 as components

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

st.set_page_config(page_title="PRISM - Petty Cash Portal", page_icon="📝", layout="wide")

# Modern Executive UI Design & Styling
st.markdown("""
    <style>
    .stApp { 
        background-color: #f1f5f9; 
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif; 
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden !important;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Top Brand Bar */
    .brand-header-flex {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-top: 5px;
        margin-bottom: 15px;
    }

    .prism-box-logo {
        font-family: 'Arial Black', sans-serif;
        font-size: 24px;
        font-weight: 900;
        letter-spacing: 1.5px;
        color: #0f172a;
        border: 2px solid #0f172a;
        border-radius: 8px;
        padding: 4px 14px;
        line-height: 1;
        display: inline-block;
        background: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .portal-title-text {
        font-size: 22px;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
        line-height: 1.2;
    }

    /* Sidebar Styling */
    .sidebar-prism-logo {
        font-family: 'Arial Black', sans-serif;
        font-size: 24px;
        font-weight: 900;
        letter-spacing: 1px;
        color: #ffffff;
        border: 2px solid #ffffff;
        border-radius: 6px;
        padding: 4px 14px;
        line-height: 1;
        display: inline-block;
        margin-bottom: 8px;
    }

    section[data-testid="stSidebar"] { 
        background-color: #0f172a; 
        color: #ffffff; 
    }
    section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { 
        color: #94a3b8 !important; 
    }
    
    .sidebar-subtitle {
        color: #94a3b8 !important;
        font-size: 13px;
        margin-bottom: 20px;
    }

    /* Form Container Card */
    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 32px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
    }

    /* Input Field Labels */
    .stTextInput > label, .stSelectbox > label, .stNumberInput > label, .stDateInput > label, .stTextArea > label, .stFileUploader > label {
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 13.5px !important;
    }
    
    /* Input Box Styles */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stDateInput input {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #f8fafc !important;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within, .stNumberInput input:focus {
        border-color: #2563eb !important;
        background-color: #ffffff !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }

    /* Primary Buttons */
    .stButton>button {
        background-color: #2563eb;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 24px;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }

    /* Section Headers */
    .section-header-title {
        color: #1e293b;
        font-weight: 700;
        font-size: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None

# Master Hotel Mapping Dictionary for instant fallback fetch
HOTEL_MASTER = {
    "DEFRAM001": {"name": "Frampton Hotel", "region": "UK"},
    "DEFRAM002": {"name": "Grand Central London", "region": "UK"},
    "DEFRAM003": {"name": "Belgrave House Hotel", "region": "UK"},
    "DEEUR001": {"name": "Amsterdam City Centre", "region": "Europe"},
    "DEEUR002": {"name": "Paris Opera Stay", "region": "Europe"}
}

def fetch_closing_records():
    try:
        res = supabase.table("month_end_cash_tracker").select("*").order("id", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# Smart Auto-Fetch Function (Database + Master Dict Fallback)
def get_property_details(prism_id):
    clean_id = str(prism_id).strip().upper()
    if not clean_id:
        return "", "UK"
    
    # 1. Try Supabase lookup
    try:
        res = supabase.table("month_end_cash_tracker").select("hotel_name, region").eq("prism_id", clean_id).limit(1).execute()
        if res.data and len(res.data) > 0 and res.data[0].get("hotel_name"):
            return res.data[0].get("hotel_name", ""), res.data[0].get("region", "UK")
    except Exception:
        pass
        
    # 2. Try Master Dictionary Fallback
    if clean_id in HOTEL_MASTER:
        return HOTEL_MASTER[clean_id]["name"], HOTEL_MASTER[clean_id]["region"]
        
    return "", "UK"

# Real-time Clock Component
live_clock_html = """
<div id="clock-container" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13.5px; font-weight: 600; color: #2563eb; display: flex; align-items: center; gap: 6px; margin-bottom: -5px;">
    <span>📅</span> <span id="live-clock">Loading time...</span>
</div>

<script>
function updateClock() {
    const now = new Date();
    const options = { day: '2-digit', month: 'short', year: 'numeric' };
    const dateStr = now.toLocaleDateString('en-GB', options);
    
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12;
    const hoursStr = String(hours).padStart(2, '0');

    const formattedTime = dateStr + ", " + hoursStr + ":" + minutes + ":" + seconds + " " + ampm;
    document.getElementById('live-clock').innerText = formattedTime;
}
setInterval(updateClock, 1000);
updateClock();
</script>
"""

# Sidebar Section
with st.sidebar:
    st.markdown("<div class='sidebar-prism-logo'>PRISM</div>", unsafe_allow_html=True)
    if not st.session_state.authenticated:
        st.markdown("<div class='sidebar-subtitle'>Please log in to access system modules.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"👤 **User:** {st.session_state.username}", unsafe_allow_html=True)
        st.markdown(f"🔑 **Role:** {st.session_state.user_role}", unsafe_allow_html=True)
        st.markdown("---")
        page = st.sidebar.radio("Navigation Menu", [
            "Closing Overview & Ledger", 
            "Submit Month-End Entry", 
            "Audit & Status Update", 
            "Month-End Reports"
        ])
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

# Login Screen
if not st.session_state.authenticated:
    components.html(live_clock_html, height=25)
    st.markdown("""
        <div class="brand-header-flex">
            <div class="prism-box-logo">PRISM</div>
            <div class="portal-title-text">Petty Cash Management Portal</div>
        </div>
        <hr style="margin-top: 0; margin-bottom: 35px; border: 0; border-top: 1px solid #cbd5e1;">
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<h3 style='margin-bottom:20px; color:#0f172a; font-size:20px;'>🔒 Secure Sign In</h3>", unsafe_allow_html=True)
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                try:
                    res = supabase.table("userstb").select("*").eq("username", user_input.strip()).execute()
                    if res.data and str(res.data[0].get("password", "")).strip() == pass_input.strip():
                        st.session_state.authenticated = True
                        st.session_state.username = res.data[0]["username"]
                        st.session_state.user_role = res.data[0].get("role", "User")
                        st.rerun()
                    else:
                        st.error("Invalid Credentials!")
                except Exception as err:
                    st.error(f"Error: {str(err)}")
    st.stop()

# Dynamic Options
REGION_OPTIONS = ["UK", "Europe"]
POST_OPTIONS = ["GM", "CGM", "Reception", "Host", "Mice", "Accounts", "PPM", "Other"]
MONTH_OPTIONS = ["Jan-2026", "Feb-2026", "Mar-2026", "Apr-2026", "May-2026", "Jun-2026", "Jul-2026", "Aug-2026", "Sep-2026", "Oct-2026", "Nov-2026", "Dec-2026"]

if page == "Closing Overview & Ledger":
    components.html(live_clock_html, height=25)
    st.markdown("### 📊 Petty Cash Ledger")
    df = fetch_closing_records()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records found.")

elif page == "Submit Month-End Entry":
    components.html(live_clock_html, height=25)
    st.markdown("### 📝 Submit Cash Entry")
    
    # Property ID Outside Form with automatic On-Change Trigger
    prism_id_input = st.text_input(
        "PRISM Property ID", 
        key="prism_search", 
        placeholder="Type PRISM Property ID (e.g., DEFRAM001) and press Enter...",
    )

    auto_hotel_name, auto_region = get_property_details(prism_id_input)

    with st.form("cash_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            hotel_name = st.text_input("Hotel Name", value=auto_hotel_name, placeholder="Auto-filled or enter manually")
            region_idx = REGION_OPTIONS.index(auto_region) if auto_region in REGION_OPTIONS else 0
            region = st.selectbox("Region", REGION_OPTIONS, index=region_idx)
            month_year = st.selectbox("Month-Year", MONTH_OPTIONS)
            closing_date = st.date_input("Closing Date", date.today())
            
        with col2:
            petty_cash_expense = st.number_input("Petty Cash Expense Amount (£/€)", min_value=0.0, format="%.2f")
            closing_balance = st.number_input("Closing Balance Amount (£/€)", min_value=0.0, format="%.2f")

        st.markdown("<div class='section-header-title'>👥 Confirmation & Sign-Off Details</div>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            confirmed_by = st.text_input("Confirmation By (Person Name)", placeholder="Enter full name")
        with col4:
            confirmed_post = st.selectbox("Post / Designation", POST_OPTIONS)

        st.markdown("---")
        uploaded_file = st.file_uploader("Upload Attachment (PDF, Image, Mail Receipt)", type=["pdf", "png", "jpg", "jpeg", "eml"])
        notes = st.text_area("Additional Notes / Remarks", placeholder="Enter any extra details or explanation...")
        
        submit_btn = st.form_submit_button("Submit Cash Entry")
        
        if submit_btn:
            if not prism_id_input.strip():
                st.error("❌ PRISM Property ID is required.")
            else:
                url = ""
                if uploaded_file:
                    try:
                        file_bytes = uploaded_file.read()
                        file_path = f"{prism_id_input.strip()}/{month_year}_{uploaded_file.name}"
                        supabase.storage.from_("month_end_attachments").upload(file_path, file_bytes)
                        url = supabase.storage.from_("month_end_attachments").get_public_url(file_path)
                    except Exception as upload_err:
                        st.warning(f"Attachment alert: {str(upload_err)}")
                
                payload = {
                    "created_at": datetime.now().isoformat(),
                    "submitted_by": st.session_state.username,
                    "prism_id": prism_id_input.strip().upper(),
                    "hotel_name": hotel_name,
                    "region": region,
                    "month_year": month_year,
                    "closing_date": str(closing_date),
                    "petty_cash_expense": petty_cash_expense,
                    "closing_balance": closing_balance,
                    "amount": closing_balance,
                    "confirmed_by": confirmed_by,
                    "confirmed_post": confirmed_post,
                    "notes": notes,
                    "attachment_url": url,
                    "status": "Submitted"
                }
                
                try:
                    supabase.table("month_end_cash_tracker").insert(payload).execute()
                    st.success("✅ Cash entry submitted successfully!")
                except Exception as db_err:
                    st.error(f"❌ Database error: {str(db_err)}")

elif page == "Audit & Status Update":
    components.html(live_clock_html, height=25)
    st.markdown("### ⚙️ Audit & Status Management")
    df = fetch_closing_records()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records to audit.")

elif page == "Month-End Reports":
    components.html(live_clock_html, height=25)
    st.markdown("### 📥 Reports Export")
    df = fetch_closing_records()
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV Report", csv, "month_end_report.csv", "text/csv")
