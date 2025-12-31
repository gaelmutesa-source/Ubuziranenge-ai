import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ubuziranenge AI", layout="centered")

# Forced Light Theme CSS
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #1E3A8A !important; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
st.title("Ubuziranenge AI")
st.write("Metrology service application assistant")

# --- 1. CUSTOMER INFO ---
company_name = st.text_input("Company Name")
applicant_name = st.text_input("Applicant Name")
# ... (keeping other fields simple for this debug version)

# --- 2. LOGIC ---
selected_item = st.selectbox("Instrument:", ["Digital Scale", "Thermometer", "Water Meter"])
usage = st.radio("Usage:", ["Trade", "Industrial"])
quantity = st.number_input("Units:", min_value=1, value=1)

is_trade = usage == "Trade"
total_cost = (quantity * 500) if is_trade else (100000 if quantity >= 10 else quantity * 10000)
lab_assigned = "Legal Metrology" if is_trade else "Industrial Lab"
col_date = (datetime.now() + timedelta(days=14)).strftime('%d %B, %Y')

# --- 3. THE SIGNATURE PAD (FIXED) ---
st.subheader("✍️ Applicant Signature")
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=3,
    stroke_color="#000000",
    background_color="#F0F2F6",
    update_streamlit=True, # Forces data to be sent
    height=150,
    drawing_mode="freedraw",
    key="canvas",
)

# --- 4. PDF GENERATION (FIXED) ---
def create_pdf(sig_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RSB METROLOGY APPLICATION", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Company: {company_name}", ln=True)
    pdf.cell(200, 10, f"Lab: {lab_assigned}", ln=True)
    pdf.cell(200, 10, f"Cost: {total_cost} Rwf", ln=True)

    # Process Signature only if it exists
    if sig_data is not None:
        # Convert the drawing into a real image
        img = Image.fromarray(sig_data.astype('uint8'), 'RGBA')
        # Create a white background to prevent PDF errors
        final_sig = Image.new("RGB", img.size, (255, 255, 255))
        final_sig.paste(img, mask=img.split()[3]) 
        final_sig.save("sig_output.png")
        pdf.image("sig_output.png", w=50)

    return pdf.output(dest="S").encode("latin-1")

# --- 5. ACTION BUTTON ---
if st.button("Generate Final Slip"):
    # Check if user actually signed
    if canvas_result.image_data is None or np.sum(canvas_result.image_data) == 0:
        st.error("⚠️ Please provide a signature before proceeding.")
    elif not company_name:
        st.error("⚠️ Please enter a Company Name.")
    else:
        try:
            pdf_bytes = create_pdf(canvas_result.image_data)
            st.success("✅ Application successfully processed!")
            st.download_button("📥 Download PDF", data=pdf_bytes, file_name="RSB_Slip.pdf")
        except Exception as e:
            st.error(f"Error creating PDF: {e}")
