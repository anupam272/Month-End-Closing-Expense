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

st.set_page_config(page_title="PRISM - Month-End POS Terminal", page_icon="💳", layout="wide")

# POS Terminal Custom Styling & Focus Glow
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    .stApp { 
        background-color: #0f172a; 
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; 
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden !important;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    /* POS Header styling */
    .pos-header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #1e293b;
        padding: 12px 24px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .prism-pos-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 2px;
        color: #38bdf8;
        background: #0f172a;
        border: 2px solid #38bdf8;
        border-radius: 8px;
        padding: 4px 16px;
        display: inline-block;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }

    .pos-status-online {
        font-family: 'JetBrains Mono', monospace;
        color: #10b981;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .pos-status-online::before {
        content: '';
        width: 10px;
        height: 10px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] { 
        background-color: #0b1120; 
        border-right: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { 
        color: #94a3b8 !important; 
    }

    /* Main Form & Container Box */
    div[data-testid="stForm"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
    }

    /* Input Field Labels */
    .stTextInput > label, .stSelectbox > label, .stNumberInput > label, .stDateInput > label, .stTextArea > label, .stFileUploader > label {
        font-weight: 600 !important;
        color: #cbd5e1 !important;
        font-size: 13px !important;
        letter-spacing: 0.3px;
    }
    
    /* Input Elements Default POS Style */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stDateInput input, .stTextArea textarea {
        border-radius: 10px !important;
        border: 1.5px solid #334155 !important;
        background-color: #0f172a !important;
        color: #f8fafc !important;
        font-family: 'JetBrains Mono', monospace !important;
        transition: all 0.25s ease-in-out !important;
    }

    /* Active Input Box POS Neon Highlight */
    .stTextInput input:focus, 
    .stSelectbox div[data-baseweb="select"]:focus-within, 
    .stNumberInput input:focus, 
    .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        background-color: #0b1329 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4), inset 0 0 5px rgba(56, 189, 248, 0.2) !important;
        transform: translateY(-1px);
    }

    /* POS Button Action Key */
    .stButton>button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: #ffffff;
        border: 1px solid #10b981;
        border-radius: 10px;
        font-weight: 700;
        font-size: 15px;
        letter-spacing: 1px;
        padding: 12px 24px;
        width: 100%;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
        transform: translateY(-2px);
    }

    .pos-section-title {
        color: #38bdf8;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 1px;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 15px;
        margin-bottom: 15px;
        border-bottom: 1px dashed #334155;
        padding-bottom: 8px;
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

def fetch_all_properties():
    try:
        res = supabase.table("properties").select("*").execute()
        if res.data:
            return pd.DataFrame(res.data)
    except Exception:
        pass
    return pd.DataFrame()

# POS Live Clock Bar
live_clock_html = """
<div class="pos-header-container">
    <div style="display: flex; align-items: center; gap: 14px;">
        <div class="prism-pos-badge">PRISM POS</div>
        <div style="color: #94a3b8; font-size: 14px; font-weight: 500;">UK & Europe Month-End Cash Terminal</div>
    </div>
    <div style="display: flex; align-items: center; gap: 20px;">
        <div class="pos-status-online">SECURE SESSION</div>
        <div id="live-clock" style="font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; color: #38bdf8;">Loading...</div>
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
    st.markdown("<div style='font-family: monospace; font-size: 20px; font-weight: 800; color: #38bdf8; margin-bottom: 10px;'>PRISM TERMINAL</div>", unsafe_allow_html=True)
    if not st.session_state.authenticated:
        st.markdown("<div style='color: #64748b; font-size: 12px;'>Please authenticate to access cash closing modules.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"👤 **Manager:** {st.session_state.username}")
        st.markdown(f"🔑 **Access Level:** {st.session_state.user_role}")
        st.markdown("---")
        page = st.sidebar.radio("Terminal Menu", [
            "Submit Month-End Closing", 
            "Closing Overview & Ledger", 
            "Audit & Status Management", 
            "Master Reports & Pending"
        ])
        if st.sidebar.button("🔒 End Terminal Session"):
            st.session_state.authenticated = False
            st.rerun()

# ----------------- UPGRADED MANAGER LOGIN SCREEN -----------------
if not st.session_state.authenticated:
    components.html(live_clock_html, height=75)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("pos_login_form"):
            st.markdown("""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <h2 style='color:#38bdf8; font-family: monospace; margin-bottom: 5px;'>🔐 TERMINAL LOGIN</h2>
                    <p style='color:#94a3b8; font-size: 13px;'>Enter manager credentials to access cash closing system</p>
                </div>
            """, unsafe_allow_html=True)
            
            user_input = st.text_input("MANAGER USERNAME", placeholder="e.g. admin or finance_uk")
            pass_input = st.text_input("SECURE PASSWORD", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            login_submit = st.form_submit_button("🚀 AUTHORIZE & OPEN TERMINAL")
            
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
    components.html(live_clock_html, height=75)
    
    st.markdown("<h4 style='color: #38bdf8; font-family: monospace;'>⚡ MONTH-END CASH CLOSING WIZARD</h4>", unsafe_allow_html=True)
    st.markdown("<div style='color: #94a3b8; font-size: 13px; margin-bottom: 15px;'>Enter PRISM Property ID, Hotel Name, and Region manually below.</div>", unsafe_allow_html=True)

    with st.form("cash_closing_form", clear_on_submit=False):
        st.markdown("<div class='pos-section-title'>🏢 PROPERTY & PERIOD IDENTIFICATION</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            prism_id_input = st.text_input("PRISM PROPERTY ID (MANUAL ENTRY)", placeholder="e.g. UK001 or LONHOTEL")
            hotel_name = st.text_input("HOTEL NAME", placeholder="e.g. OYO Townhouse London")
            region = st.selectbox("OPERATING REGION", REGION_OPTIONS)
            
        with col2:
            month_year = st.selectbox("CLOSING MONTH-YEAR", MONTH_OPTIONS, index=8) # Default Sep'26
            closing_date = st.date_input("REPORTING DATE", date.today())

        st.markdown("<div class='pos-section-title'>💰 CASH RECONCILIATION & CLOSING FIGURES</div>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            petty_cash_expense = st.number_input("TOTAL PETTY CASH EXPENSE (£/€)", min_value=0.0, format="%.2f", value=0.0)
        with col4:
            closing_balance = st.number_input("FINAL CLOSING BALANCE AMOUNT (£/€)", min_value=0.0, format="%.2f", value=0.0)

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
                    st.success("✅ MONTH-END CLOSING RECORDED & STORED SUCCESSFULLY IN DATABASE!")
                except Exception as db_err:
                    st.error(f"❌ Database Insertion Error: {str(db_err)}")

# ----------------- 2. CLOSING OVERVIEW & LEDGER -----------------
elif page == "Closing Overview & Ledger":
    components.html(live_clock_html, height=75)
    st.markdown("<h3 style='color:#38bdf8; font-family: monospace;'>📊 MONTH-END CASH LEDGER OVERVIEW</h3>", unsafe_allow_html=True)
    df = fetch_closing_records()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No closing records found in ledger.")

# ----------------- 3. AUDIT & STATUS MANAGEMENT -----------------
elif page == "Audit & Status Management":
    components.html(live_clock_html, height=75)
    st.markdown("<h3 style='color:#38bdf8; font-family: monospace;'>⚙️ CLOSING AUDIT & STATUS PANEL</h3>", unsafe_allow_html=True)
    df = fetch_closing_records()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No closing records available for audit.")

# ----------------- 4. MASTER REPORTS & PENDING TRACKER -----------------
elif page == "Master Reports & Pending":
    components.html(live_clock_html, height=75)
    st.markdown("<h3 style='color:#38bdf8; font-family: monospace;'>📥 MASTER HOTEL REPORT & MISSING DATA TRACKER</h3>", unsafe_allow_html=True)
    
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
