import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io
import os
import zipfile
import json
import uuid

# --- CONFIGURATION & SETUP ---
ST_PAGE_TITLE = "Purchase Tracker"
ST_PAGE_ICON = "📊"

# Detect Environment
# We default to False (Web Mode) unless explicitly set to True
IS_LOCAL_MODE = os.environ.get("PURCHASE_TRACKER_LOCAL", "False").lower() == "true"

# Default Configuration
config = {
    "csv_path": "purchase_history.csv",
    "currency_symbol": "$",
    "accent_color": "#818CF8",
    "categories": [],
    "methods": ["Credit Card", "Debit Card", "Cash", "Transfer", "Other"]
}

# Load Local Settings
SETTINGS_FILE = "settings.json"
if IS_LOCAL_MODE:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                saved_config = json.load(f)
                config.update(saved_config)
        except Exception as e:
            print(f"Error loading settings: {e}")

# Page Config
st.set_page_config(
    page_title=ST_PAGE_TITLE,
    page_icon=ST_PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME & CSS (HabitKit Style) ---
# Pitch Black background, High Contrast Cards
st.markdown(f"""
    <style>
    /* Main Background */
    .stApp {{
        background-color: #000000;
        color: #FFFFFF;
    }}
    
    /* Card/Container Styling */
    div.css-1r6slb0, div.stForm, div[data-testid="stMetric"], div[data-testid="stExpander"] {{
        background-color: #121212; /* Slightly lighter than pitch black */
        border: 1px solid #2A2A2A;
        border-radius: 12px;
        padding: 16px;
    }}
    
    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stDateInput input {{
        background-color: #1E1E1E !important;
        color: white !important;
        border: 1px solid #333333 !important;
        border-radius: 8px;
    }}
    
    /* Buttons */
    button[kind="primary"] {{
        background-color: {config['accent_color']} !important;
        border: none;
        color: white !important;
        font-weight: 600;
        border-radius: 8px;
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: #0A0A0A;
        border-right: 1px solid #222222;
    }}
    
    /* Headers */
    h1, h2, h3, h4 {{
        font-family: 'Inter', sans-serif;
        color: #FFFFFF !important;
    }}
    
    /* Dataframe Header */
    thead tr th {{
        background-color: #1E1E1E !important;
        color: #AAAAAA !important;
    }}
    
    /* Bigger Metrics */
    div[data-testid="stMetricValue"] {{
        font-size: 36px !important;
        font-weight: 700 !important;
    }}
    
    /* Maximize Dropdown Height for Categories */
    ul[data-testid="stSelectboxVirtualDropdown"] {{
        max-height: 600px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Vibrant Palette for Charts
VIBRANT_COLORS = [
    "#F87171", "#FB923C", "#FACC15", "#4ADE80", "#60A5FA", 
    "#818CF8", "#A78BFA", "#F472B6", "#FB7185", "#2DD4BF"
]

# --- SCHEMA DEFINITION ---
# Dropped 'N' column. We will manage data without it.
COLUMNS = ["Date", "Description", "Amount", "Necessity", "Method", "Category", "Tag", "More info"]

# --- HELPER FUNCTIONS ---
def clean_amount(val):
    """Parses currency strings like '$1,200.00' into floats."""
    if pd.isna(val): return 0.0
    if isinstance(val, (int, float)): return float(val)
    if isinstance(val, str):
        cleaned = val.replace(config['currency_symbol'], '').replace('$', '').replace(',', '').strip()
        if not cleaned: return 0.0
        try: return float(cleaned)
        except: return 0.0
    return 0.0

def load_dataset(file_source):
    """Loads and standardizes dataset from file object or path."""
    try:
        df = pd.read_csv(file_source)
        
        # 1. Clean Date
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']) # Drop invalid dates
        
        # 2. Standardize Schema
        # Remove legacy 'N' if exists
        if 'N' in df.columns:
            df = df.drop(columns=['N'])
            
        # Add missing columns
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
                
        # 3. Type Conversion
        if 'Category' in df.columns: df['Category'] = df['Category'].astype(str)
        if 'Method' in df.columns: df['Method'] = df['Method'].astype(str)
        
        # 4. Return as formatted strings for UI (Date)
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        
        return df[COLUMNS]
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame(columns=COLUMNS)

def save_local(df):
    """Saves DataFrame to local CSV path defined in config."""
    if IS_LOCAL_MODE:
        try:
            path = config['csv_path']
            # Create dir if not exists
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True) if os.path.dirname(path) else None
            df.to_csv(path, index=False)
            return True
        except Exception as e:
            st.error(f"Save failed: {e}")
            return False
    return False

def save_settings():
    """Saves current config to settings.json."""
    if IS_LOCAL_MODE:
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            st.error(f"Settings save failed: {e}")

# --- SESSION STATE INIT ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=COLUMNS)
if 'categories' not in st.session_state:
    st.session_state.categories = list(config['categories'])
if 'methods' not in st.session_state:
    st.session_state.methods = list(config['methods'])
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# --- AUTO-LOAD (LOCAL MODE) ---
if IS_LOCAL_MODE and not st.session_state.initialized:
    if os.path.exists(config['csv_path']):
        loaded_df = load_dataset(config['csv_path'])
        if not loaded_df.empty:
            st.session_state.data = loaded_df
            # Update filters/lists based on data
            unique_cats = [x for x in loaded_df['Category'].dropna().unique() if x != 'nan']
            st.session_state.categories = list(set(st.session_state.categories + unique_cats))
            
            unique_methods = [x for x in loaded_df['Method'].dropna().unique() if x != 'nan']
            st.session_state.methods = list(set(st.session_state.methods + unique_methods))
            
    st.session_state.initialized = True

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 📊 Purchase Tracker")
    
    # Mode Indicator
    if IS_LOCAL_MODE:
        st.caption(f"📍 Local Mode | Path: `{config['csv_path']}`")
    else:
        st.caption("☁️ Web Mode (Ephemeral)")

    # 1. DATA I/O
    with st.expander("💾 Data Management", expanded=not st.session_state.initialized):
        # Import
        uploaded_file = st.file_uploader("Import CSV", type=['csv'])
        if uploaded_file:
            if st.button("Load Imported Data", use_container_width=True):
                df_new = load_dataset(uploaded_file)
                st.session_state.data = df_new
                
                # Update Categories
                new_cats = [x for x in df_new['Category'].dropna().unique() if x != 'nan']
                st.session_state.categories = list(set(st.session_state.categories + new_cats))
                
                if IS_LOCAL_MODE:
                    save_local(st.session_state.data)
                    st.toast("Data imported & saved!", icon="💾")
                
                st.session_state.initialized = True
                st.rerun()

        # Export
        if not st.session_state.data.empty:
            csv = st.session_state.data.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export CSV",
                csv,
                "purchase_history.csv",
                "text/csv",
                key='download-csv',
                use_container_width=True
            )
            
        # Open Source Download (Web Only)
        if not IS_LOCAL_MODE:
            st.markdown("---")
            st.markdown("**Run Locally**")
            st.caption("Download the source code to run this app privately on your machine.")
            
            # Generate ZIP in memory
            def create_zip():
                with open(__file__, "r") as f:
                    source_code = f.read()
                # Force local mode in the downloaded version
                source_code_local = source_code.replace(
                    'IS_LOCAL_MODE = os.environ.get("PURCHASE_TRACKER_LOCAL", "False").lower() == "true"',
                    'IS_LOCAL_MODE = True'
                )
                reqs = "streamlit\npandas\nplotly\n"
                readme = "# Purchase Tracker (Local)\n1. Install Python\n2. pip install -r requirements.txt\n3. streamlit run app.py"
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    zf.writestr("app.py", source_code_local)
                    zf.writestr("requirements.txt", reqs)
                    zf.writestr("README.txt", readme)
                return zip_buffer.getvalue()

            st.download_button(
                label="📥 Download .zip",
                data=create_zip(),
                file_name="purchase_tracker_local.zip",
                mime="application/zip",
                use_container_width=True
            )

    # --- VIEW CONTROLS ---
    st.markdown("### Controls")
    # Toggle for View - DEFINED EARLY
    show_log = st.toggle("View Log / Edit", value=False)
    
    view_option = "Dashboard" if not show_log else "Log / Edit"
    
    # Filters
    st.markdown("### Filters")
    time_filter = st.selectbox(
        "Period", 
        ["All Time", "This Month", "Last 14 Days", "Last 30 Days", "Last 60 Days", "Last 90 Days", "Last 180 Days", "Last 365 Days", "This Year"]
    )
    
    selected_cats = st.multiselect("Categories", st.session_state.categories, default=st.session_state.categories)

    # 3. SETTINGS (Local Only)
    if IS_LOCAL_MODE:
        with st.expander("⚙️ Settings"):
            st.markdown("#### App Configuration")
            new_accent = st.color_picker("Accent Color", config['accent_color'])
            if new_accent != config['accent_color']:
                config['accent_color'] = new_accent
                save_settings()
                st.rerun()
                
            new_path = st.text_input("CSV Path", config['csv_path'])
            if new_path != config['csv_path']:
                config['csv_path'] = new_path
                save_settings()
                st.rerun()
                
            st.markdown("---")
            st.markdown("#### Lists")
            new_cat_input = st.text_input("Add Category")
            if st.button("Add"):
                if new_cat_input and new_cat_input not in st.session_state.categories:
                    st.session_state.categories.append(new_cat_input)
                    config['categories'] = st.session_state.categories
                    save_settings()
                    st.rerun()


# --- MAIN LOGIC ---

# HELP DIALOG
if st.session_state.get('show_help', False):
    @st.dialog("👋 Welcome to Purchase Tracker")
    def help_dialog():
        st.info("This is a **privacy-first**, **account-free** finance tracker.")
        st.markdown("#### 🔒 Privacy")
        st.write("No data is stored on our servers. In Web mode, data exists only in RAM.")
        st.markdown("#### 💾 Data")
        st.success("1. Log purchases.\n2. Export CSV before closing.\n3. Import CSV to resume.")
        if st.button("Got it!", use_container_width=True):
            st.session_state.show_help = False
            st.rerun()
    help_dialog()

# FILTER DATA
df_filtered = st.session_state.data.copy()
if not df_filtered.empty:
    df_filtered['Date_dt'] = pd.to_datetime(df_filtered['Date'])
    
    # Sort by date DESC by default for Log/Dashboard consistency
    df_filtered = df_filtered.sort_values('Date_dt', ascending=False)
    
    # Time Filter
    today = datetime.now()
    if time_filter == "This Month":
        df_filtered = df_filtered[df_filtered['Date_dt'].dt.to_period('M') == today.strftime('%Y-%m')]
    elif time_filter == "Last 14 Days":
        cutoff = today - timedelta(days=14)
        df_filtered = df_filtered[df_filtered['Date_dt'] >= cutoff]
    elif time_filter == "Last 30 Days":
        cutoff = today - timedelta(days=30)
        df_filtered = df_filtered[df_filtered['Date_dt'] >= cutoff]
    elif time_filter == "Last 60 Days":
        cutoff = today - timedelta(days=60)
        df_filtered = df_filtered[df_filtered['Date_dt'] >= cutoff]
    elif time_filter == "Last 90 Days":
        cutoff = today - timedelta(days=90)
        df_filtered = df_filtered[df_filtered['Date_dt'] >= cutoff]
    elif time_filter == "Last 180 Days":
        cutoff = today - timedelta(days=180)
        df_filtered = df_filtered[df_filtered['Date_dt'] >= cutoff]
    elif time_filter == "Last 365 Days":
        cutoff = today - timedelta(days=365)
        df_filtered = df_filtered[df_filtered['Date_dt'] >= cutoff]
    elif time_filter == "This Year":
        df_filtered = df_filtered[df_filtered['Date_dt'].dt.year == today.year]
    elif time_filter == "Custom Days":
        cutoff = today - timedelta(days=custom_days)
        df_filtered = df_filtered[df_filtered['Date_dt'] >= cutoff]
        
    # Category Filter
    if selected_cats:
        df_filtered = df_filtered[df_filtered['Category'].isin(selected_cats)]


# --- TOP BAR & VIEW ROUTING ---
c_title, c_help = st.columns([20, 1]) # Push help to far right
with c_title:
    if not show_log:
        st.title("Dashboard")
    else:
        st.title("Transaction Log")
with c_help:
    # Use a simpler button character or icon
    if st.button("❓", help="Help & Information"):
        st.session_state.show_help = True

# --- VIEW: DASHBOARD ---
if not show_log:
    if st.session_state.data.empty:
        st.info("👋 No data found. Import a CSV or start adding transactions!")
        
    # INPUT FORM
    with st.expander("➕ Log Transaction", expanded=True):
        with st.form("entry_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            desc = c1.text_input("Description")
            amt = c2.text_input("Amount", placeholder="0.00")
            date = c3.date_input("Date", datetime.today())
            
            c4, c5, c6 = st.columns(3)
            cat = c4.selectbox("Category", st.session_state.categories)
            method = c5.selectbox("Method", st.session_state.methods)
            nec = c6.slider("Necessity (1-5)", 1, 5, 3)
            
            if st.form_submit_button("Log Entry", type="primary", use_container_width=True):
                new_row = {
                    "Date": date.strftime('%Y-%m-%d'),
                    "Description": desc,
                    "Amount": amt,
                    "Necessity": nec,
                    "Method": method,
                    "Category": cat,
                    "Tag": "",
                    "More info": ""
                }
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
                
                if IS_LOCAL_MODE:
                    save_local(st.session_state.data)
                st.success("Saved!")
                st.rerun()

    # ANALYTICS
    if not df_filtered.empty:
        df_filtered['Amount_Val'] = df_filtered['Amount'].apply(clean_amount)
        total_spend = df_filtered['Amount_Val'].sum()
        
        # Calculate Monthly Average
        # We use the filtered period to determine the denominator, or just count unique months in the filtered data.
        # Logic: If I filter "Last 30 Days", I have 1 or 2 months. 
        # Better: Total Spend / Number of Unique Months in the selection (min 1)
        unique_months = df_filtered['Date_dt'].dt.to_period('M').nunique()
        avg_monthly = total_spend / unique_months if unique_months > 0 else total_spend
        
        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Spend", f"{config['currency_symbol']}{total_spend:,.2f}")
        k2.metric("Transactions", len(df_filtered))
        k3.metric("Avg. Transaction", f"{config['currency_symbol']}{total_spend/len(df_filtered):,.2f}")
        k4.metric("Avg. / Month", f"{config['currency_symbol']}{avg_monthly:,.2f}")
        
        # Charts
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.subheader("Spending by Category")
            cat_group = df_filtered.groupby('Category')['Amount_Val'].sum().reset_index()
            fig_pie = px.pie(cat_group, values='Amount_Val', names='Category', hole=0.5, color_discrete_sequence=VIBRANT_COLORS)
            fig_pie.update_traces(
                textinfo='percent+label',
                textfont_size=16,
                hovertemplate="<b>%{label}</b><br>%{percent}<br>$%{value:,.2f}<extra></extra>"
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                font_color="white", 
                margin=dict(t=0, b=0, l=0, r=0),
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c_right:
            st.subheader("Monthly Trend")
            df_filtered['Month'] = df_filtered['Date_dt'].dt.to_period('M').astype(str)
            time_group = df_filtered.groupby('Month')['Amount_Val'].sum().reset_index()
            fig_bar = px.bar(
                time_group, 
                x='Month', 
                y='Amount_Val', 
                color='Amount_Val', 
                color_continuous_scale=VIBRANT_COLORS,
                text='Amount_Val' # Show value inside bar
            )
            fig_bar.update_traces(
                textposition='inside',
                texttemplate='$%{y:,.0f}',
                hovertemplate="<b>%{x}</b><br>$%{y:,.2f}<extra></extra>"
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                font_color="white", 
                plot_bgcolor="rgba(0,0,0,0)", 
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# --- VIEW: LOG / EDIT ---
else:
    st.caption("Select rows to delete them.")
    
    if not df_filtered.empty:
        # Prepare for Editor
        df_edit = df_filtered.copy()
        # Add a unique ID for deletion tracking if not present (we use index here for simplicity in display)
        df_edit.insert(0, "Delete", False)
        
        edited_df = st.data_editor(
            df_edit,
            column_config={
                "Delete": st.column_config.CheckboxColumn(
                    "Delete",
                    help="Check to delete",
                    default=False,
                    width="small"
                ),
                "Amount": st.column_config.TextColumn("Amount"), # Keep as text to avoid float formatting issues during edit
            },
            hide_index=True,
            use_container_width=True,
            height=800, # Increased height for full screen feel
            num_rows="dynamic" # Allow adding rows directly in table
        )
        
        # Handle Deletions
        if edited_df['Delete'].any():
            if st.button("Confirm Deletion", type="primary"):
                # We need to find which rows in the ORIGINAL session_state.data correspond to the deleted rows.
                # Since df_filtered is a subset, index matching is tricky if we reset index.
                # BETTER APPROACH: Reconstruct the session_state.data from the edited dataframe IF no filters are applied.
                # BUT if filters ARE applied, we need robust matching.
                
                # For this iteration, we will rely on the fact that 'edited_df' preserves the index of 'df_filtered' 
                # if we didn't reset it.
                
                # Get indices of rows marked for deletion
                indices_to_drop = edited_df[edited_df['Delete']].index
                
                # Drop from main state
                st.session_state.data = st.session_state.data.drop(indices_to_drop)
                
                if IS_LOCAL_MODE:
                    save_local(st.session_state.data)
                
                st.success("Deleted!")
                st.rerun()
                
        # Handle Edits (Sync changes back)
        # Check if other columns changed
        # This is complex with partial views. 
        # For V1 of this feature, we might just restrict editing to "All Time" view or warn user.
        # But 'st.data_editor' returns the modified dataframe.
        # If we want to support full editing, we should probably update st.session_state.data 
        # with the values from edited_df, matching by index.
        
        # diff = edited_df.compare(df_edit) # This works if shapes match
    else:
        st.info("No data in current filter.")
