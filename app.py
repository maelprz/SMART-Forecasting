import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
from pathlib import Path

# --- IMPORT OUR NEW MODEL FUNCTIONS ---
from models.forecast import train_evaluation_models, train_future_models

# --- PAGE SETUP ---
st.set_page_config(page_title="SMART FORECASTING", page_icon="📈", layout="wide")

# --- SAFE CUSTOM CSS ---
# Removed hardcoded backgrounds that break Dark Mode. 
# Updated to use modern Streamlit selectors that adapt safely.
st.markdown("""
    <style>
    /* Modern Headers */
    h1, h2, h3 { 
        color: #1E3A8A; 
        font-weight: 700; 
        letter-spacing: -0.5px; 
    }
    
    /* Theme-Aware Metric Cards */
    [data-testid="stMetric"] {
        background-color: rgba(150, 150, 150, 0.05);
        border: 1px solid rgba(150, 150, 150, 0.2);
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* Button Hover Effect */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
with st.container():
    st.title("📈 SMART FORECASTING")
    st.markdown("#### Predicting Urban Unemployment in the National Capital Region (NCR)")
    st.markdown("*A prototype comparing traditional statistical methods with Machine Learning to forecast economic trends.*")
    st.markdown("---")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent
    data_candidates = [
        base_dir / 'data' / 'dataset.csv',
        base_dir / 'dataset.csv',
        base_dir / 'dataset.xlsx - NCR.csv',
    ]

    data_path = next((path for path in data_candidates if path.exists()), None)
    if data_path is None:
        raise FileNotFoundError(
            'Could not find the dataset file. Expected one of: data/dataset.csv, dataset.csv, or dataset.xlsx - NCR.csv'
        )

    df = pd.read_csv(data_path)
    
    # Clean all columns
    df['Population'] = df['Population'].astype(str).replace([',', ' '], '', regex=True).replace('nan', np.nan)
    df['Population'] = pd.to_numeric(df['Population'], errors='coerce').ffill()
    df['Labor Force Participation'] = pd.to_numeric(df['Labor Force Participation'], errors='coerce').ffill()
    
    # Feature Engineering
    df['Prev_Unemployment'] = df['Unemployment Rate'].shift(1)
    
    # Drop rows with NaNs caused by shift
    df_ml = df.dropna(subset=['Prev_Unemployment', 'GDP', 'Inflation Rate', 'Labor Force Participation', 'Population']).copy()
    return df, df_ml

df_raw, df_ml = load_data()

# ALL FACTORS UTILIZED IN THE DATASET
features = ['Prev_Unemployment', 'Labor Force Participation', 'Inflation Rate', 'Population', 'GDP']
X = df_ml[features]
y = df_ml['Unemployment Rate']

# --- SIDEBAR: SYSTEM CONTROLS ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2267/2267776.png", width=60)
st.sidebar.header("System Settings")
st.sidebar.success(f"📚 Dataset Loaded: {len(df_ml)} Quarters")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

view_option = st.sidebar.radio(
    "Select Dashboard View:",
    ("1. Model Evaluation (80/20 Test)", "2. Future Forecasting & Simulator")
)

# ==========================================
# VIEW 1: MODEL EVALUATION
# ==========================================
if view_option == "1. Model Evaluation (80/20 Test)":
    st.header("📊 Model Evaluation: Linear Regression vs. XGBoost")
    st.write("Testing models on the latest 20% of the historical data.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    split_index = int(len(X) * 0.8)
    train_X, test_X = X.iloc[:split_index], X.iloc[split_index:]
    train_y, test_y = y.iloc[:split_index], y.iloc[split_index:]

    # Call the training function from models/forecast.py
    lr_model, ml_model = train_evaluation_models(train_X, train_y)
    
    lr_preds = lr_model.predict(test_X)
    ml_preds = ml_model.predict(test_X)

    # --- METRICS SECTION ---
    st.markdown("### 🏆 Performance Metrics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Baseline (Linear Regression)**")
        m1, m2, m3 = st.columns(3)
        m1.metric("MAE", f"{mean_absolute_error(test_y, lr_preds):.4%}")
        m2.metric("RMSE", f"{np.sqrt(mean_squared_error(test_y, lr_preds)):.4%}")
        m3.metric("R² Score", f"{r2_score(test_y, lr_preds):.4f}")

    with col2:
        st.markdown("**AI Model (XGBoost)**")
        m4, m5, m6 = st.columns(3)
        m4.metric("MAE", f"{mean_absolute_error(test_y, ml_preds):.4%}")
        m5.metric("RMSE", f"{np.sqrt(mean_squared_error(test_y, ml_preds)):.4%}")
        m6.metric("R² Score", f"{r2_score(test_y, ml_preds):.4f}")
    
    st.markdown("---")

    # --- VISUAL PLOT ---
    st.markdown("### 📉 Prediction Trajectory")
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    
    test_dates = range(len(test_y))
    
    # Updated line colors to be visible on both dark/light backgrounds
    ax.plot(test_dates, test_y.values, label='Actual Unemployment', color='#888888', marker='o', linewidth=2)
    ax.plot(test_dates, lr_preds, label='Baseline Forecast', color='#FF9999', linestyle=':', linewidth=2)
    ax.plot(test_dates, ml_preds, label='Smart Forecast (XGBoost)', color='#3b82f6', linestyle='--', marker='s', linewidth=2)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#888888')
    ax.spines['bottom'].set_color('#888888')
    ax.tick_params(colors='#888888')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Legend text color needs to adapt
    legend = ax.legend(frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
    for text in legend.get_texts():
        text.set_color('#888888')
        
    st.pyplot(fig)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- FEATURE IMPORTANCE CHART ---
    st.markdown("### 🧠 The 'Brain Scan' (Feature Importance)")
    st.write("This shows which economic factors influenced the XGBoost AI the most.")
    
    importances = ml_model.feature_importances_
    fig_imp, ax_imp = plt.subplots(figsize=(8, 3))
    fig_imp.patch.set_facecolor('none')
    ax_imp.set_facecolor('none')
    
    indices = np.argsort(importances)
    sorted_features = [features[i] for i in indices]
    sorted_importances = importances[indices]
    
    bars = ax_imp.barh(sorted_features, sorted_importances, color='#3b82f6', height=0.6)
    
    for bar in bars:
        ax_imp.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                    f'{bar.get_width():.1%}', va='center', color='#888888', fontweight='bold')

    ax_imp.spines['top'].set_visible(False)
    ax_imp.spines['right'].set_visible(False)
    ax_imp.spines['bottom'].set_visible(False)
    ax_imp.spines['left'].set_color('#888888')
    ax_imp.tick_params(colors='#888888')
    ax_imp.set_xticks([]) 
    st.pyplot(fig_imp)

# ==========================================
# VIEW 2: FUTURE FORECASTING & WHAT-IF SIMULATOR
# ==========================================
elif view_option == "2. Future Forecasting & Simulator":
    st.header("🔮 Future Forecasting & Scenario Simulator")
    st.write("Compare the **Official Forecast** (business-as-usual) against your **Simulated Forecast** (slider adjustments).")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Call the full training function from models/forecast.py
    lr_model_full, ml_model_full = train_future_models(X, y)

    # Base values for the "Official Forecast"
    last_gdp = float(X['GDP'].iloc[-1])
    last_inf = float(X['Inflation Rate'].iloc[-1])
    last_lfpr = float(X['Labor Force Participation'].iloc[-1])

    # WHAT-IF SIMULATOR SLIDERS
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ What-If Simulator")
    st.sidebar.write("Adjust to simulate an economic shock or boom.")
    
    sim_gdp = st.sidebar.slider("Simulated GDP", min_value=-0.10, max_value=0.15, value=last_gdp, step=0.01, format="%.2f")
    sim_inf = st.sidebar.slider("Simulated Inflation", min_value=-0.02, max_value=0.10, value=last_inf, step=0.01, format="%.2f")
    sim_lfpr = st.sidebar.slider("Simulated LFPR", min_value=0.50, max_value=0.70, value=last_lfpr, step=0.01, format="%.2f")

    # Tracking Variables
    last_pop_off = X['Population'].iloc[-1]
    last_pop_sim = X['Population'].iloc[-1]
    
    last_unemp_off_lr = y.iloc[-1]
    last_unemp_off_xgb = y.iloc[-1]
    last_unemp_sim_xgb = y.iloc[-1]

    off_lr_preds = []
    off_xgb_preds = []
    sim_xgb_preds = []
    future_labels = []

    for i in range(4):
        future_labels.append(f"Q{i + 1}")
        
        # 1. Compound population for both tracks
        last_pop_off += 50000 
        last_pop_sim += 50000 
        
        # 2. Official natural drift (business as usual)
        current_off_gdp = last_gdp + (0.002 * i) 
        current_off_inf = last_inf + (0.001 * i) 
        
        # 3. Simulated drift (slider based)
        current_sim_gdp = sim_gdp + (0.002 * i)
        current_sim_inf = sim_inf + (0.001 * i)
        
        # Create strict float DataFrames
        next_data_off = pd.DataFrame([[
            float(last_unemp_off_xgb), float(last_lfpr), float(current_off_inf), float(last_pop_off), float(current_off_gdp)
        ]], columns=features)
        
        next_data_off_lr = pd.DataFrame([[
            float(last_unemp_off_lr), float(last_lfpr), float(current_off_inf), float(last_pop_off), float(current_off_gdp)
        ]], columns=features)
        
        next_data_sim = pd.DataFrame([[
            float(last_unemp_sim_xgb), float(sim_lfpr), float(current_sim_inf), float(last_pop_sim), float(current_sim_gdp)
        ]], columns=features)
        
        # Predict
        pred_off_lr = lr_model_full.predict(next_data_off_lr)[0]
        pred_off_xgb = ml_model_full.predict(next_data_off)[0]
        pred_sim_xgb = ml_model_full.predict(next_data_sim)[0]
        
        # Store
        off_lr_preds.append(pred_off_lr)
        off_xgb_preds.append(pred_off_xgb)
        sim_xgb_preds.append(pred_sim_xgb)
        
        # Feed prediction back into loop
        last_unemp_off_lr = pred_off_lr
        last_unemp_off_xgb = pred_off_xgb
        last_unemp_sim_xgb = pred_sim_xgb

    # THRESHOLD ALERT SYSTEM (Runs on Simulation)
    if any(p > 0.06 for p in sim_xgb_preds):
        st.error("🚨 **SIMULATOR ALERT:** Under these conditions, the AI predicts unemployment will exceed the 6.0% threshold. Intervention required!")
    else:
        st.success("✅ **SYSTEM NOMINAL:** Simulated unemployment remains stable below the 6.0% critical threshold.")

    # Future Plot 
    st.markdown("### 🔭 Trajectory Comparison")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    fig2.patch.set_facecolor('none')
    ax2.set_facecolor('none')
    
    past_dates = range(8) 
    future_dates = range(7, 12)
    
    ax2.plot(past_dates, y.iloc[-8:].values, label='Historical Data', color='#888888', marker='o', linewidth=2)
    
    # Setup plot data lists (connecting today to future)
    off_lr_plot = [y.iloc[-1]] + off_lr_preds
    off_xgb_plot = [y.iloc[-1]] + off_xgb_preds
    sim_xgb_plot = [y.iloc[-1]] + sim_xgb_preds
    
    # Plot lines
    ax2.plot(future_dates, off_lr_plot, label='Official Baseline (LR)', color='#FF9999', linestyle=':', marker='^', linewidth=2)
    ax2.plot(future_dates, off_xgb_plot, label='Official Forecast (XGBoost)', color='#3b82f6', linestyle='-', marker='o', linewidth=2)
    ax2.plot(future_dates, sim_xgb_plot, label='Simulated Forecast (XGBoost)', color='#ef4444', linestyle='--', marker='s', linewidth=2)
    
    ax2.axvline(x=7, color='#888888', linestyle='-', alpha=0.5, label='Today')
    
    # Styling
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#888888')
    ax2.spines['bottom'].set_color('#888888')
    ax2.tick_params(colors='#888888')
    ax2.grid(axis='y', linestyle='--', alpha=0.3)
    
    legend2 = ax2.legend(frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
    for text in legend2.get_texts():
        text.set_color('#888888')
        
    st.pyplot(fig2)

    st.markdown("<br>", unsafe_allow_html=True)

    # Projection Table
    st.markdown("### 📑 Detailed Projection Data")
    proj_df = pd.DataFrame({
        "Quarter": future_labels,
        "Official Baseline (LR)": [f"{p:.2%}" for p in off_lr_preds],
        "Official XGBoost": [f"{p:.2%}" for p in off_xgb_preds],
        "Simulated XGBoost": [f"{p:.2%}" for p in sim_xgb_preds]
    })
    st.table(proj_df)

    # DOWNLOAD BUTTON
    csv = proj_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Forecast Report (CSV)",
        data=csv,
        file_name='smart_forecast_report.csv',
        mime='text/csv',
    )