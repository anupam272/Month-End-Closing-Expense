import streamlit as st
import pandas as pd
from datetime import datetime, date, time
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
    st.error("Supabase Connection Error! Secrets verify karein.")
    st.stop()

st.set_page_config(page_title="Petty Cash Management Portal", page_icon="📈", layout="wide")

# Custom UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden !important;}
    header {visibility: hidden;}
    
    /* PRISM Exact Logo Box Styling */
    .prism-box-logo {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-family: 'Arial Black', sans-serif;
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 1px;
        color: #1e293b;
        border: 2.5px solid #1e293b;
        border-radius: 8px;
        padding: 2px 12px;
        line-height: 1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    .sidebar-prism-logo {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-family: 'Arial Black', sans-serif;
        font-size: 24px;
        font-weight: 900;
        letter-spacing: 1px;
        color: #ffffff;
        border: 2px solid #ffffff;
        border-radius: 6px;
        padding: 4px 12px;
        line-height: 1;
        margin-bottom: 8px;
    }

    /* Portal Title Text */
    .portal-title-text {
        font-size: 24px;
        font-weight: 600;
        color: #1e293b;
        margin-left: 15px;
    }

    /* Sidebar Theme */
    section[data-testid="stSidebar"] { background-color: #1c2b36; color: #ffffff; }
    section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { color: #94a3b8 !important; }
    .sidebar-subtitle {
        color: #94a3b8 !important;
        font-size: 13px;
        margin-bottom: 20px;
    }

    /* Form Container */
    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .stButton>button {
        background-color: #ffffff;
        color: #334155;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        font-weight: 500;
    }
    .stButton>button:hover {
        border-color: #3b82f6;
        color: #3b82f6;
    }
    </style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None

def fetch_closing_records():
    try:
        res = supabase.table("month_end_cash_tracker").select("*").order("id", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# JavaScript Real-Time Live Ticking Clock Component
live_clock_html = """
<div id="clock-container" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; font-weight: 500; color: #3b82f6; display: flex; align-items: center; gap: 6px;">
    <span>📅</span> <span id="live-clock">Loading live time...</span>
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

# Sidebar Layout
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

# Login Header Section
if not st.session_state.authenticated:
    # Live Clock Execution
    components.html(live_clock_html, height=30)
    
    # Title Header with Logo Box
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <div class="prism-box-logo">PRISM</div>
            <div class="portal-title-text">Petty Cash Management Portal</div>
        </div>
        <hr style="margin-top: 0; margin-bottom: 35px; border: 0; border-top: 1px solid #e2e8f0;">
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<h3 style='margin-bottom:20px; color:#1e293b;'>🔒 Secure Sign In</h3>", unsafe_allow_html=True)
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

# Post-Login Dynamic Dashboard Pages
REGION_OPTIONS = ["UK", "Europe"]
CATEGORY_OPTIONS = ["Petty Cash Closing Balance", "Cash at Hotel", "Vendor Cash Settlement", "Bank & Card Adjustments", "Operational Expenses"]
STATUS_OPTIONS = ["Submitted", "Under Review", "Approved", "Rejected"]

if page == "Closing Overview & Ledger":
    components.html(live_clock_html, height=30)
    st.markdown("### 📊 Petty Cash Ledger")
    df = fetch_closing_records()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records found.")

elif page == "Submit Month-End Entry":
    components.html(live_clock_html, height=30)
    st.markdown("### 📝 Submit Cash Entry")
    with st.form("cash_form"):
        col1, col2 = st.columns(2)
        with col1:
            prism_id = st.text_input("PRISM Property ID")
            month_year = st.selectbox("Month-Year", ["Jan-2026", "Feb-2026", "Mar-2026", "Apr-2026", "May-2026", "Jun-2026", "Jul-2026", "Aug-2026", "Sep-2026", "Oct-2026", "Nov-2026", "Dec-2026"])
            amount = st.number_input("Amount", min_value=0.0)
        with col2:
            region = st.selectbox("Region", REGION_OPTIONS)
            category = st.selectbox("Category", CATEGORY_OPTIONS)
            closing_date = st.date_input("Date", date.today())
        
        uploaded_file = st.file_uploader("Upload Attachment (PDF/Mail)", type=["pdf", "png", "jpg", "eml"])
        submit_btn = st.form_submit_button("Submit Entry")
        
        if submit_btn:
            url = ""
            if uploaded_file:
                try:
                    file_bytes = uploaded_file.read()
                    file_path = f"{prism_id}/{month_year}_{uploaded_file.name}"
                    supabase.storage.from_("month_end_attachments").upload(file_path, file_bytes)
                    url = supabase.storage.from_("month_end_attachments").get_public_url(file_path)
                except Exception as upload_err:
                    st.warning(f"Attachment alert: {str(upload_err)}")
            
            payload = {
                "created_at": datetime.now().isoformat(),
                "submitted_by": st.session_state.username,
                "prism_id": prism_id,
                "month_year": month_year,
                "region": region,
                "category": category,
                "amount": amount,
                "closing_date": str(closing_date),
                "attachment_url": url,
                "status": "Submitted"
            }
            supabase.table("month_end_cash_tracker").insert(payload).execute()
            st.success("Record successfully saved!")
