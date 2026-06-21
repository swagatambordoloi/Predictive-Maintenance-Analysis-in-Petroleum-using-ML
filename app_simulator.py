import streamlit as st
import numpy as np
import pandas as pd  
import joblib        
import os

# =====================================================================
# 1. PAGE CONFIGURATION & DARK THEME CUSTOM CSS
# =====================================================================
st.set_page_config(
    page_title="SCADA ML Parameter Simulator",
    page_icon="🛢️",
    layout="wide"
)

# Dark Terminal CSS Override Block
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        
        /* Force crisp white text inside the metric boxes to stand out in the dark */
        div[data-testid="stMetricValue"] > div {
            color: #F8FAFC !important; 
            font-size: 28px !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetricLabel"] > div > p {
            color: #94A3B8 !important; 
            font-size: 13px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }
        
        /* Style the Metric Cards with a dark industrial background */
        div[data-testid="stMetric"] {
            background-color: #1E293B !important; 
            border: 1px solid #334155 !important; 
            padding: 20px !important;
            border-radius: 8px !important;
            transition: all 0.25s ease-in-out !important;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 20px -5px rgb(0 0 0 / 0.5) !important;
            background-color: #243346 !important; 
            border-color: #475569 !important;
        }
        
        h3, h4 { color: #F8FAFC !important; }
        
        /* Adjust alignment for number input boxes in sidebar */
        div[data-testid="stNumberInput"] { margin-top: 4px !important; }
    </style>
""", unsafe_allow_html=True)

# Dark industrial header banner with your custom orange accent track bar
st.markdown("""
    <div style="background-color:#111C24; padding:18px; border-radius:8px; margin-bottom:25px; border-left: 8px solid #FF7F0E; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.3);">
        <h2 style="color:white; text-align:center; margin:0; font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; letter-spacing: 1px; font-size:24px;">
            🛢️ CONTROL LAYER ENGINE // SCADA PARAMETER SIMULATOR
        </h2>
        <p style="color:#A1A1AA; text-align:center; margin:6px 0 0 0; font-family:'Segoe UI', sans-serif; font-size:13px; letter-spacing: 0.5px;">
            REAL-TIME ISOLATION FOREST ANOMALY DETECTION DEPLOYMENT
        </p>
    </div>
""", unsafe_allow_html=True)

# =====================================================================
# 2. OPTIMIZED ML MODEL LOADING (OS-SAFE PATHS)
# =====================================================================
@st.cache_resource
def load_predictive_engine():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    absolute_model_path = os.path.join(current_directory, "isolation_forest_model.pkl")
    return joblib.load(absolute_model_path)

try:
    anomaly_detector = load_predictive_engine()
    model_status_flag = True
except Exception as e:
    model_status_flag = False
    st.sidebar.error("⚠️ ML Engine Offline: Running in Mock Engine Mode.")

# =====================================================================
# 3. SIDEBAR LOCKING SYNC LOGIC (SESSION STATE CALLBACKS)
# =====================================================================
def update_slider(param_prefix):
    st.session_state[f"{param_prefix}_slider"] = st.session_state[f"{param_prefix}_text"]

def update_text(param_prefix):
    st.session_state[f"{param_prefix}_text"] = st.session_state[f"{param_prefix}_slider"]

# Initialize all unique state tracking targets on application boot
initial_defaults = {
    'p_tpt': 14_000_000, 'p_pdg': 21_000_000, 't_tpt': 80, 't_pdg': 95,
    'p_mon_ckp': 4_000_000, 'volatility': 15_000, 't_trend': 0.0, 'p_trend': 0.0
}

for param, default_val in initial_defaults.items():
    if f"{param}_slider" not in st.session_state:
        st.session_state[f"{param}_slider"] = default_val
    if f"{param}_text" not in st.session_state:
        st.session_state[f"{param}_text"] = default_val

# =====================================================================
# 4. SIDEBAR CONTROL PANEL IMPLEMENTATION
# =====================================================================
st.sidebar.markdown("### 🎛️ SCADA TELEMETRY INPUTS")
st.sidebar.markdown("Modify sensor node streams to evaluate multivariate model boundaries.")
st.sidebar.markdown("---")

# 1. Wellhead Pressure (P-TPT)
st.sidebar.markdown("**Wellhead Pressure (P-TPT) [Pa]**")
c1, c2 = st.sidebar.columns([2, 1])
sim_p_tpt = c1.slider("P-TPT Slide UI", 1_000_000, 35_000_000, key="p_tpt_slider", on_change=update_text, args=('p_tpt',), label_visibility="collapsed", step=500_000)
c2.number_input("P-TPT Text UI", 1_000_000, 35_000_000, key="p_tpt_text", on_change=update_slider, args=('p_tpt',), label_visibility="collapsed", step=500_000)

# 2. Downhole Pressure (P-PDG)
st.sidebar.markdown("**Downhole Pressure (P-PDG) [Pa]**")
c3, c4 = st.sidebar.columns([2, 1])
sim_p_pdg = c3.slider("P-PDG Slide UI", 1_000_000, 45_000_000, key="p_pdg_slider", on_change=update_text, args=('p_pdg',), label_visibility="collapsed", step=500_000)
c4.number_input("P-PDG Text UI", 1_000_000, 45_000_000, key="p_pdg_text", on_change=update_slider, args=('p_pdg',), label_visibility="collapsed", step=500_000)

# 3. Wellhead Temperature (T-TPT)
st.sidebar.markdown("**Wellhead Temperature (T-TPT) [°C]**")
c5, c6 = st.sidebar.columns([2, 1])
sim_t_tpt = c5.slider("T-TPT Slide UI", 0, 120, key="t_tpt_slider", on_change=update_text, args=('t_tpt',), label_visibility="collapsed")
c6.number_input("T-TPT Text UI", 0, 120, key="t_tpt_text", on_change=update_slider, args=('t_tpt',), label_visibility="collapsed")

# 4. Downhole Temperature (T-PDG)
st.sidebar.markdown("**Downhole Temperature (T-PDG) [°C]**")
c7, c8 = st.sidebar.columns([2, 1])
sim_t_pdg = c7.slider("T-PDG Slide UI", 0, 150, key="t_pdg_slider", on_change=update_text, args=('t_pdg',), label_visibility="collapsed")
c8.number_input("T-PDG Text UI", 0, 150, key="t_pdg_text", on_change=update_slider, args=('t_pdg',), label_visibility="collapsed")

# 5. Choke Valve Pressure (P-MON-CKP)
st.sidebar.markdown("**Choke Valve Pressure (P-MON-CKP) [Pa]**")
c9, c10 = st.sidebar.columns([2, 1])
sim_p_mon_ckp = c9.slider("P-MON-CKP Slide UI", 500_000, 20_000_000, key="p_mon_ckp_slider", on_change=update_text, args=('p_mon_ckp',), label_visibility="collapsed", step=250_000)
c10.number_input("P-MON-CKP Text UI", 500_000, 20_000_000, key="p_mon_ckp_text", on_change=update_slider, args=('p_mon_ckp',), label_visibility="collapsed", step=250_000)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 STABILITY & TRENDS")

# 6. Pressure Volatility
st.sidebar.markdown("**Pressure Volatility (Std Dev) [Pa]**")
c11, c12 = st.sidebar.columns([2, 1])
sim_volatility = c11.slider("Volatility Slide UI", 0, 500_000, key="volatility_slider", on_change=update_text, args=('volatility',), label_visibility="collapsed", step=10_000)
c12.number_input("Volatility Text UI", 0, 500_000, key="volatility_text", on_change=update_slider, args=('volatility',), label_visibility="collapsed", step=10_000)

# 7. Temperature Trend
st.sidebar.markdown("**Temperature Rolling Trend Indicator**")
c13, c14 = st.sidebar.columns([2, 1])
sim_t_trend = c13.slider("T-Trend Slide UI", -5.0, 5.0, key="t_trend_slider", on_change=update_text, args=('t_trend',), label_visibility="collapsed", step=0.1)
c14.number_input("T-Trend Text UI", -5.0, 5.0, key="t_trend_text", on_change=update_slider, args=('t_trend',), label_visibility="collapsed", step=0.1)

# 8. Choke Pressure Trend
st.sidebar.markdown("**Choke Pressure Rolling Trend Indicator**")
c15, c16 = st.sidebar.columns([2, 1])
sim_p_trend = c15.slider("P-Trend Slide UI", -5.0, 5.0, key="p_trend_slider", on_change=update_text, args=('p_trend',), label_visibility="collapsed", step=0.1)
c16.number_input("P-Trend Text UI", -5.0, 5.0, key="p_trend_text", on_change=update_slider, args=('p_trend',), label_visibility="collapsed", step=0.1)

# Calculate physical differential drop feature
delta_p = sim_p_pdg - sim_p_tpt

# =====================================================================
# =====================================================================
# 5. LIVE ML INFERENCE LOOP (THE EXACT 9-FEATURE DATAFRAME)
# =====================================================================
input_data = [[
    sim_p_pdg,            # P-PDG
    sim_t_pdg,            # T-PDG
    sim_p_tpt,            # P-TPT
    sim_t_tpt,            # T-TPT
    sim_p_mon_ckp,        # P-MON-CKP
    sim_volatility,       # P-TPT_Rolling_Std
    sim_volatility * 1.2, # P-PDG_Rolling_Std 
    sim_t_trend,          # T-TPT_Rolling_Trend
    sim_p_trend           # P-MON-CKP_Rolling_Trend
]]

# FIXED: Changed 'T-TEMPER' to match your notebook training column 'T-TPT'
feature_names = [
    'P-PDG', 'T-PDG', 'P-TPT', 'T-TPT', 'P-MON-CKP', 
    'P-TPT_Rolling_Std', 'P-PDG_Rolling_Std', 
    'T-TPT_Rolling_Trend', 'P-MON-CKP_Rolling_Trend'
]

# Create standard Pandas DataFrame to completely eliminate the feature name UserWarning
feature_dataframe = pd.DataFrame(input_data, columns=feature_names)
if model_status_flag:
    prediction = anomaly_detector.predict(feature_dataframe)[0]        
    anomaly_score = anomaly_detector.score_samples(feature_dataframe)[0] 
else:
    if sim_volatility > 200000 or sim_t_trend < -2.0:
        prediction = -1
        anomaly_score = -0.6521
    else:
        prediction = 1
        anomaly_score = 0.3841

# =====================================================================
# =====================================================================
# 6. DYNAMIC DIAGNOSTIC MONITORING CENTRE (REALIGNED LOGIC LAYER)
# =====================================================================
st.markdown("### 🖥️ DATA SCIENCE ENGINE TELEMETRY")

# Initialize a flag to see if a known physical condition is met
known_fault_triggered = False

# Only evaluate specific faults if the ML engine intercepts a deviation signature
if prediction == -1:
    if sim_volatility > 200000:
        known_fault_triggered = True
        st.markdown(f"""
            <div style="background-color: #2D1414; border-left: 6px solid #EF4444; padding: 18px; border-radius: 6px; margin-bottom: 25px; border-top: 1px solid #451A1A; border-right: 1px solid #451A1A; border-bottom: 1px solid #451A1A;">
                <h4 style="color: #FCA5A5; margin: 0 0 8px 0; font-family: 'Segoe UI', sans-serif; font-weight:600;">🚨 CRITICAL: SEVERE MULTIPHASE SLUGGING INSTABILITY</h4>
                <p style="color: #F8FAFC; margin: 0; font-size: 14px; line-height: 1.6;">
                    <b>Physical Phenomenon:</b> High-frequency, violent cyclic wave surges are moving through the riser.<br>
                    <b>Remediation Protocol:</b> Initiate automated choke valve tracking loops to stabilize fluid fluctuations.
                </p>
            </div>
        """, unsafe_allow_html=True)

    elif delta_p > 15000000 and sim_t_tpt < 25:
        known_fault_triggered = True
        st.markdown(f"""
            <div style="background-color: #2A1B10; border-left: 6px solid #F97316; padding: 18px; border-radius: 6px; margin-bottom: 25px; border-top: 1px solid #43250E; border-right: 1px solid #43250E; border-bottom: 1px solid #43250E;">
                <h4 style="color: #FED7AA; margin: 0 0 8px 0; font-family: 'Segoe UI', sans-serif; font-weight:600;">🟠 WARNING: THERMODYNAMIC GAS HYDRATE PLUG FORMATION</h4>
                <p style="color: #F8FAFC; margin: 0; font-size: 14px; line-height: 1.6;">
                    <b>Physical Phenomenon:</b> Subsea environment has entered the crystallization zone.<br>
                    <b>Remediation Protocol:</b> Trigger continuous subsea chemical injection arrays for thermodynamic methanol/glycol dosing.
                </p>
            </div>
        """, unsafe_allow_html=True)

    elif delta_p < 0:
        known_fault_triggered = True
        st.markdown(f"""
            <div style="background-color: #11222C; border-left: 6px solid #38BDF8; padding: 18px; border-radius: 6px; margin-bottom: 25px; border-top: 1px solid #0F2D3E; border-right: 1px solid #0F2D3E; border-bottom: 1px solid #0F2D3E;">
                <h4 style="color: #BAE6FD; margin: 0 0 8px 0; font-family: 'Segoe UI', sans-serif; font-weight:600;">🔍 SYSTEM ERROR: INVERTED HYDROSTATIC PRESSURE GRADIENT</h4>
                <p style="color: #F8FAFC; margin: 0; font-size: 14px; line-height: 1.6;">
                    <b>Physical Phenomenon:</b> Upstream reservoir pressure cannot physically drop below surface wellhead pressure.<br>
                    <b>Remediation Protocol:</b> Flag data integrity error to network operators. Initialize node diagnostics.
                </p>
            </div>
        """, unsafe_allow_html=True)

# If the ML says it's normal (prediction == 1) OR it was unclassified, show Nominal Operation!
if prediction == 1 or not known_fault_triggered:
    st.markdown(f"""
        <div style="background-color: #062419; border-left: 6px solid #22C55E; padding: 18px; border-radius: 6px; margin-bottom: 25px; border-top: 1px solid #14462F; border-right: 1px solid #14462F; border-bottom: 1px solid #14462F;">
            <h4 style="color: #86EFAC; margin: 0 0 8px 0; font-family: 'Segoe UI', sans-serif; font-weight:600;">✅ STATUS: NOMINAL FIELD OPERATION</h4>
            <p style="color: #F8FAFC; margin: 0; font-size: 14px; line-height: 1.6;">
                <b>Model Diagnostic:</b> Telemetry matrices are operating within acceptable production boundaries.<br>
                <span style="display: inline-block; margin-top: 8px;"><b>Continuous Scoring Profile:</b> 
                    <code style="background-color:#14462F; padding:2px 6px; border-radius:4px; color:#86EFAC; border: 1px solid #166534;">{anomaly_score:.4f}</code>
                </span>
            </p>
        </div>
    """, unsafe_allow_html=True)

# =====================================================================
# 7. OPERATIONAL TELEMETRIC MATRIX CARDS
# =====================================================================
st.divider()
st.markdown("#### 📊 Derived Streaming Telemetry Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Differential Pressure Drop (ΔP)", 
        value=f"{delta_p / 1_000_000:.2f} MPa",
        delta="Normal Boundary" if delta_p < 15_000_000 else "HIGH GRADIENT SHIFT",
        delta_color="normal" if delta_p < 15_000_000 else "inverse"
    )

with col2:
    st.metric(
        label="Riser Temperature Core", 
        value=f"{sim_t_tpt} °C",
        delta="Stable Thermal Zone" if sim_t_tpt >= 25 else "CRYSTALLIZATION RISK",
        delta_color="normal" if sim_t_tpt >= 25 else "inverse"
    )

with col3:
    st.metric(
        label="Real-Time Signal Variance", 
        value=f"± {sim_volatility / 1_000:.1f} kPa",
        delta="Laminar Stream Profile" if sim_volatility <= 200_000 else "CYCLIC WAVE FLUCTUATION",
        delta_color="normal" if sim_volatility <= 200_000 else "inverse"
    )