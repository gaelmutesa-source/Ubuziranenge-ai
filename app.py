import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Ubuziranenge AI", page_icon="⚖️")

st.title("⚖️ Ubuziranenge AI")
st.write("Official RSB Metrology Service Guide")

# 1. THE DATA (This ensures the dropdown and lab names match exactly)
lab_mapping = {
    "Legal Metrology Unit": ["Market Scale", "Fuel Pump", "Water Meter", "Electricity Meter", "Taxi Meter", "Weighbridge"],
    "Mass & Balance Lab": ["Analytical Balance", "Industrial Scale", "Standard Weights"],
    "Temperature & Humidity Lab": ["Thermometer", "Oven/Fridge", "Autoclave/Incubator"],
    "Volume & Flow Lab": ["Micropipette", "Laboratory Glassware", "Prover Tank"],
    "Pressure & Force Lab": ["Pressure Gauge", "Compression Machine"],
    "Force & Torque Lab": ["cbr","torque wrench","comprension and tension machine","loadcell"],
    "Dimension Lab": ["dial gauge","Vernier Caliper", "Micrometer", "Ruler/Tape Measure"]
}

# Create the dropdown list
all_instruments = []
for list_of_items in lab_mapping.values():
    all_instruments.extend(list_of_items)
all_instruments.sort()

# 2. THE INTERFACE
selected_item = st.selectbox("Select your instrument:", all_instruments)
is_trade = st.radio("Is this used for Trade (Buying/Selling)?", ["Yes", "No"])

if st.button("Check Designation"):
    # 3. THE LOGIC
    if is_trade == "Yes":
        final_lab = "Legal Metrology Unit"
    else:
        # Find which lab the instrument belongs to
        final_lab = "General Metrology" # Fallback
        for lab_name, instruments in lab_mapping.items():
            if selected_item in instruments:
                final_lab = lab_name
                break

    # Date Calculation
    col_date = datetime.now() + timedelta(days=14)
    
    # 4. THE DISPLAY (No more dots!)
    st.success(f"### Service Details")
    st.info(f"**Designated Lab:** {final_lab}")
    st.info(f"**Collection Date:** {col_date.strftime('%d %B, %Y')}")
