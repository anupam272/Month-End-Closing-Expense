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

st.set_page_config(page_title="PRISM - POS Cash Terminal", page_icon="💳", layout="wide")

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

    /* Main Form Layout Box */
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

def get_property_details(prism_id):
    clean_id = str(prism_id).strip().upper()
    if not clean_id:
        return "", "UK"
    
    search_ids = [clean_id]
    if "_" not in clean_id and len(clean_id) > 2:
        search_ids.append(f"{clean_id[:2]}_{clean_id[2:]}")

    for target_id in search_ids:
        try:
            res = supabase.table("properties").select("property_name, property_region").eq("prism_id", target_id).limit(1).execute()
            if res.data and len(res.data) > 0:
                name = res.data[0].get("property_name", "")
                region = res.data[0].get("property_region", "UK")
                if name:
                    return name, region
        except Exception:
            pass
            
        try:
            res = supabase.table("month_end_cash_tracker").select("hotel_name, region").eq("prism_id", target_id).limit(1).execute()
            if res.data and len(res.data) > 0:
                name = res.data[0].get("hotel_name", "")
                region = res.data[0].get("region", "UK")
                if name:
                    return name, region
        except Exception:
            pass

    return "", "UK"

# POS Live Clock Bar
live_clock_html = """
<div class="pos-header-container">
    <div style="display: flex; align-items: center; gap: 14px;">
        <div class="prism-pos-badge">PRISM POS</div>
        <div style="color: #94a3b8; font-size: 14px; font-weight: 500;">Month-End Cash Entry Kiosk</div>
    </div>
    <div style="display: flex; align-items: center; gap: 20px;">
        <div class="pos-status-online">TERMINAL ACTIVE</div>
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
        st.markdown("<div style='color: #64748b; font-size: 12px;'>Sign in to access POS modules.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"👤 **Operator:** {st.session_state.username}")
        st.markdown(f"🔑 **Role:** {st.session_state.user_role}")
        st.markdown("---")
        page = st.sidebar.radio("Navigation Menu", [
            "Submit Month-End Entry", 
            "Closing Overview & Ledger", 
            "Audit & Status Update", 
            "Month-End Reports"
        ])
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

# Login Screen
if not st.session_state.authenticated:
    components.html(live_clock_html, height=75)
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<h3 style='color:#38bdf8; font-family: monospace;'>🔒 OPERATOR LOGIN</h3>", unsafe_allow_html=True)
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")
            submit = st.form_submit_button("LOGIN TO TERMINAL")
            
            if submit:
                try:
                    res = supabase.table("userstb").select("*").eq("username", user_input.strip()).execute()
                    if res.data and str(res.data[0].get("password", "")).strip() == pass_input.strip():
                        st.session_state.authenticated = True
                        st.session_state.username = res.data[0]["username"]
                        st.session_state.user_role = res.data[0].get("role", "User")
                        st.rerun()
                    else:
                        st.error("Invalid Operator Credentials!")
                except Exception as err:
                    st.error(f"Error: {str(err)}")
    st.stop()

REGION_OPTIONS = ["UK", "Europe"]
POST_OPTIONS = ["GM", "CGM", "Reception", "Host", "Mice", "Accounts", "PPM", "Other"]
MONTH_OPTIONS = ["Jan-2026", "Feb-2026", "Mar-2026", "Apr-2026", "May-2026", "Jun-2026", "Jul-2026", "Aug-2026", "Sep-2026", "Oct-2026", "Nov-2026", "Dec-2026"]

if page == "Submit Month-End Entry":
    components.html(live_clock_html, height=75)
    
    prism_id_input = st.text_input(
        "PRISM PROPERTY ID (Type & Press Enter)", 
        key="prism_search", 
        placeholder="e.g. DE_SCHO003 or DESCHO003",
    )

    auto_hotel_name, auto_region = get_property_details(prism_id_input)

    with st.form("cash_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            hotel_name = st.text_input("HOTEL NAME", value=auto_hotel_name, placeholder="Enter Property / Hotel Name")
            region_idx = REGION_OPTIONS.index(auto_region) if auto_region in REGION_OPTIONS else 0
            region = st.selectbox("REGION", REGION_OPTIONS, index=region_idx)
            month_year = st.selectbox("MONTH-YEAR", MONTH_OPTIONS)
            closing_date = st.date_input("CLOSING DATE", date.today())
            
        with col2:
            petty_cash_expense = st.number_input("PETTY CASH EXPENSE (£/€)", min_value=0.0, format="%.2f")
            closing_balance = st.number_input("CLOSING BALANCE AMOUNT (£/€)", min_value=0.0, format="%.2f")

        st.markdown("<div class='pos-section-title'>👤 CONFIRMATION & SIGN-OFF DETAILS</div>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            confirmed_by = st.text_input("CONFIRMED BY (PERSON NAME)", placeholder="Enter full name")
        with col4:
            confirmed_post = st.selectbox("POST / DESIGNATION", POST_OPTIONS)

        st.markdown("<div class='pos-section-title'>📎 ATTACHMENTS & REMARKS</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("UPLOAD ATTACHMENT (PDF / IMAGE / MAIL RECEIPT)", type=["pdf", "png", "jpg", "jpeg", "eml"])
        notes = st.text_area("ADDITIONAL REMARKS / NOTES", placeholder="Type additional notes here...")
        
        submit_btn = st.form_submit_button("⚡ SUBMIT CASH ENTRY")
        
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
                        st.warning(f"Attachment Notice: {str(upload_err)}")
                
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
                    st.success("✅ CASH ENTRY RECORDED SUCCESSFULLY!")
                except Exception as db_err:
                    st.error(f"❌ Database error: {str(db_err)}")

elif page == "Closing Overview & Ledger":
    components.html(live_clock_html, height=75)
    st.markdown("<h3 style='color:#38bdf8; font-family: monospace;'>📊 PETTY CASH LEDGER</h3>", unsafe_allow_html=True)
    df = fetch_closing_records()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records found in ledger.")

elif page == "Audit & Status Update":
    components.html(live_clock_html, height=75)
    st.markdown("<h3 style='color:#38bdf8; font-family: monospace;'>⚙️ AUDIT & STATUS MANAGEMENT</h3>", unsafe_allow_html=True)
    df = fetch_closing_records()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records available for audit.")

elif page == "Month-End Reports":
    components.html(live_clock_html, height=75)
    st.markdown("<h3 style='color:#38bdf8; font-family: monospace;'>📥 MASTER HOTEL REPORT & PENDING DATA TRACKER</h3>", unsafe_allow_html=True)
    
    selected_month = st.selectbox("SELECT MONTH-YEAR FOR SUBMISSION CHECK", MONTH_OPTIONS, index=7) # Default Sep-2026
    
    properties_df = fetch_all_properties()
    entries_df = fetch_closing_records()
    
    if not properties_df.empty:
        # Filter entries for selected month
        if not entries_df.empty and "month_year" in entries_df.columns and "prism_id" in entries_df.columns:
            month_entries = entries_df[entries_df["month_year"] == selected_month]
            submitted_ids = set(month_entries["prism_id"].astype(str).str.strip().str.upper())
        else:
            submitted_ids = set()

        # Map Master properties with submission status
        report_rows = []
        for _, row in properties_df.iterrows():
            p_id = str(row.get("prism_id", "")).strip().upper()
            p_name = row.get("property_name", "")
            p_region = row.get("property_region", "")
            
            is_submitted = p_id in submitted_ids
            status_label = "Submitted ✅" if is_submitted else "Pending / Missing ❌"
            
            # Get submitted details if available
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
        
        # Summary metrics
        total_hotels = len(report_df)
        submitted_count = len(report_df[report_df["Status"] == "Submitted ✅"])
        pending_count = total_hotels - submitted_count
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Master Properties", total_hotels)
        m2.metric("Submitted Data", submitted_count, delta=f"{int((submitted_count/total_hotels)*100)}%" if total_hotels > 0 else "0%")
        m3.metric("Pending / Missing Data", pending_count, delta=f"-{pending_count}" if pending_count > 0 else "0", delta_color="inverse")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(report_df, use_container_width=True)
        
        csv = report_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DOWNLOAD STATUS & MASTER REPORT (CSV)", csv, f"master_status_report_{selected_month}.csv", "text/csv")
    else:
        st.warning("⚠️ No properties found in the 'properties' table. Please check Supabase table name.")
