import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path to import logic
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logic.mbe import calculate_f, calculate_eo, calculate_eg, calculate_efw, estimate_ooip, calculate_error

# --- Helper Functions ---
def format_res(value, unit="STB"):
    """Professional dynamic formatting for reservoir units."""
    if value == 0:
        return f"0.00 {unit}"
    abs_val = abs(value)
    if abs_val >= 1_000_000:
        return f"{value/1e6:,.2f} MM {unit}"
    elif abs_val >= 1_000:
        return f"{value:,.0f} {unit}"
    else:
        return f"{value:,.2f} {unit}"

# --- Page Configuration ---
st.set_page_config(
    page_title="MBE Reservoir Tool",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #dee2e6 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07) !important;
    }

    /* Force dark text for metrics to ensure readability on white cards regardless of theme */
    div[data-testid="stMetricLabel"] p {
        color: #495057 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] > div {
        color: #1e3d59 !important;
        font-weight: 800 !important;
    }
    
    /* Delta (Error) styling */
    div[data-testid="stMetricDelta"] > div {
        font-weight: 600 !important;
    }

    h1 {
        color: #1e3d59;
        font-weight: 800;
    }
    h2, h3 {
        color: #17a2b8 !important;
        font-weight: 700;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Title and Header ---
st.title("🛢️ Material Balance Equation (MBE) Estimator")
st.markdown("""
This professional utility estimates **Original Oil in Place (OOIP)** using the Havlena-Odeh Material Balance method. 
It accounts for oil expansion, gas cap expansion, and formation/water compressibility.
""")

# --- Sidebar: Initial Reservoir Properties ---
with st.sidebar:
    st.header("📍 Initial Reservoir Properties")
    
    boi = st.number_input("Initial Oil FVF ($B_{oi}$)", value=1.25, step=0.01, format="%.4f", help="Bbl/STB")
    rsi = st.number_input("Initial Solution GOR ($R_{si}$)", value=800.0, step=10.0, help="scf/STB")
    bgi = st.number_input("Initial Gas FVF ($B_{gi}$)", value=0.0012, step=0.0001, format="%.5f", help="Bbl/scf")
    
    st.divider()
    
    st.subheader("⚙️ Advanced Parameters")
    cw = st.number_input("Water Compressibility ($c_w$)", value=3e-6, format="%.2e")
    swi = st.slider("Initial Water Saturation ($S_{wi}$)", 0.0, 1.0, 0.2, step=0.05)
    cf = st.number_input("Formation Compressibility ($c_f$)", value=4e-6, format="%.2e")
    m = st.number_input("Gas Cap Ratio ($m$)", value=0.0, step=0.1, help="Ratio of gas cap volume to oil zone volume")
    
    st.divider()
    
    st.subheader("🎯 Validation")
    actual_ooip = st.number_input("Actual/Expected OOIP (MMSTB)", value=33.5, step=1.0) * 1e6

# --- Tabs for Analysis Type ---
tab1, tab2 = st.tabs(["📊 Single Point Analysis", "📅 Production History (CSV)"])

with tab1:
    st.subheader("Manual Data Input")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        np_val = st.number_input("Cum. Oil Production ($N_p$)", value=5.0e6, format="%.2e", help="STB")
        gp_val = st.number_input("Cum. Gas Production ($G_p$)", value=5.0e9, format="%.2e", help="scf")
    
    with col2:
        bo = st.number_input("Current Oil FVF ($B_o$)", value=1.3, step=0.01, format="%.4f")
        rs = st.number_input("Current Solution GOR ($R_s$)", value=600.0, step=10.0)
    
    with col3:
        bg = st.number_input("Current Gas FVF ($B_g$)", value=0.001, step=0.0001, format="%.5f")
        dp = st.number_input("Pressure Drop ($\Delta P$)", value=500.0, step=50.0)
        we = st.number_input("Water Influx ($W_e$)", value=0.0, format="%.2e")

    if st.button("🚀 Calculate OOIP", type="primary"):
        # Derived parameters
        rp = gp_val / np_val if np_val > 0 else 0
        
        # Calculations
        f = calculate_f(np_val, bo, rs, bg, rp)
        eo = calculate_eo(bo, boi, rsi, rs, bg)
        eg = calculate_eg(boi, bg, bgi)
        efw = calculate_efw(boi, cw, swi, cf, dp)
        ooip = estimate_ooip(f, we, eo, eg, efw, m)
        error = calculate_error(ooip, actual_ooip)
        
        # Display Results
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Estimated OOIP", format_res(ooip, "STB"))
        m2.metric("Withdrawal (F)", format_res(f, "bbl"))
        m3.metric("Error Accuracy", f"{100-error:.2f}%" if error < 100 else "N/A", delta=f"{error:.2f}% Error", delta_color="inverse")
        
        with st.expander("Show Intermediate Calculation Values"):
            st.write(f"- **F (Underground Withdrawal):** {f:,.2f} res bbl")
            st.write(f"- **Eo (Oil Expansion):** {eo:,.4f} bbl/STB")
            st.write(f"- **Eg (Gas Expansion):** {eg:,.4f} bbl/STB")
            st.write(f"- **Efw (Formation/Water Expansion):** {efw:,.6f} bbl/STB")
            st.write(f"- **Total Expansion (Et):** {eo + m*eg + efw:,.6f} bbl/STB")

with tab2:
    st.subheader("Batch Production Analysis")
    uploaded_file = st.file_uploader("Upload Reservoir Production History (CSV)", type=["csv"])
    
    st.info("""
    **CSV Format Expected:**
    Columns: `Np`, `Gp`, `Bo`, `Rs`, `Bg`, `dP`, `We`
    """)
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of Uploaded Data:")
        st.dataframe(df.head())
        
        if st.button("📈 Run Historical Analysis"):
            # Process dataframe
            df['Rp'] = df['Gp'] / df['Np']
            df['F'] = calculate_f(df['Np'], df['Bo'], df['Rs'], df['Bg'], df['Rp'])
            df['Eo'] = calculate_eo(df['Bo'], boi, rsi, df['Rs'], df['Bg'])
            df['Eg'] = calculate_eg(boi, df['Bg'], bgi)
            df['Efw'] = calculate_efw(boi, cw, swi, cf, df['dP'])
            df['Et'] = df['Eo'] + (m * df['Eg']) + df['Efw']
            df['OOIP_Calc'] = (df['F'] - df['We']) / df['Et']
            
            st.divider()
            st.subheader("Calculated Results")
            st.dataframe(df[['Np', 'F', 'Et', 'OOIP_Calc']])
            
            # Visualization
            st.subheader("Visual Analytics")
            fig = go.Figure()
            # Havlena-Odeh Plot: F vs Et
            fig.add_trace(go.Scatter(x=df['Et'], y=df['F'] - df['We'], mode='markers+lines', name='Havlena-Odeh', marker=dict(size=10, color='#17a2b8')))
            
            # Add trendline (Slope = N)
            x = df['Et'].values.reshape(-1, 1)
            y = (df['F'] - df['We']).values
            slope = np.linalg.lstsq(x, y, rcond=None)[0][0]
            
            fig.add_trace(go.Scatter(x=df['Et'], y=slope*df['Et'], mode='lines', name=f'Trend (N = {slope/1e6:.2f} MMSTB)', line=dict(dash='dash', color='gray')))
            
            fig.update_layout(
                title="Havlena-Odeh Diagnostic Plot",
                xaxis_title="Expansion Term (Et) [bbl/STB]",
                yaxis_title="Withdrawal Term (F - We) [res bbl]",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)

            # OOIP Stability Plot
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df['Np'], y=df['OOIP_Calc']/1e6, mode='markers+lines', name='Calculated OOIP', line=dict(color='#ff7f0e')))
            fig2.add_hline(y=actual_ooip/1e6, line_dash="dot", annotation_text="Expected OOIP", line_color="green")
            fig2.update_layout(
                title="OOIP Consistency over Production",
                xaxis_title="Cumulative Production (Np) [STB]",
                yaxis_title="Estimated OOIP [MMSTB]",
                template="plotly_white"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Please upload a CSV file to run historical analysis.")
        # Provide example download
        example_df = pd.DataFrame({
            'Np': [1e6, 2e6, 3e6, 4e6, 5e6],
            'Gp': [1e9, 2e9, 3e9, 4e9, 5e9],
            'Bo': [1.26, 1.27, 1.28, 1.29, 1.30],
            'Rs': [750, 710, 670, 630, 600],
            'Bg': [0.0011, 0.00108, 0.00105, 0.00102, 0.001],
            'dP': [100, 200, 300, 400, 500],
            'We': [0, 0, 0, 0, 0]
        })
        st.write("Example CSV Structure:")
        st.dataframe(example_df)

# --- Footer ---
st.divider()

