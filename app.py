import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="Ubuziranenge Assistant", page_icon="⚖️")

# --- 1. DATA & LOGIC ---
lab_mapping = {
    "Legal Metrology Unit": ["Market Scale", "Fuel Pump", "Water Meter", "Electricity Meter", "Taxi Meter", "Weighbridge"],
    "Mass & Balance Lab": ["Analytical Balance", "Industrial Scale", "Standard Weights"],
    "Temperature & Humidity Lab": ["Thermometer", "Oven/Fridge", "Autoclave/Incubator"],
    "Volume & Flow Lab": ["Micropipette", "Laboratory Glassware", "Prover Tank"],
    "Pressure": ["Pressure Gauge"],
    "Force & Torque Lab":["cbr","Torque wrench","compression and tension machine","marshall"],
    "Dimension Lab": ["dial gauge","Vernier Caliper", "Micrometer", "Ruler/Tape Measure"]
}

all_instruments = []
for items in lab_mapping.values():
    all_instruments.extend(items)
all_instruments.sort()

# --- 2. UI HEADER ---
st.image("logo.png", width=150)
st.title("⚖️ Ubuziranenge Assistant")
st.write("### RSB Metrology Quotation & Service Guide")

# --- 3. INPUTS ---
col_in1, col_in2 = st.columns(2)

with col_in1:
    selected_item = st.selectbox("Select Instrument:", all_instruments)
    is_trade = st.radio("Purpose of use:", ["Trade (Buying/Selling)", "Industrial/Scientific"])

with col_in2:
    quantity = st.number_input("Number of Instruments:", min_value=1, value=1, step=1)

# --- 4. CALCULATION ---
if is_trade == "Trade (Buying/Selling)":
    service_type = "Verification"
    unit_price = 500
    total_cost = quantity * unit_price
    lab_assigned = "Legal Metrology Unit"
else:
    service_type = "Calibration"
    unit_price = 10000
    lab_assigned = "General Metrology" # Default
    for lab, items in lab_mapping.items():
        if selected_item in items:
            lab_assigned = lab
            break
    
    # Pricing logic: 10k each, max 100k for 10+ items
    if quantity >= 10:
        total_cost = 100000
    else:
        total_cost = quantity * unit_price

collection_date = (datetime.now() + timedelta(days=14)).strftime('%d %B, %Y')

# --- 5. RESULTS DISPLAY ---
st.divider()
st.subheader("Service Summary")

res1, res2, res3 = st.columns(3)
res1.metric("Designated Lab", lab_assigned)
res2.metric("Total Cost", f"{total_cost:,} Rwf")
res3.metric("Collection Date", collection_date)

# --- 6. PDF GENERATION ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RSB Ubuziranenge AI Service Slip", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Date generated: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 10, f"Instrument: {selected_item}", ln=True)
    pdf.cell(200, 10, f"Service Type: {service_type}", ln=True)
    pdf.cell(200, 10, f"Quantity: {quantity}", ln=True)
    pdf.cell(200, 10, f"Designated Lab: {lab_assigned}", ln=True)
    pdf.cell(200, 10, f"Total Estimated Cost: {total_cost:,} Rwf", ln=True)
    pdf.cell(200, 10, f"Collection Date: {collection_date}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 5, "Note: This is an automated estimate. Final billing will be done at the RSB reception desk.")
    return pdf.output(dest="S").encode("latin-1")

pdf_data = create_pdf()
st.download_button(label="📥 Download Service Slip (PDF)", data=pdf_data, file_name="RSB_Service_Slip.pdf", mime="application/pdf")
