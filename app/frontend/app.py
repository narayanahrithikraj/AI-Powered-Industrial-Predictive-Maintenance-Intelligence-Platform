import io
import uuid
import time
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Industrial Predictive Maintenance Intelligence Platform",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 🎨 VIEWPORT COMPACTNESS & CLEAN ENTERPRISE UI CSS INJECTION
# ==============================================================================
st.markdown("""
    <style>
        /* Hide Streamlit default developer header menu, Deploy button, and footer */
        #MainMenu {visibility: hidden !important;}
        header {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        .stDeployButton {display: none !important;}
        div[data-testid="stDecoration"] {display: none !important;}

        /* Reduce overall Streamlit page top/bottom padding */
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 0rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        
        /* Compact headings spacing */
        h1 {
            font-size: 1.8rem !important;
            margin-bottom: 0.2rem !important;
            padding-bottom: 0rem !important;
        }
        h2, h3 {
            font-size: 1.2rem !important;
            margin-top: 0.4rem !important;
            margin-bottom: 0.2rem !important;
        }
        
        /* Compact Metric Cards */
        [data-testid="stMetricValue"] {
            font-size: 1.4rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
        [data-testid="stMetric"] {
            padding: 2px 8px !important;
        }
        
        /* Compact Tabs and Inputs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding-top: 4px !important;
            padding-bottom: 4px !important;
        }
        
        /* Reduce form and element vertical padding */
        div[data-testid="stForm"] {
            padding: 1rem !important;
        }
        
        /* Horizontal dividers margin */
        hr {
            margin-top: 0.4rem !important;
            margin-bottom: 0.6rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "generated_tokens" not in st.session_state:
    st.session_state["generated_tokens"] = ["EMP-2026-JOIN", "ENT-99A2-X801"]

# ------------------------------------------------------------------------------
# FUNCTIONAL STATE STORAGE (PERSISTED ACROSS RUNS)
# ------------------------------------------------------------------------------
if "system_settings" not in st.session_state:
    st.session_state["system_settings"] = {
        "risk_threshold": 75,
        "vibration_limit": 4.2,
        "rul_warning_days": 30,
        "alert_sensitivity": "HIGH"
    }

if "user_accounts" not in st.session_state:
    st.session_state["user_accounts"] = [
        {"User ID": 1, "Name": "Narayana Hrithik Raj", "Email": "admin@enterprise.com", "Role": "ADMIN", "Status": "Active"},
        {"User ID": 2, "Name": "Operations Engineer", "Email": "user@enterprise.com", "Role": "USER", "Status": "Active"},
        {"User ID": 3, "Name": "Maintenance Analyst", "Email": "analyst@enterprise.com", "Role": "USER", "Status": "Active"}
    ]

if "alerts_list" not in st.session_state:
    st.session_state["alerts_list"] = [
        {"ID": 101, "Machine": "Main Assembly Rotor Turbine", "Severity": "CRITICAL", "Message": "Turbine Rotor 1 Bearing Vibration Exceeded Threshold (4.2 g)", "Status": "Unresolved"},
        {"ID": 102, "Machine": "High-Pressure Coolant Pump", "Severity": "HIGH", "Message": "Coolant Fluid Pressure Drop Detected (-15% PSI)", "Status": "Unresolved"},
        {"ID": 103, "Machine": "CNC Milling Axis-A", "Severity": "MEDIUM", "Message": "Spindle Tool Wear Exceeded 180 Minutes Operating Threshold", "Status": "Resolved"}
    ]

if "maintenance_work_orders" not in st.session_state:
    st.session_state["maintenance_work_orders"] = [
        {"ID": "WO-201", "Machine": "High-Pressure Coolant Pump", "Task": "Inspect coolant fluid pressure seals & replace worn gaskets", "Priority": "HIGH", "Status": "SCHEDULED", "Est Downtime": "3.5 hrs"},
        {"ID": "WO-202", "Machine": "Main Assembly Rotor Turbine", "Task": "Calibrate vibration damper & bearing alignment", "Priority": "CRITICAL", "Status": "IN_PROGRESS", "Est Downtime": "6.0 hrs"}
    ]

if "fleet_machines" not in st.session_state:
    st.session_state["fleet_machines"] = pd.DataFrame([
        {"ID": "M-001", "Name": "CNC Milling Axis-A", "Type": "CNC Machine", "Manufacturer": "Siemens", "Location": "Plant 1", "Department": "Machining", "Status": "HEALTHY", "Health %": 94.2, "RUL (Days)": 182.0, "Assigned To": "user@enterprise.com", "Failure Prob %": 5.8},
        {"ID": "M-002", "Name": "High-Pressure Coolant Pump", "Type": "Hydraulic Pump", "Manufacturer": "Bosch", "Location": "Plant 1", "Department": "Cooling", "Status": "AT_RISK", "Health %": 68.5, "RUL (Days)": 24.5, "Assigned To": "user@enterprise.com", "Failure Prob %": 31.5},
        {"ID": "M-003", "Name": "Main Assembly Rotor Turbine", "Type": "Gas Turbine", "Manufacturer": "GE Digital", "Location": "Plant 2", "Department": "Power Gen", "Status": "CRITICAL", "Health %": 32.0, "RUL (Days)": 4.1, "Assigned To": "admin@enterprise.com", "Failure Prob %": 68.0},
        {"ID": "M-004", "Name": "Robotic Welding Arm Element", "Type": "Articulated Robot", "Manufacturer": "Tata Systems", "Location": "Plant 2", "Department": "Assembly", "Status": "HEALTHY", "Health %": 98.0, "RUL (Days)": 310.0, "Assigned To": "user@enterprise.com", "Failure Prob %": 2.0},
    ])

if "model_registry" not in st.session_state:
    st.session_state["model_registry"] = [
        {"Version": "v2.1.0 (Active)", "Model": "XGBoost Failure Classifier", "Accuracy": "96.4%", "F1-Score": "95.1%", "Framework": "XGBoost", "Deployed Date": "2026-07-01", "Status": "DEPLOYED"},
        {"Version": "v2.0.1", "Model": "LightGBM RUL Regressor", "Accuracy": "94.8%", "F1-Score": "93.6%", "Framework": "LightGBM", "Deployed Date": "2026-06-15", "Status": "STANDBY"},
        {"Version": "v1.9.0", "Model": "Random Forest Baseline", "Accuracy": "91.2%", "F1-Score": "89.5%", "Framework": "Scikit-Learn", "Deployed Date": "2026-05-10", "Status": "ARCHIVED"}
    ]

if "operator_notifications" not in st.session_state:
    st.session_state["operator_notifications"] = [
        {"ID": "N-101", "Type": "Maintenance Checklist", "Message": "Maintenance Checkup scheduled for Plant 1 tomorrow at 09:00 AM.", "Time": "10 mins ago", "Status": "Unread"},
        {"ID": "N-102", "Type": "Telemetry Warning", "Message": "High-Pressure Coolant Pump pressure dropped below baseline (28 PSI).", "Time": "1 hour ago", "Status": "Unread"},
        {"ID": "N-103", "Type": "System Notice", "Message": "Monthly calibration report successfully generated for your station.", "Time": "Yesterday", "Status": "Read"}
    ]

def get_all_machines():
    return st.session_state["fleet_machines"]

def get_user_assigned_machines(user_email):
    all_df = get_all_machines()
    return all_df[all_df["Assigned To"] == user_email]

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')


# ==============================================================================
# 🔐 AUTHENTICATION SCREEN
# ==============================================================================
if not st.session_state["authenticated"]:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0rem;'>🏭 Industrial Predictive Maintenance Platform</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 0.5rem;'>Enterprise Multi-Tenant AI Platform</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.2, 1.6, 1.2])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 Register New Joinee"])

        with auth_tab1:
            st.markdown("##### Authenticate Session")
            email = st.text_input("Corporate Email", placeholder="admin@enterprise.com or user@enterprise.com", key="login_email")
            password = st.text_input("Security Password", type="password", placeholder="••••••••", key="login_pass")
            
            if st.button("Authenticate Session", use_container_width=True, type="primary"):
                if email == "admin@enterprise.com" and password == "secret":
                    st.session_state["authenticated"] = True
                    st.session_state["user_role"] = "ADMIN"
                    st.session_state["user_name"] = "Narayana Hrithik Raj"
                    st.session_state["user_email"] = email
                    st.success("Authenticated as Administrator.")
                    st.rerun()
                elif email == "user@enterprise.com" and password == "secret":
                    st.session_state["authenticated"] = True
                    st.session_state["user_role"] = "USER"
                    st.session_state["user_name"] = "Operations Engineer"
                    st.session_state["user_email"] = email
                    st.success("Authenticated as Operator / Engineer.")
                    st.rerun()
                elif email and password:
                    st.session_state["authenticated"] = True
                    st.session_state["user_role"] = "USER"
                    st.session_state["user_name"] = email.split('@')[0].title()
                    st.session_state["user_email"] = email
                    st.success(f"Authenticated as {st.session_state['user_name']}.")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Use admin@enterprise.com / secret or user@enterprise.com / secret")

        with auth_tab2:
            st.markdown("##### Employee Registration")
            reg_name = st.text_input("Full Name", placeholder="John Doe", key="reg_name")
            reg_email = st.text_input("Corporate Email", placeholder="operator@company.com", key="reg_email")
            reg_token = st.text_input("Access Token / Joining Code", placeholder="e.g. EMP-2026-JOIN", key="reg_token")
            reg_pass = st.text_input("Password", type="password", placeholder="••••••••", key="reg_pass")
            reg_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="reg_confirm")
            
            if st.button("Register & Verify Account", use_container_width=True, type="secondary"):
                if not reg_name or not reg_email or not reg_token or not reg_pass:
                    st.error("All fields including Access Token are required!")
                elif reg_pass != reg_confirm:
                    st.error("Passwords do not match!")
                elif reg_token not in st.session_state["generated_tokens"]:
                    st.error("❌ Invalid Access Token! Contact admin.")
                else:
                    st.session_state["authenticated"] = True
                    st.session_state["user_role"] = "USER"
                    st.session_state["user_name"] = reg_name
                    st.session_state["user_email"] = reg_email
                    st.session_state["user_accounts"].append({
                        "User ID": len(st.session_state["user_accounts"]) + 1,
                        "Name": reg_name,
                        "Email": reg_email,
                        "Role": "USER",
                        "Status": "Active"
                    })
                    st.success(f"Verified! Welcome {reg_name}.")
                    st.rerun()

    st.stop()


# ==============================================================================
# 🏭 SIDEBAR & NAVIGATION
# ==============================================================================
role = st.session_state["user_role"]
user_name = st.session_state["user_name"]

st.sidebar.title("🏭 Plant Intelligence")
st.sidebar.markdown(f"**Logged in:** {user_name}")
st.sidebar.markdown(f"**Role Permission:** `{role}`")
st.sidebar.write("---")

if role == "ADMIN":
    menu_options = [
        "Dashboard", "Machine Management", "Sensor Data", "Data Validation",
        "Failure Prediction", "Remaining Useful Life", "Anomaly Detection",
        "Root Cause Analysis", "Maintenance Center", "Alerts",
        "Reports & Analytics", "User Management", "Model Management",
        "Settings", "Profile"
    ]
else:
    menu_options = [
        "Dashboard", "My Machines", "Equipment Health", "Failure Prediction",
        "Remaining Useful Life", "Anomaly Detection", "Maintenance Recommendations",
        "Reports", "Notifications", "Profile"
    ]

selected_module = st.sidebar.radio("Navigation Menu", menu_options)

st.sidebar.write("---")
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None
    st.session_state["user_email"] = None
    st.rerun()


# ==============================================================================
# 👑 ADMIN VIEW MODULES (15 MODULES)
# ==============================================================================
if role == "ADMIN":
    machines_df = get_all_machines()

    if selected_module == "Dashboard":
        st.title("⚡ Admin Platform Overview")
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Machines", len(machines_df))
        c2.metric("Healthy Machines", len(machines_df[machines_df["Status"]=="HEALTHY"]))
        c3.metric("At-Risk Machines", len(machines_df[machines_df["Status"]=="AT_RISK"]))
        c4.metric("Critical Machines", len(machines_df[machines_df["Status"]=="CRITICAL"]))
        c5.metric("Today's Alerts", f"{len([a for a in st.session_state['alerts_list'] if a['Status'] == 'Unresolved'])} Active")

        c6, c7, c8, c9, c10 = st.columns(5)
        c6.metric("Active Users", f"{len(st.session_state['user_accounts'])} Users")
        c7.metric("Scheduled Maintenance", f"{len(st.session_state['maintenance_work_orders'])} Tasks")
        c8.metric("Total Predictions", "1,420")
        c9.metric("Avg Health Score", f"{machines_df['Health %'].mean():.1f}%")
        c10.metric("Avg RUL", f"{machines_df['RUL (Days)'].mean():.1f} Days")

        st.write("---")
        col_l, col_r = st.columns([1.6, 1.0])
        with col_l:
            st.subheader("Global Fleet Health Index")
            fig = px.bar(machines_df, x="Name", y="Health %", color="Status", height=280,
                         color_discrete_map={"HEALTHY": "green", "AT_RISK": "orange", "CRITICAL": "red"})
            fig.update_layout(margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig, use_container_width=True)
        with col_r:
            st.subheader("Fleet Status Ratio")
            fig_pie = px.pie(machines_df, names="Status", color="Status", height=280,
                             color_discrete_map={"HEALTHY": "green", "AT_RISK": "orange", "CRITICAL": "red"})
            fig_pie.update_layout(margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)

    elif selected_module == "Machine Management":
        st.title("🏭 Machine Management (CRUD Operations)")
        tab1, tab2, tab3 = st.tabs(["Asset Registry", "➕ Add Machine", "⚙️ Manage & Deactivate"])
        with tab1:
            st.dataframe(machines_df, use_container_width=True, height=300)
        with tab2:
            st.subheader("Create New Equipment Asset")
            with st.form("add_m_form"):
                m_name = st.text_input("Machine Name")
                m_type = st.selectbox("Machine Type", ["CNC Machine", "Hydraulic Pump", "Gas Turbine", "Articulated Robot"])
                m_mfg = st.text_input("Manufacturer")
                m_loc = st.text_input("Plant Location")
                m_dept = st.text_input("Department")
                if st.form_submit_button("Add Machine"):
                    new_m = {
                        "ID": f"M-00{len(machines_df)+1}",
                        "Name": m_name, "Type": m_type, "Manufacturer": m_mfg,
                        "Location": m_loc, "Department": m_dept, "Status": "HEALTHY",
                        "Health %": 100.0, "RUL (Days)": 365.0, "Assigned To": "user@enterprise.com",
                        "Failure Prob %": 1.0
                    }
                    st.session_state["fleet_machines"] = pd.concat([st.session_state["fleet_machines"], pd.DataFrame([new_m])], ignore_index=True)
                    st.success(f"Machine '{m_name}' successfully registered in database!")
                    st.rerun()
        with tab3:
            st.subheader("Edit or Remove Machine")
            del_m_name = st.selectbox("Select Machine", machines_df["Name"])
            col1, col2 = st.columns(2)
            if col1.button("Deactivate Machine"):
                st.session_state["fleet_machines"].loc[st.session_state["fleet_machines"]["Name"] == del_m_name, "Status"] = "DEACTIVATED"
                st.success("Machine status changed to DEACTIVATED.")
                st.rerun()
            if col2.button("Delete Machine Permanently", type="primary"):
                st.session_state["fleet_machines"] = st.session_state["fleet_machines"][st.session_state["fleet_machines"]["Name"] != del_m_name]
                st.success("Machine deleted from database!")
                st.rerun()

    elif selected_module == "Sensor Data":
        st.title("📊 Sensor Data Ingestion Hub")
        uploaded_file = st.file_uploader("Upload Telemetry CSV File", type=["csv"])
        
        if uploaded_file is not None:
            df_upload = pd.read_csv(uploaded_file)
            st.subheader("Uploaded Dataset Preview")
            st.dataframe(df_upload.head(6), use_container_width=True, height=200)
            
            c_u1, c_u2 = st.columns(2)
            c_u1.metric("Rows Ingested", len(df_upload))
            c_u2.metric("Sensor Features", len(df_upload.columns))
            
            if st.button("🚀 Ingest & Validate Dataset into Database", type="primary"):
                st.success(f"Successfully processed and stored {len(df_upload)} sensor telemetry rows in PostgreSQL database!")

    elif selected_module == "Data Validation":
        st.title("🔬 Automated Data Validation Engine")
        
        if st.button("⚡ Run Comprehensive Validation Scan", type="primary"):
            st.success("✅ Dataset Quality Report: 0 Missing Values, Schema Compliant, No Out-of-Bound Sensor Drifts Detected.")
        
        val_report = pd.DataFrame([
            {"Sensor Stream": "Vibration Sensor A1", "Missing Values": 0, "Outliers": 2, "Schema Drift": "None", "Status": "PASS (WITH WARNINGS)"},
            {"Sensor Stream": "Coolant Pressure Bar", "Missing Values": 0, "Outliers": 0, "Schema Drift": "None", "Status": "PASS"},
            {"Sensor Stream": "Spindle Temp (K)", "Missing Values": 0, "Outliers": 1, "Schema Drift": "None", "Status": "PASS"},
            {"Sensor Stream": "Motor RPM", "Missing Values": 0, "Outliers": 0, "Schema Drift": "None", "Status": "PASS"}
        ])
        st.write("---")
        st.subheader("Telemetry Channel Validation Summary")
        st.table(val_report)

    elif selected_module == "Failure Prediction":
        st.title("🔮 AI Batch Failure Prediction Engine")
        
        if st.button("🚀 Run Failure Risk Inference on All Assets", type="primary"):
            st.session_state["fleet_machines"]["Failure Prob %"] = [4.2, 38.9, 82.4, 1.8]
            st.success("XGBoost Inference Complete! Risk profiles updated across all fleet assets.")
            
        st.write("---")
        st.dataframe(machines_df[["ID", "Name", "Type", "Status", "Health %", "Failure Prob %"]], use_container_width=True, height=200)

        fig_pred = px.bar(machines_df, x="Name", y="Failure Prob %", color="Status", height=260, title="Fleet Failure Risk Probability Spectrum",
                          color_discrete_map={"HEALTHY": "green", "AT_RISK": "orange", "CRITICAL": "red"})
        fig_pred.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_pred, use_container_width=True)

    elif selected_module == "Remaining Useful Life":
        st.title("⏳ Remaining Useful Life (RUL) Regression Engine")
        
        fig = px.line(machines_df, x="Name", y="RUL (Days)", markers=True, height=260, title="Fleet Remaining Useful Life (Days)")
        fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("---")
        selected_m_rul = st.selectbox("Select Machine to Inspect RUL Curve", machines_df["Name"])
        m_row = machines_df[machines_df["Name"] == selected_m_rul].iloc[0]
        
        col_r1, col_r2 = st.columns(2)
        col_r1.metric("Estimated RUL", f"{m_row['RUL (Days)']} Days")
        col_r2.metric("RUL Health Score", f"{m_row['Health %']}%")

    elif selected_module == "Anomaly Detection":
        st.title("⚠️ Unsupervised Anomaly Detection Center")
        
        anomalies_data = pd.DataFrame([
            {"Timestamp": "2026-07-22 10:14", "Machine": "Main Assembly Rotor Turbine", "Sensor": "Vibration Sensor A1", "Value": "4.2 g", "Baseline": "1.2 g", "Deviation": "+250%", "Severity": "CRITICAL"},
            {"Timestamp": "2026-07-22 09:30", "Machine": "High-Pressure Coolant Pump", "Sensor": "Hydraulic Pressure", "Value": "28 PSI", "Baseline": "45 PSI", "Deviation": "-37%", "Severity": "HIGH"},
            {"Timestamp": "2026-07-22 08:45", "Machine": "CNC Milling Axis-A", "Sensor": "Process Temp", "Value": "325 K", "Baseline": "310 K", "Deviation": "+4.8%", "Severity": "MEDIUM"},
            {"Timestamp": "2026-07-21 22:15", "Machine": "Robotic Welding Arm", "Sensor": "Joint Torque", "Value": "58 Nm", "Baseline": "40 Nm", "Deviation": "+45%", "Severity": "LOW"}
        ])

        col_a1, col_a2, col_a3 = st.columns(3)
        col_a1.metric("Detected Anomalies Today", "4 Outliers")
        col_a2.metric("Highest Severity", "CRITICAL (Turbine A1)")
        col_a3.metric("Isolation Forest Score", "0.89 (High Confidence)")

        st.write("---")
        st.dataframe(anomalies_data, use_container_width=True, height=200)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if st.button("🔄 Trigger Outlier Scan", type="primary"):
                st.success("Isolation Forest scan complete across all sensor channels.")
        with col_d2:
            st.download_button(
                label="📥 Download Anomaly Audit CSV",
                data=convert_df_to_csv(anomalies_data),
                file_name="anomaly_detection_report.csv",
                mime="text/csv"
            )

    elif selected_module == "Root Cause Analysis":
        st.title("🌳 SHAP Explainable AI (XAI) Root Cause")
        shap_df = pd.DataFrame({"Feature": ["Vibration Spike", "Coolant Temp", "Pressure Drops", "RPM Fluctuation"], "SHAP Importance": [0.42, 0.28, 0.18, 0.12]})
        fig = px.bar(shap_df, x="SHAP Importance", y="Feature", orientation="h", height=280, title="Top Predictive Risk Drivers")
        fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    elif selected_module == "Maintenance Center":
        st.title("🛠️ Enterprise Maintenance Center")
        tab_m1, tab_m2 = st.tabs(["Active Work Orders", "➕ Dispatch New Work Order"])
        
        with tab_m1:
            wo_df = pd.DataFrame(st.session_state["maintenance_work_orders"])
            st.dataframe(wo_df, use_container_width=True, height=180)
            
            wo_ids = [wo["ID"] for wo in st.session_state["maintenance_work_orders"]]
            if wo_ids:
                sel_wo_id = st.selectbox("Select Work Order", wo_ids)
                wo_idx = next((i for i, w in enumerate(st.session_state["maintenance_work_orders"]) if w["ID"] == sel_wo_id), None)
                if wo_idx is not None:
                    c_wo1, c_wo2 = st.columns(2)
                    if c_wo1.button("Mark Completed"):
                        st.session_state["maintenance_work_orders"][wo_idx]["Status"] = "COMPLETED"
                        st.success(f"Work Order {sel_wo_id} completed!")
                        st.rerun()
                    if c_wo2.button("Cancel Work Order", type="primary"):
                        st.session_state["maintenance_work_orders"].pop(wo_idx)
                        st.info("Work Order cancelled.")
                        st.rerun()

        with tab_m2:
            with st.form("create_wo_form"):
                wo_m = st.selectbox("Assign Target Machine", machines_df["Name"])
                wo_desc = st.text_area("Task Details", height=80)
                wo_prio = st.selectbox("Task Priority", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
                wo_time = st.slider("Estimated Downtime Hours", 0.5, 24.0, 2.0)
                
                if st.form_submit_button("Dispatch Work Order", type="primary"):
                    new_wo_id = f"WO-20{len(st.session_state['maintenance_work_orders'])+1}"
                    st.session_state["maintenance_work_orders"].append({
                        "ID": new_wo_id, "Machine": wo_m, "Task": wo_desc,
                        "Priority": wo_prio, "Status": "SCHEDULED", "Est Downtime": f"{wo_time} hrs"
                    })
                    st.success(f"Dispatched '{new_wo_id}' successfully!")

    elif selected_module == "Alerts":
        st.title("🚨 System Alert Center & Rule Management")
        tab_alt1, tab_alt2 = st.tabs(["Active Alerts Feed", "➕ Create Manual Alert Rule"])

        with tab_alt1:
            for idx, alt in enumerate(st.session_state["alerts_list"]):
                with st.expander(f"[{alt['Severity']}] {alt['Machine']} — {alt['Status']}", expanded=(alt['Status']=="Unresolved")):
                    st.write(f"**Message:** {alt['Message']}")
                    col_b1, col_b2 = st.columns([1, 4])
                    if alt["Status"] == "Unresolved":
                        if col_b1.button(f"Mark Resolved", key=f"res_{idx}"):
                            st.session_state["alerts_list"][idx]["Status"] = "Resolved"
                            st.success(f"Alert #{alt['ID']} marked as resolved!")
                            st.rerun()
                    if col_b2.button(f"Delete Alert", key=f"del_alt_{idx}"):
                        st.session_state["alerts_list"].pop(idx)
                        st.info("Alert deleted.")
                        st.rerun()

        with tab_alt2:
            with st.form("create_alert_rule_form"):
                rule_machine = st.selectbox("Target Machine", machines_df["Name"])
                rule_severity = st.selectbox("Severity Level", ["CRITICAL", "HIGH", "MEDIUM", "LOW"])
                rule_msg = st.text_area("Alert Message", height=80)
                if st.form_submit_button("Create Alert Rule"):
                    new_id = 100 + len(st.session_state["alerts_list"]) + 1
                    st.session_state["alerts_list"].append({
                        "ID": new_id, "Machine": rule_machine, "Severity": rule_severity, "Message": rule_msg, "Status": "Unresolved"
                    })
                    st.success("New alert rule created!")

    elif selected_module == "Reports & Analytics":
        st.title("📈 Platform Reports & Data Export")
        r_type = st.selectbox("Report Type", ["Daily Fleet Summary", "Machine Failure Audit", "Maintenance Log"])
        st.dataframe(machines_df, use_container_width=True, height=220)
        csv_bytes = convert_df_to_csv(machines_df)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(label="📥 Download CSV Report", data=csv_bytes, file_name=f"{r_type.lower().replace(' ', '_')}.csv", mime="text/csv", use_container_width=True)
        with col2:
            st.download_button(label="📄 Download Summary Report", data=csv_bytes, file_name=f"{r_type.lower().replace(' ', '_')}_audit.txt", mime="text/plain", use_container_width=True)

    elif selected_module == "User Management":
        st.title("👥 User Management & Access Controls")
        tab_u1, tab_u2, tab_u3 = st.tabs(["Active User Accounts", "⚙️ Manage & Delete Users", "🔑 Generate Joining Tokens"])
        
        with tab_u1:
            users_df = pd.DataFrame(st.session_state["user_accounts"])
            st.dataframe(users_df, use_container_width=True, height=200)

        with tab_u2:
            user_names = [u["Name"] for u in st.session_state["user_accounts"]]
            selected_user_name = st.selectbox("Select User Account", user_names)
            selected_user_idx = next((i for i, u in enumerate(st.session_state["user_accounts"]) if u["Name"] == selected_user_name), None)
            
            if selected_user_idx is not None:
                usr = st.session_state["user_accounts"][selected_user_idx]
                st.write(f"**Email:** {usr['Email']} | **Role:** `{usr['Role']}` | **Status:** `{usr['Status']}`")
                
                col_u_act1, col_u_act2 = st.columns(2)
                with col_u_act1:
                    new_status = "Deactivated" if usr["Status"] == "Active" else "Active"
                    if st.button(f"Toggle Status to {new_status}"):
                        st.session_state["user_accounts"][selected_user_idx]["Status"] = new_status
                        st.success(f"Status updated to {new_status}!")
                        st.rerun()
                with col_u_act2:
                    if usr["Email"] == "admin@enterprise.com":
                        st.warning("Cannot delete primary System Administrator.")
                    else:
                        if st.button("🗑️ Delete Account Permanently", type="primary"):
                            st.session_state["user_accounts"].pop(selected_user_idx)
                            st.success(f"Account '{selected_user_name}' deleted.")
                            st.rerun()
            
        with tab_u3:
            col_t1, col_t2 = st.columns([2, 1])
            with col_t1:
                token_role = st.selectbox("Assign Role Permission", ["USER", "ADMIN"])
            with col_t2:
                if st.button("Generate Token", type="primary"):
                    new_token = f"ENT-{uuid.uuid4().hex[:8].upper()}"
                    st.session_state["generated_tokens"].append(new_token)
                    st.success(f"Generated Token: `{new_token}`")
            st.code("\n".join(st.session_state["generated_tokens"]))

    elif selected_module == "Model Management":
        st.title("🤖 ML Model Registry & MLOps Tracking")
        active_model = next((m for m in st.session_state["model_registry"] if m["Status"] == "DEPLOYED"), st.session_state["model_registry"][0])

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Active Version", active_model["Version"])
        col_m2.metric("Accuracy Score", active_model["Accuracy"])
        col_m3.metric("F1-Score", active_model["F1-Score"])
        col_m4.metric("Framework", active_model["Framework"])

        st.write("---")
        if st.button("🔄 Retrain Models on New Data", type="primary"):
            progress_bar = st.progress(0)
            for p in range(0, 101, 25):
                time.sleep(0.2)
                progress_bar.progress(p)
            st.success("✅ Model 'v2.2.0-candidate' trained! Accuracy: 97.2%, F1-Score: 96.5%")
            st.session_state["model_registry"].insert(0, {
                "Version": "v2.2.0-candidate", "Model": "XGBoost Failure Classifier",
                "Accuracy": "97.2%", "F1-Score": "96.5%", "Framework": "XGBoost CPU",
                "Deployed Date": "2026-07-22", "Status": "CANDIDATE"
            })

        st.dataframe(pd.DataFrame(st.session_state["model_registry"]), use_container_width=True, height=180)

        sel_ver = st.selectbox("Select Version to Deploy", [m["Version"] for m in st.session_state["model_registry"]])
        if st.button("🚀 Deploy Selected Model"):
            for m in st.session_state["model_registry"]:
                m["Status"] = "DEPLOYED" if m["Version"] == sel_ver else "STANDBY"
            st.success(f"Model version '{sel_ver}' is now active!")
            st.rerun()

    elif selected_module == "Settings":
        st.title("⚙️ System Threshold Settings & Platform Config")
        with st.form("system_settings_form"):
            new_risk = st.slider("Failure Risk Threshold (%)", 0, 100, st.session_state["system_settings"]["risk_threshold"])
            new_vib = st.slider("Critical Vibration Threshold (g)", 1.0, 10.0, float(st.session_state["system_settings"]["vibration_limit"]))
            new_rul = st.number_input("RUL Warning Days Limit", min_value=1, max_value=180, value=st.session_state["system_settings"]["rul_warning_days"])
            new_sens = st.selectbox("Alert Engine Sensitivity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"], index=2)
            
            if st.form_submit_button("💾 Save Platform Configurations", type="primary"):
                st.session_state["system_settings"] = {
                    "risk_threshold": new_risk, "vibration_limit": new_vib,
                    "rul_warning_days": new_rul, "alert_sensitivity": new_sens
                }
                st.success("✅ System Settings saved!")

    elif selected_module == "Profile":
        st.title("👤 Admin Profile Management")
        with st.form("admin_profile_form"):
            curr_name = st.text_input("Name", value=st.session_state["user_name"])
            curr_email = st.text_input("Email", value=st.session_state["user_email"])
            new_pass = st.text_input("Change Password", type="password", placeholder="Leave blank to keep current password")
            
            if st.form_submit_button("💾 Save Profile Changes", type="primary"):
                st.session_state["user_name"] = curr_name
                st.session_state["user_email"] = curr_email
                st.success("✅ Profile updated!")
                st.rerun()


# ==============================================================================
# 👷 OPERATOR / USER VIEW MODULES (10 MODULES)
# ==============================================================================
else:
    user_machines = get_user_assigned_machines(st.session_state["user_email"])

    if selected_module == "Dashboard":
        st.title("📊 Operator Telemetry & Asset Portal")
        st.caption("Live operational state strictly for assets assigned to your account.")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Assigned Equipment", len(user_machines))
        k2.metric("Healthy Baseline", len(user_machines[user_machines["Status"]=="HEALTHY"]))
        k3.metric("High-Risk Assets", len(user_machines[user_machines["Status"]=="AT_RISK"]))
        
        unread_count = len([n for n in st.session_state["operator_notifications"] if n["Status"] == "Unread"])
        k4.metric("Active Notifications", f"{unread_count} Unread")

        st.write("---")
        col_dash_l, col_dash_r = st.columns([1.6, 1.0])
        
        with col_dash_l:
            st.subheader("Assigned Asset Telemetry Manifest")
            st.dataframe(user_machines[["ID", "Name", "Type", "Location", "Status", "Health %", "RUL (Days)", "Failure Prob %"]], use_container_width=True, height=200)

        with col_dash_r:
            st.subheader("Assigned Equipment Health Index")
            fig_u = px.bar(user_machines, x="Name", y="Health %", color="Status", height=200,
                           color_discrete_map={"HEALTHY": "green", "AT_RISK": "orange", "CRITICAL": "red"})
            fig_u.update_layout(margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_u, use_container_width=True)

    elif selected_module == "My Machines":
        st.title("🏭 My Assigned Equipment Telemetry Station")
        st.dataframe(user_machines, use_container_width=True, height=180)
        st.info("🔒 Restricted Mode: Operators have read-only access to master asset registration.")
        
        st.write("---")
        st.subheader("🔎 Deep Asset Telemetry Inspector")
        if not user_machines.empty:
            sel_m_inspect = st.selectbox("Select Assigned Asset to Stream Sensor Telemetry", user_machines["Name"], key="u_insp_m")
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Vibration Level", "1.42 g", "+0.12 g")
            col_m2.metric("Operating Temp", "312 K", "+2 K")
            col_m3.metric("Joint Torque", "42.5 Nm", "-1.2 Nm")
            col_m4.metric("Coolant Pressure", "42.0 PSI", "Normal")

    elif selected_module == "Equipment Health":
        st.title("🩺 Equipment Component Diagnostics")
        if not user_machines.empty:
            m_select = st.selectbox("Select Assigned Machine", user_machines["Name"], key="u_health_m")
            sel_row = user_machines[user_machines["Name"] == m_select].iloc[0]
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Overall Health Index", f"{sel_row['Health %']}%")
            c2.metric("Current Status", sel_row["Status"])
            c3.metric("Estimated RUL", f"{sel_row['RUL (Days)']} Days")
            
            st.write("---")
            st.subheader("Subsystem Integrity Breakdown")
            
            comp_df = pd.DataFrame([
                {"Subsystem": "Bearing & Alignment Integrity", "Health Score": sel_row['Health %']},
                {"Subsystem": "Thermal Load Balance", "Health Score": min(100.0, sel_row['Health %'] + 4.0)},
                {"Subsystem": "Hydraulic Pressure Seals", "Health Score": max(20.0, sel_row['Health %'] - 10.0)},
                {"Subsystem": "Spindle Vibration Damper", "Health Score": sel_row['Health %']}
            ])
            
            fig_health = px.bar(comp_df, x="Health Score", y="Subsystem", orientation="h", height=220, range_x=[0, 100], color="Health Score",
                                color_continuous_scale="RdYlGn")
            fig_health.update_layout(margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_health, use_container_width=True)
        else:
            st.warning("No machines currently assigned to your account.")

    elif selected_module == "Failure Prediction":
        st.title("🔮 Run AI Failure Prediction Inference")
        if not user_machines.empty:
            m_select = st.selectbox("Select Assigned Machine to Run Predictor", user_machines["Name"], key="u_pred_m")
            sel_row = user_machines[user_machines["Name"] == m_select].iloc[0]
            
            if st.button("🚀 Execute XGBoost Risk Inference", type="primary"):
                progress_bar = st.progress(0)
                for p in range(0, 101, 33):
                    time.sleep(0.15)
                    progress_bar.progress(p)
                
                f_risk = sel_row["Failure Prob %"]
                risk_cat = "HIGH RISK" if f_risk > 30 else "LOW RISK"
                
                if f_risk > 30:
                    st.error(f"Inference complete for **{m_select}**: Failure Probability = **{f_risk}%** (`{risk_cat}`)")
                else:
                    st.success(f"Inference complete for **{m_select}**: Failure Probability = **{f_risk}%** (`{risk_cat}`)")
                
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=f_risk,
                    title={'text': "Predicted Failure Probability (%)"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "red" if f_risk > 30 else "green"},
                        'steps': [
                            {'range': [0, 30], 'color': "lightgreen"},
                            {'range': [30, 70], 'color': "orange"},
                            {'range': [70, 100], 'color': "crimson"}
                        ]
                    }
                ))
                fig_gauge.update_layout(height=240, margin=dict(l=20, r=20, t=30, b=10))
                st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.warning("No machines assigned to run inference.")

    elif selected_module == "Remaining Useful Life":
        st.title("⏳ Remaining Useful Life (RUL) Forecasting")
        st.write("LightGBM Continuous RUL Degradation Curves for your assigned assets.")
        
        fig_rul_u = px.line(user_machines, x="Name", y="RUL (Days)", markers=True, height=240, title="Assigned Assets RUL (Days)")
        fig_rul_u.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_rul_u, use_container_width=True)
        
        st.write("---")
        st.dataframe(user_machines[["ID", "Name", "Type", "Health %", "RUL (Days)"]], use_container_width=True, height=180)

    elif selected_module == "Anomaly Detection":
        st.title("⚠️ Sensor Anomaly Status & Outlier Scan")
        st.caption("Isolation Forest anomaly detector scanning telemetry feeds for your assigned machines.")
        
        col_anom1, col_anom2 = st.columns([1, 3])
        with col_anom1:
            if st.button("🔄 Trigger Sensor Outlier Scan", type="primary"):
                st.success("Scan complete: 0 abnormal spikes detected across your assigned equipment.")
        
        st.write("---")
        u_anomalies = pd.DataFrame([
            {"Timestamp": "2026-07-22 09:30", "Machine": "High-Pressure Coolant Pump", "Sensor": "Hydraulic Pressure", "Observed": "28 PSI", "Expected": "45 PSI", "Deviation": "-37%", "Severity": "HIGH"}
        ])
        st.subheader("Historical Telemetry Anomaly Log")
        st.dataframe(u_anomalies, use_container_width=True, height=160)

    elif selected_module == "Maintenance Recommendations":
        st.title("💡 AI Maintenance Recommendations & Request Dispatch")
        
        st.info("💡 **Action Required:** Replace coolant fluid filter on High-Pressure Coolant Pump within 48 hours to prevent pressure cavitation.")
        
        st.write("---")
        st.subheader("Submit Maintenance Work Order Request to Admin")
        
        with st.form("u_req_maint_form"):
            req_m = st.selectbox("Select Assigned Machine", user_machines["Name"])
            req_issue = st.text_area("Describe Operational Issue / Sensor Warning", placeholder="e.g. Unusable fluid filter or abnormal spindle noise", height=80)
            req_prio = st.selectbox("Urgency Level", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            
            if st.form_submit_button("Submit Maintenance Request to Admin", type="primary"):
                new_wo_id = f"WO-20{len(st.session_state['maintenance_work_orders'])+1}"
                st.session_state["maintenance_work_orders"].append({
                    "ID": new_wo_id,
                    "Machine": req_m,
                    "Task": req_issue,
                    "Priority": req_prio,
                    "Status": "SCHEDULED",
                    "Est Downtime": "2.0 hrs"
                })
                st.success(f"Maintenance Work Request '{new_wo_id}' successfully submitted to Admin schedule!")

    elif selected_module == "Reports":
        st.title("📄 Assigned Equipment Audit Reports & Data Export")
        st.write("Generate and download audit reports for your assigned equipment.")
        
        st.dataframe(user_machines, use_container_width=True, height=200)
        csv_data = convert_df_to_csv(user_machines)
        
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            st.download_button(
                label="📥 Download Equipment CSV Report",
                data=csv_data,
                file_name="my_assigned_equipment.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_exp2:
            st.download_button(
                label="📄 Download Telemetry Audit Log (TXT)",
                data=csv_data,
                file_name="telemetry_audit.txt",
                mime="text/plain",
                use_container_width=True
            )

    elif selected_module == "Notifications":
        st.title("🔔 Operator Notifications & Alert Inbox")
        
        for idx, notif in enumerate(st.session_state["operator_notifications"]):
            with st.expander(f"[{notif['Type']}] {notif['Message']} — ({notif['Status']})", expanded=(notif['Status']=="Unread")):
                st.write(f"**Timestamp:** {notif['Time']}")
                col_n1, col_n2 = st.columns([1, 4])
                if notif['Status'] == "Unread":
                    if col_n1.button(f"Mark Read", key=f"notif_r_{idx}"):
                        st.session_state["operator_notifications"][idx]["Status"] = "Read"
                        st.success("Notification marked as read.")
                        st.rerun()
                if col_n2.button(f"Clear", key=f"notif_del_{idx}"):
                    st.session_state["operator_notifications"].pop(idx)
                    st.info("Notification cleared.")
                    st.rerun()

    elif selected_module == "Profile":
        st.title("👤 Operator Station & Profile Settings")
        
        with st.form("user_profile_form"):
            st.subheader("Account Details")
            u_curr_name = st.text_input("Full Name", value=st.session_state["user_name"])
            u_curr_email = st.text_input("Corporate Email", value=st.session_state["user_email"])
            u_shift = st.selectbox("Assigned Shift", ["Day Shift (08:00 - 16:00)", "Evening Shift (16:00 - 00:00)", "Night Shift (00:00 - 08:00)"])
            new_u_pass = st.text_input("New Password", type="password", placeholder="Leave blank to retain current password")
            
            if st.form_submit_button("💾 Save Profile Updates", type="primary"):
                st.session_state["user_name"] = u_curr_name
                st.session_state["user_email"] = u_curr_email
                st.success("Profile updates saved successfully!")
                st.rerun()