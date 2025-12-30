import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
import os

# Page Configuration
st.set_page_config(page_title="Ubuziranenge AI", page_icon="⚖️", layout="centered")

# --- UI HEADER & LOGO ---
# This looks for the logo.png you uploaded to GitHub
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
    
    # Optional: Allow user to download the logo directly
    with open("logo.png", "rb") as file:
        st.sidebar.download_button(
            label="📥 Download Official RSB Logo",
            data=file,
            file_name="RSB_Logo.png",
            mime="image/png"
        )
else:
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>Ubuziranenge AI</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center;'><b>Rwanda Standards Board Metrology Assistant</b></p>", unsafe_allow_html=True)
st.divider()

# --- 1. THE KNOWLEDGE BASE ---
lab_mapping = {
    "Legal Metrology Unit": ["Market Scale", "Fuel Pump", "Water Meter", "Electricity Meter", "Taxi Meter", "Weighbridge"],
    "Mass & Balance Lab": ["Analytical Balance", "Industrial Scale", "Standard Weights"],
    "Temperature & Humidity Lab": ["Thermometer", "Oven/Fridge", "Autoclave/Incubator"],
    "Volume & Flow Lab": ["Micropipette", "Laboratory Glassware", "Prover Tank"],
    "Pressure & Force Lab": ["Pressure Gauge", "Compression Machine"],
    "Dimension Lab": ["Vernier Caliper", "Micrometer", "Ruler/Tape Measure"]
}

all_instruments = []
for items in lab_mapping.values():
    all_instruments.extend(items)
all_instruments.sort()

# --- 2. INPUT SECTION ---
st.subheader("📝 Request Details")
col1, col2 = st.columns(2)

with col1:
    selected_item = st.selectbox("Select your instrument:", all_instruments)
    quantity = st.number_input("Number of instruments:", min_value=1, value=1, step=1)

with col2:
    usage = st.radio(
        "Purpose of use:",
        ["Trade/Commercial (Market, Billing, etc.)", "Industrial/Scientific (Lab, Medical, Factory)"]
    )

# --- 3. CALCULATION LOGIC ---
is_trade = "Trade" in usage

if is_trade:
    service_type = "Verification"
    lab_assigned = "Legal Metrology Unit"
    unit_price = 500
    total_cost = quantity * unit_price
else:
    service_type = "Calibration"
    unit_price = 10000
    lab_assigned = "General Metrology Lab"
    for lab, items in lab_mapping.items():
        if selected_item in items:
            lab_assigned = lab
            break
    
    # 100,000 Rwf Cap for Industrial
    if quantity >= 10:
        total_cost = 100000
    else:
        total_cost = quantity * unit_price

collection_date = (datetime.now() + timedelta(days=14)).strftime('%d %B, %Y')

# --- 4. RESULTS DISPLAY ---
st.info(f"### Service Summary")
res_col1, res_col2 = st.columns(2)

with res_col1:
    st.write(f"**Laboratory:** {lab_assigned}")
    st.write(f"**Service:** {service_type}")
    st.write(f"**Quantity:** {quantity}")

with res_col2:
    st.write(f"**Total Cost:** {total_cost:,} Rwf")
    st.write(f"**Collection Date:** {collection_date}")

# --- 5. PDF GENERATION ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RSB Metrology Service Slip", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Instrument: {selected_item}", ln=True)
    pdf.cell(200, 10, f"Service Type: {service_type}", ln=True)
    pdf.cell(200, 10, f"Quantity: {quantity}", ln=True)
    pdf.cell(200, 10, f"Designated Lab: {lab_assigned}", ln=True)
    pdf.cell(200, 10, f"Total Estimated Cost: {total_cost:,} Rwf", ln=True)
    pdf.cell(200, 10, f"Scheduled Collection: {collection_date}", ln=True)
    return pdf.output(dest="S").encode("latin-1")

st.divider()
pdf_data = create_pdf()
st.download_button(
    label="📥 Download Service Slip (PDF)",
    data=pdf_data,
    file_name=f"RSB_Slip_{selected_item.replace(' ', '_')}.pdf",
    mime="application/pdf"
)
