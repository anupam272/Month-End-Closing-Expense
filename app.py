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

# Custom Corporate Finance Theme Styling with Flexbox Header Fix
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');

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

    /* Enterprise Header Styling with Flexbox Layout */
    .pos-header-container {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        background: linear-gradient(to bottom, #f8fafc, #e2e8f0);
        padding: 12px 20px;
        border-radius: 4px;
        border: 1px solid #94a3b8;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        width: 100%;
        box-sizing: border-box;
    }

    .prism-pos-badge {
        font-family: 'Segoe UI', sans-serif;
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #1e3a8a;
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 3px;
        padding: 3px 10px;
        display: inline-block;
        margin-right: 10px;
    }

    .pos-status-online {
        font-family: 'Segoe UI', sans-serif;
        color: #15803d;
        font-size: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .pos-status-online::before {
        content: '';
        width: 8px;
        height: 8px;
        background-color: #16a34a;
        border-radius: 50%;
        display: inline-block;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] { 
        background-color: #e2e8f0; 
        border-right: 1px solid #cbd5e1;
    }
    section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { 
        color: #1e293b !important; 
    }

    /* Main Form & Container Box */
    div[data-testid="stForm"] {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 25px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    /* Input Field Labels */
    .stTextInput > label, .stSelectbox > label, .stNumberInput > label, .stDateInput > label, .stTextArea > label, .stFileUploader > label {
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 12px !important;
    }
    
    /* Input Elements Styling */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stDateInput input, .stTextArea textarea {
        border-radius: 3px !important;
        border: 1px solid #94a3b8 !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-family: 'Segoe UI', sans-serif !important;
    }

    /* Active Input Focus */
    .stTextInput input:focus, 
    .stSelectbox div[data-baseweb="select"]:focus-within, 
    .stNumberInput input:focus, 
    .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
    }

    /* Action Button */
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

def fetch_all_properties():
    try:
        res = supabase.table("properties").select("*").execute()
        if res.data:
            return pd.DataFrame(res.data)
    except Exception:
        pass
    return pd.DataFrame()

# Live Clock Bar with Robust Left-Right Alignment
live_clock_html = """
<div class="pos-header-container">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span class="prism-pos-badge">PRISM FINANCE</span>
        <span class="pos-status-online">PORTAL ACTIVE</span>
    </div>
    <div style="display: flex; align-items: center; gap: 15px; text-align: right;">
        <span style="color: #334155; font-size: 13px; font-weight: 600;">UK & Europe Month-End Cash & Expense Portal</span>
        <span style="color: #64748b; font-size: 12px; font-weight: 600;">|</span>
        <span id="live-clock" style="font-family: 'Segoe UI', sans-serif; font-size: 12px; font-weight: 600; color: #1e293b;">Loading...</span>
    </div>
</div>

<script>
function updateClock() {
    const now = new Date();
    const options = { day: '2-digit', month: 'short', year: 'numeric' };
    const dateStr = now.toLocaleDateString('en-GB', options);
    
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    const hoursStr = String(hours).padStart(2, '0');

    document.getElementById('live-clock').innerText = dateStr + " | " + hoursStr + ":" + minutes + ":" + seconds + " " + ampm;
}
setInterval(updateClock, 1000);
updateClock();
</script>
"""

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
    components.html(live_clock_html, height=60)
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
    components.html(live_clock_html, height=60)
    
    st.markdown("<h4 style='color: #1e3a8a; font-family: Segoe UI, sans-serif;'>⚡ MONTH-END CASH & EXPENSE CLOSING WIZARD</h4>", unsafe_allow_html=True)
    st.markdown("<div style='color: #475569; font-size: 12px; margin-bottom: 12px;'>Enter PRISM Property ID, Hotel Name, and Region manually below.</div>", unsafe_allow_html=True)

    with st.form("cash_closing_form", clear_on_submit=False):
        st.markdown("<div class='pos-section-title'>🏢 PROPERTY & PERIOD IDENTIFICATION</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            prism_id_input = st.text_input("PRISM PROPERTY ID (MANUAL ENTRY)", placeholder="e.g. UK001 or LONHOTEL")
            hotel_name = st.text_input("HOTEL NAME", placeholder="e.g. OYO Townhouse London")
            region = st.selectbox("OPERATING REGION", REGION_OPTIONS)
            
        with col2:
            month_year = st.selectbox("CLOSING MONTH-YEAR", MONTH_OPTIONS, index=8) # Default Sep'26

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
        submit_btn = st.form_submit_button("💾 SUBMIT MONTH-END CLOSING RECORD")
        
        if submit_btn:
            if not prism_id_input.strip() or not hotel_name.strip():
                st.error("❌ Property ID and Hotel Name are mandatory.")
            else:
                url = ""
                if uploaded_file:
                    try:
                        file_bytes = uploaded_file.read()
                        file_path = f"{prism_id_input.strip()}/{month_year}_{uploaded_file.name}"
                        supabase.storage.from_("month_end_attachments").upload(file_path, file_bytes)
                        url = supabase.storage.from_("month_end_attachments").get_public_url(file_path)
                    except Exception as upload_err:
                        st.warning(f"Storage Notice: {str(upload_err)}")
                
                payload = {
                    "created_at": datetime.now().isoformat(),
                    "submitted_by": st.session_state.username,
                    "prism_id": prism_id_input.strip().upper(),
                    "hotel_name": hotel_name,
                    "region": region,
                    "month_year": month_year,
                    "petty_cash_expense": petty_cash_expense,
                    "closing_balance": closing_balance,
                    "confirmed_by": confirmed_by,
                    "confirmed_post": confirmed_post,
                    "notes": notes,
                    "attachment_url": url,
                    "status": "Submitted"
                }
                
                try:
                    supabase.table("month_end_cash_tracker").insert(payload).execute()
                    st.success("✅ MONTH-END CLOSING RECORDED & STORED SUCCESSFULLY IN DATABASE!")
                except Exception as db_err:
                    st.error(f"❌ Database Insertion Error: {str(db_err)}")

# ----------------- 2. CLOSING OVERVIEW & LEDGER -----------------
elif page == "Closing Overview & Ledger":
    components.html(live_clock_html, height=60)
    st.markdown("<h3 style='color:#1e3a8a; font-family: Segoe UI, sans-serif;'>📊 MONTH-END CASH & EXPENSE LEDGER OVERVIEW</h3>", unsafe_allow_html=True)
    df = fetch_closing_records()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No closing records found in ledger.")

# ----------------- 3. AUDIT & STATUS MANAGEMENT -----------------
elif page == "Audit & Status Management":
    components.html(live_clock_html, height=60)
    st.markdown("<h3 style='color:#1e3a8a; font-family: Segoe UI, sans-serif;'>⚙️ CLOSING AUDIT & STATUS PANEL</h3>", unsafe_allow_html=True)
    df = fetch_closing_records()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No closing records available for audit.")

# ----------------- 4. MASTER REPORTS & PENDING TRACKER -----------------
elif page == "Master Reports & Pending":
    components.html(live_clock_html, height=60)
    st.markdown("<h3 style='color:#1e3a8a; font-family: Segoe UI, sans-serif;'>📥 MASTER HOTEL REPORT & MISSING DATA TRACKER</h3>", unsafe_allow_html=True)
    
    selected_month = st.selectbox("SELECT MONTH-YEAR FOR STATUS AUDIT", MONTH_OPTIONS, index=8) # Default Sep'26
    
    properties_df = fetch_all_properties()
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
        st.warning("⚠️ No properties found in the 'properties' table.")
