import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
import os

# 1. Page Configuration & Theme Styling
st.set_page_config(page_title="Ubuziranenge AI", page_icon="⚖️", layout="centered")

# Force a clean light theme for mobile visibility
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    h1, h2, h3 { color: #1E3A8A; font-family: 'Arial'; }
    .stMetric { background-color: #F8FAFC; padding: 10px; border-radius: 10px; border: 1px solid #E2E8F0; }
    </style>
    """, unsafe_allow_html=True)

# 2. UI HEADER & LOGO
if os.path.exists("logo.png"):
    st.image("logo.png", width=180)
else:
    st.title("🇷🇼 Rwanda Standards Board")

st.markdown("<h1 style='text-align: center;'>Ubuziranenge AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Metrology Service Quotation & Application Portal</p>", unsafe_allow_html=True)
st.divider()

# 3. CUSTOMER INFORMATION SECTION
st.subheader("🏢 Customer Information")
col_c1, col_c2 = st.columns(2)
with col_c1:
    company_name = st.text_input("Company Name")
    tin_number = st.text_input("Company TIN Number")
    company_address = st.text_input("Company Address")
with col_c2:
    applicant_name = st.text_input("Name of the Applicant")
    contact_number = st.text_input("Contact Number (Phone)")

st.divider()

# 4. INSTRUMENT DETAILS
st.subheader("⚖️ Instrument & Service Details")
lab_mapping = {
    "Legal Metrology Unit": ["Market Scale", "Fuel Pump", "Water Meter", "Electricity Meter", "Taxi Meter", "Weighbridge"],
    "Mass & Balance Lab": ["Analytical Balance", "Industrial Scale", "Standard Weights"],
    "Temperature & Humidity Lab": ["Thermometer", "Oven/Fridge", "Autoclave/Incubator"],
    "Volume & Flow Lab": ["Micropipette", "Laboratory Glassware", "Prover Tank"],
    "Pressure Lab": ["Pressure Gauge"],
    "Force & Torque Lab":["Compression and tension Machine","cbr","torque wrench","marshall"],
    "Dimension Lab": ["dial gauge","Vernier Caliper", "Micrometer", "Ruler/Tape Measure"]
}
all_instruments = sorted([item for sublist in lab_mapping.values() for item in sublist])

col_in1, col_in2 = st.columns(2)
with col_in1:
    selected_item = st.selectbox("Select Instrument:", all_instruments)
    usage = st.radio("Purpose:", ["Trade/Commercial", "Industrial/Scientific"])
with col_in2:
    quantity = st.number_input("Number of Instruments:", min_value=1, value=1)

# Logic for Price
is_trade = "Trade" in usage
if is_trade:
    service_type, lab_assigned, unit_price = "Verification", "Legal Metrology Unit", 500
    total_cost = quantity * unit_price
else:
    service_type, unit_price = "Calibration", 10000
    lab_assigned = next((lab for lab, items in lab_mapping.items() if selected_item in items), "General Lab")
    total_cost = 100000 if quantity >= 10 else quantity * unit_price

collection_date = (datetime.now() + timedelta(days=14)).strftime('%d %B, %Y')

# 5. DIGITAL SIGNATURE
st.subheader("✍️ Digital Signature")
st.write("Please sign inside the box below:")
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#EEEEEE",
    height=150,
    drawing_mode="freedraw",
    key="canvas",
)

# 6. PDF GENERATION LOGIC
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RWANDA STANDARDS BOARD", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 8, "METROLOGY SERVICES QUOTATION", ln=True, align='C')
    pdf.ln(10)
    
    # Customer Details Table
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 8, "CUSTOMER DETAILS", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(100, 7, f"Company: {company_name}", ln=True)
    pdf.cell(100, 7, f"TIN: {tin_number}", ln=True)
    pdf.cell(100, 7, f"Address: {company_address}", ln=True)
    pdf.cell(100, 7, f"Contact: {applicant_name} ({contact_number})", ln=True)
    pdf.ln(5)
    
    # Service Details Table
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 8, "SERVICE INFORMATION", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(100, 7, f"Instrument: {selected_item}", ln=True)
    pdf.cell(100, 7, f"Service Type: {service_type}", ln=True)
    pdf.cell(100, 7, f"Designated Lab: {lab_assigned}", ln=True)
    pdf.cell(100, 7, f"Estimated Collection: {collection_date}", ln=True)
    pdf.ln(5)
    
    # Price
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"TOTAL COST: {total_cost:,} Rwf", ln=True)
    pdf.ln(10)
    
    # Footer Note
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, "Note: This quotation is generated automatically. Please present this slip and the instrument(s) at RSB Metrology Reception. Final verification of instrument condition will be done upon receipt.")
    return pdf.output(dest="S").encode("latin-1")

# 7. FINAL RESULTS & DOWNLOAD
if st.button("Confirm & Generate Slip"):
    if not company_name or not applicant_name:
        st.error("Please fill in the Customer Information before proceeding.")
    else:
        st.success("Quotation Generated Successfully!")
        st.metric("Total Estimate", f"{total_cost:,} Rwf")
        st.metric("Collection Date", collection_date)
        
        pdf_data = create_pdf()
        st.download_button(
            label="📥 Download Official Quotation (PDF)",
            data=pdf_data,
            file_name=f"RSB_Quotation_{company_name}.pdf",
            mime="application/pdf"
        )
