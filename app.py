import streamlit as st
import pandas as pd

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="SMART Forecast", layout="wide")

# -----------------------------
# HEADER
# -----------------------------
st.title("SMART Forecast")
st.divider()

# -----------------------------
# SAMPLE DATA (PLACEHOLDER)
# -----------------------------
data = {
    "City": ["Cebu City", "Manila", "Davao City"],
    "Population": [964169, 1846513, 1776949],
    "Unemployment_New_Model": [5.2, 6.1, 4.8],
    "Unemployment_Traditional": [6.5, 7.0, 5.9]
}

df = pd.DataFrame(data)

# -----------------------------
# LAYOUT (SPLIT SCREEN)
# -----------------------------
col1, col2 = st.columns([2, 1])

# -----------------------------
# LEFT SIDE (MAP)
# -----------------------------
with col1:
    st.subheader("Philippines Map (Click a City)")

    map_data = pd.DataFrame({
        "lat": [10.3157, 14.5995, 7.1907],
        "lon": [123.8854, 120.9842, 125.4553],
    })

    st.map(map_data)

    selected_city = st.selectbox("Select City", df["City"])

# -----------------------------
# RIGHT SIDE (INFO PANEL)
# -----------------------------
with col2:
    st.subheader("City Information")

    city_data = df[df["City"] == selected_city].iloc[0]

    st.markdown(f"""
    ### {city_data['City']}

    **Population:** {city_data['Population']}

    **Unemployment Rate (SMART Forecast - XGBoost):**  
    {city_data['Unemployment_New_Model']}%

    **Unemployment Rate (Traditional Model):**  
    {city_data['Unemployment_Traditional']}%
    """)

    st.markdown("---")
    st.info("This is a prototype. Data shown are placeholders.")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("<hr><center>SMART Forecast Prototype Dashboard</center>", unsafe_allow_html=True)