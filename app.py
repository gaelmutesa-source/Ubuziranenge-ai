import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import os
import io

# --- 1. PAGE CONFIG & FORCED LIGHT THEME ---
st.set_page_config(page_title="Ubuziranenge AI", page_icon="⚖️", layout="centered")

# CSS to ensure visibility on mobile (ignores dark mode settings)
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #1E3A8A !important; }
    .stButton>button { background-color: #1E3A8A !important; color: white !important; width: 100%; border-radius: 8px; font-weight: bold; }
    [data-testid="stMetricValue"] { color: #1E3A8A !important; }
    .stCanvas { border: 1px solid #1E3A8A !important; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER & LOGO ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
st.markdown("<h1 style='text-align: center;'>Ubuziranenge AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 20px;'>Metrology service application assistant</p>", unsafe_allow_html=True)
st.divider()

# --- 3. CUSTOMER INFORMATION ---
st.subheader("🏢 Customer Information")
col_c1, col_c2 = st.columns(2)
with col_c1:
    company_name = st.text_input("Company Name")
    tin_number = st.text_input("Company TIN Number")
    company_address = st.text_input("Company Address")
with col_c2:
    applicant_name = st.text_input("Name of the Applicant")
    contact_number = st.text_input("Contact Number")
    customer_email = st.text_input("Email Address")

# --- 4. INSTRUMENT & SERVICE DETAILS ---
st.subheader("⚖️ Service Selection")
lab_mapping = {
    "Legal Metrology Unit": ["Market Scale", "Fuel Pump", "Water Meter", "Electricity Meter", "Taxi Meter", "Weighbridge"],
    "Mass & Balance Lab": ["Analytical Balance", "Industrial Scale", "Standard Weights"],
    "Temperature & Humidity Lab": ["Thermometer", "Oven/Fridge", "Autoclave/Incubator"],
    "Volume & Flow Lab": ["Micropipette", "Laboratory Glassware", "Prover Tank"],
    "Pressure & Force Lab": ["Pressure Gauge", "Compression Machine"],
    "Dimension Lab": ["Vernier Caliper", "Micrometer", "Ruler/Tape Measure"]
}
all_instruments = sorted([item for sublist in lab_mapping.values() for item in sublist])

col_s1, col_s2 = st.columns(2)
with col_s1:
    selected_item = st.selectbox("Select Instrument:", all_instruments)
    usage = st.radio("Usage Purpose:", ["Trade/Commercial (Verification)", "Industrial/Scientific (Calibration)"])
with col_s2:
    quantity = st.number_input("Number of Units:", min_value=1, value=1)

# Pricing & Lab Logic
is_trade = "Trade" in usage
if is_trade:
    service_type, lab_assigned, unit_price = "Verification", "Legal Metrology Unit", 500
    total_cost = quantity * unit_price
else:
    service_type, unit_price = "Calibration", 10000
    lab_assigned = next((lab for lab, items in lab_mapping.items() if selected_item in items), "General Metrology Lab")
    total_cost = 100000 if quantity >= 10 else quantity * unit_price

collection_date = (datetime.now() + timedelta(days=14)).strftime('%d %B, %Y')

# --- 5. DIGITAL SIGNATURE ---
st.subheader("✍️ Applicant Signature")
canvas_result = st_canvas(
    stroke_width=2, stroke_color="#000000", background_color="#F8FAFC",
    height=150, update_streamlit=True, key="canvas",
)

# --- 6. PDF GENERATION FUNCTION (SOLVES INTERLACING ISSUE) ---
def generate_pdf(sig_data):
    pdf = FPDF()
    pdf.add_page()
    
    # LOGO HANDLING: Fixes "Interlacing not supported" by re-saving the image
    if os.path.exists("logo.png"):
        try:
            with Image.open("logo.png") as img:
                img = img.convert("RGB") # Remove transparency/interlacing
                img.save("clean_logo.png", interlaced=False)
            pdf.image("clean_logo.png", x=85, y=10, w=40)
            pdf.ln(35)
        except Exception:
            pdf.ln(10) # Fallback if image fails
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RWANDA STANDARDS BOARD", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 8, "METROLOGY SERVICE APPLICATION SLIP", ln=True, align='C')
    pdf.ln(10)

    # Info Sections
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "  CUSTOMER INFORMATION", ln=True, fill=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Company: {company_name}", ln=True)
    pdf.cell(0, 8, f"TIN: {tin_number}", ln=True)
    pdf.cell(0, 8, f"Applicant: {applicant_name} ({contact_number})", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "  SERVICE DETAILS", ln=True, fill=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Instrument: {selected_item}", ln=True)
    
    # Lab Assignment Highlight
    pdf.set_text_color(30, 58, 138)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, f"DESIGNATED LAB: {lab_assigned}", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.cell(0, 8, f"Total Cost: {total_cost:,} Rwf", ln=True)
    pdf.cell(0, 8, f"Collection Date: {collection_date}", ln=True)

    # Signature Processing
    if sig_data is not None and np.sum(sig_data) > 0:
        sig_img = Image.fromarray(sig_data.astype('uint8'), 'RGBA')
        bg = Image.new("RGB", sig_img.size, (255, 255, 255))
        bg.paste(sig_img, mask=sig_img.split()[3])
        bg.save("sig_temp.png")
        pdf.ln(5)
        pdf.cell(0, 8, "Applicant Signature:", ln=True)
        pdf.image("sig_temp.png", w=40)

    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, "Note: This is an automated slip. Present this document at RSB Metrology reception.", align='C')
    
    return pdf.output(dest="S").encode("latin-1")

# --- 7. FINAL EXECUTION ---
st.divider()
if st.button("Generate & Download Official Slip"):
    if not company_name or not applicant_name or not customer_email:
        st.error("⚠️ Please fill in all Customer Information fields.")
    elif canvas_result.image_data is None or np.sum(canvas_result.image_data) == 0:
        st.error("⚠️ Please provide your digital signature.")
    else:
        try:
            pdf_bytes = generate_pdf(canvas_result.image_data)
            st.success("✅ Application Processed Successfully!")
            st.download_button(
                label="📥 Click here to Download PDF Slip",
                data=pdf_bytes,
                file_name=f"RSB_Application_{company_name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error: {e}")
