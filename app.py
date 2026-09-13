import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from supabase import create_client, Client

@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("Supabase Connection Error! Secrets verify karein.")
    st.stop()

st.set_page_config(page_title="PRISM Month-End Cash Tracker", page_icon="📈", layout="wide")

# Styling
st.markdown("""
    <style>
    .stApp { background-color: #f5f6f7; font-family: "72", Arial, sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden !important;}
    header {visibility: hidden;}
    .main-header {
        font-size: 20px; font-weight: 600; color: #1d2d3e; margin-bottom: 20px; 
        border-bottom: 2px solid #0070f2; padding: 12px 16px; background-color: #ffffff;
        border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%; border-radius: 4px; font-weight: 600; background-color: #0070f2; 
        color: white; border: 1px solid #0070f2; padding: 6px 16px;
    }
    section[data-testid="stSidebar"] { background-color: #1d2d3e; color: #ffffff; }
    section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { color: #ffffff !important; }
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
    except Exception as e:
        st.error(f"Data Fetch Error: {str(e)}")
        return pd.DataFrame()

# Sidebar Navigation
st.sidebar.markdown("<h3 style='color:white;'>PRISM Cash Tracker</h3>", unsafe_allow_html=True)

if st.session_state.authenticated:
    st.sidebar.markdown(f"**User:** {st.session_state.username}<br>**Role:** {st.session_state.user_role}", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigation", [
        "Closing Overview & Ledger", 
        "Submit Month-End Entry", 
        "Audit & Status Update", 
        "Month-End Reports"
    ])
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
else:
    page = "Login"

# Login Screen
if not st.session_state.authenticated:
    st.markdown("<h2 style='color: #1d2d3e;'>PRISM Month-End Cash Tracker</h2>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### 🔐 User Login")
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")
            if submit:
                res = supabase.table("users").select("*").eq("username", user_input.strip()).execute()
                if res.data and res.data[0]["password"] == pass_input.strip():
                    st.session_state.authenticated = True
                    st.session_state.username = res.data[0]["username"]
                    st.session_state.user_role = res.data[0]["role"]
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Credentials!")
    st.stop()

REGION_OPTIONS = ["UK", "Europe"]
CATEGORY_OPTIONS = ["Petty Cash Closing Balance", "Cash at Hotel", "Vendor Cash Settlement", "Bank & Card Adjustments", "Operational Expenses"]
STATUS_OPTIONS = ["Submitted", "Under Review", "Approved", "Rejected"]

# 1. Ledger Overview
if page == "Closing Overview & Ledger":
    st.markdown("<div class='main-header'>📊 Month-End Cash Tracker Ledger & Attachments</div>", unsafe_allow_html=True)
    df = fetch_closing_records()
    
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Records", len(df))
        col2.metric("Total Closing Cash", f"€/£ {df['amount'].sum():,.2f}" if 'amount' in df.columns else "0.00")
        col3.metric("Approved Entries", len(df[df['status'] == 'Approved']) if 'status' in df.columns else 0)
        col4.metric("Pending Audits", len(df[df['status'].isin(['Submitted', 'Under Review'])]) if 'status' in df.columns else 0)
        
        st.markdown("### 📋 Property Entries")
        st.dataframe(
            df, 
            column_config={
                "attachment_url": st.column_config.LinkColumn("Attachment PDF / Mail Link")
            },
            use_container_width=True
        )
    else:
        st.info("No records found in month_end_cash_tracker.")

# 2. Entry Submission with PDF/Mail Attachment Upload
elif page == "Submit Month-End Entry":
    st.markdown("<div class='main-header'>📝 Submit Month-End Entry & Attach Receipts</div>", unsafe_allow_html=True)
    
    with st.form("cash_tracker_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            prism_id = st.text_input("Property / PRISM ID (e.g. UK_LON_01)")
            month_year = st.selectbox("Month-Year", ["Jan-2026", "Feb-2026", "Mar-2026", "Apr-2026", "May-2026", "Jun-2026", "Jul-2026", "Aug-2026", "Sep-2026", "Oct-2026", "Nov-2026", "Dec-2026"])
            clock_in = st.time_input("Clock In Time / Login Time", time(9, 0))
            clock_out = st.time_input("Clock Out Time / Logout Time", time(18, 0))
            region = st.selectbox("Region", REGION_OPTIONS)
            
        with col2:
            category = st.selectbox("Expense Category", CATEGORY_OPTIONS)
            amount = st.number_input("Closing Cash Amount (£/€)", min_value=0.0, format="%.2f")
            ref_number = st.text_input("Voucher / Ref Number")
            closing_date = st.date_input("Closing Date", date.today())

        st.markdown("---")
        uploaded_file = st.file_uploader("📎 Upload Attachment (PDF, Email Print, Invoice JPG/PNG)", type=["pdf", "png", "jpg", "jpeg", "msg", "eml"])
        notes = st.text_area("Audit / Reconciliation Notes")
        
        submitted = st.form_submit_button("Submit Record")
        
        if submitted:
            if not prism_id or amount <= 0:
                st.error("❌ PRISM ID aur Amount add karna zaroori hai.")
            else:
                attachment_url = ""
                # Handle File Upload to Supabase Storage
                if uploaded_file is not None:
                    try:
                        file_bytes = uploaded_file.read()
                        file_path = f"{prism_id}/{month_year}_{uploaded_file.name}"
                        
                        # Storage Bucket Upload
                        supabase.storage.from_("month_end_attachments").upload(
                            path=file_path, 
                            file=file_bytes, 
                            file_options={"content-type": uploaded_file.type}
                        )
                        # Get Public Download URL
                        attachment_url = supabase.storage.from_("month_end_attachments").get_public_url(file_path)
                    except Exception as upload_err:
                        st.warning(f"⚠️ Attachment Upload Alert: File upload replace ya fail ho sakta hai ({str(upload_err)})")

                try:
                    payload = {
                        "created_at": datetime.now().isoformat(),
                        "submitted_by": st.session_state.username,
                        "prism_id": prism_id,
                        "month_year": month_year,
                        "clock_in": str(clock_in),
                        "clock_out": str(clock_out),
                        "region": region,
                        "category": category,
                        "amount": amount,
                        "ref_number": ref_number,
                        "closing_date": str(closing_date),
                        "notes": notes,
                        "attachment_url": attachment_url,
                        "status": "Submitted"
                    }
                    supabase.table("month_end_cash_tracker").insert(payload).execute()
                    st.success("✅ Entry aur Attachment successfully save ho gaye!")
                except Exception as err:
                    st.error(f"❌ Database error: {str(err)}")

# 3. Status Change & Audit Management
elif page == "Audit & Status Update":
    st.markdown("<div class='main-header'>⚙️ Audit Entry & View Attachment</div>", unsafe_allow_html=True)
    df = fetch_closing_records()
    
    if not df.empty:
        selected_id = st.selectbox("Select Record ID to Update", df["id"].tolist())
        record = df[df["id"] == selected_id].iloc[0]
        
        st.write(f"**PRISM ID:** {record.get('prism_id', 'N/A')} | **Month:** {record.get('month_year', 'N/A')} | **Amount:** {record.get('amount', 0.0)}")
        
        url = record.get("attachment_url", "")
        if url:
            st.markdown(f"📎 **Attached File:** [View / Download PDF/Mail Receipt]({url})")
        else:
            st.write("📎 **Attached File:** No attachment uploaded.")
            
        current_status = record.get("status", "Submitted")
        new_status = st.selectbox("Status Dropdown", STATUS_OPTIONS, index=STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0)
        remarks = st.text_input("Manager Notes", value=str(record.get("notes", "")))
        
        if st.button("Update Status"):
            supabase.table("month_end_cash_tracker").update({"status": new_status, "notes": remarks}).eq("id", selected_id).execute()
            st.success(f"✅ Record #{selected_id} Status update ho gaya!")
            st.rerun()
    else:
        st.info("No records available.")

# 4. Export Reports
elif page == "Month-End Reports":
    st.markdown("<div class='main-header'>📥 Export Cash Tracker Reports</div>", unsafe_allow_html=True)
    df = fetch_closing_records()
    
    if not df.empty:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("📄 Export CSV (Includes Attachment Links)", csv_data, f"Month_End_Cash_Tracker_{date.today()}.csv", "text/csv")
    else:
        st.info("No data to export.")
