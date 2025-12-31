import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import os
import io

# --- 1. PAGE CONFIG & THEME (FORCED LIGHT MODE) ---
st.set_page_config(page_title="Ubuziranenge AI", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #1E3A8A !important; }
    .stButton>button { background-color: #1E3A8A !important; color: white !important; width: 100%; border-radius: 8px; }
    .chat-bubble { background-color: #F0F4F8; padding: 15px; border-radius: 15px; border-left: 5px solid #1E3A8A; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER & LOGO ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
st.markdown("<h1 style='text-align: center;'>Ubuziranenge AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 20px;'>Metrology service application assistant</p>", unsafe_allow_html=True)
st.divider()

# --- 3. CUSTOMER INFORMATION (ALL FIELDS RESTORED) ---
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
    usage = st.radio("Usage Purpose:", ["Trade/Commercial", "Industrial/Scientific"])
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

# --- 5. CHATBOT ASSISTANT ---
st.divider()
st.subheader("🤖 Ubuziranenge Chatbot")
user_query = st.text_input("Ask me about RSB scope or this application:")
if user_query:
    q = user_query.lower()
    if any(word in q for word in ["cost", "price", "pay"]):
        ans = f"Your total estimated cost is **{total_cost:,} Rwf**."
    elif any(word in q for word in ["date", "ready", "pickup"]):
        ans = f"Your collection date is **{collection_date}**."
    elif "lab" in q:
        ans = f"Your {selected_item} will be handled by the **{lab_assigned}**."
    else:
        ans = "For other inquiries, please contact the **RSB Hotline at 3250**."
    st.markdown(f"<div class='chat-bubble'>{ans}</div>", unsafe_allow_html=True)

# --- 6. STABLE SIGNATURE PAD ---
st.subheader("✍️ Applicant Signature")
canvas_result = st_canvas(
    stroke_width=2, stroke_color="#000000", background_color="#F8FAFC",
    height=150, update_streamlit=True, key="canvas",
)

# --- 7. PDF GENERATION WITH LOGO & SIGNATURE ---
def create_pdf(sig_data):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=85, y=10, w=40)
        pdf.ln(35)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RWANDA STANDARDS BOARD", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 8, "METROLOGY SERVICE APPLICATION SLIP", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=10)
    pdf.cell(100, 7, f"Company: {company_name}", ln=True)
    pdf.cell(100, 7, f"TIN: {tin_number}", ln=True)
    pdf.cell(100, 7, f"Instrument: {selected_item} ({quantity} units)", ln=True)
    pdf.cell(100, 7, f"Designated Lab: {lab_assigned}", ln=True)
    pdf.cell(100, 7, f"Total Cost: {total_cost:,} Rwf", ln=True)
    pdf.cell(100, 7, f"Collection Date: {collection_date}", ln=True)

    if sig_data is not None and np.sum(sig_data) > 0:
        img = Image.fromarray(sig_data.astype('uint8'), 'RGBA')
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        bg.save("temp_sig.png")
        pdf.ln(5)
        pdf.cell(100, 8, "Applicant Signature:", ln=True)
        pdf.image("temp_sig.png", w=40)

    return pdf.output(dest="S").encode("latin-1")

# --- 8. FINAL BUTTON & ERROR HANDLING ---
st.divider()
if st.button("Confirm & Generate Slip"):
    if not company_name or not applicant_name or not customer_email:
        st.error("⚠️ Please fill in all Customer Information fields.")
    elif canvas_result.image_data is None or np.sum(canvas_result.image_data) == 0:
        st.error("⚠️ Please provide your digital signature.")
    else:
        try:
            pdf_bytes = create_pdf(canvas_result.image_data)
            st.success("✅ Application generated successfully!")
            st.download_button("📥 Download Official Slip (PDF)", data=pdf_bytes, file_name=f"RSB_Slip_{company_name}.pdf")
        except Exception as e:
            st.error(f"Error: {e}")
