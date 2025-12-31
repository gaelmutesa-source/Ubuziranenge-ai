import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import os
import io

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Ubuziranenge AI", layout="centered")

# Force Light Mode CSS
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #1E3A8A !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
st.title("Ubuziranenge AI")
st.write("Metrology service application assistant")
st.divider()

# --- 3. INPUT FIELDS ---
col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("Company Name")
    applicant_name = st.text_input("Applicant Name")
    tin_number = st.text_input("TIN Number")
with col2:
    selected_item = st.selectbox("Instrument:", ["Digital Scale", "Thermometer", "Water Meter", "Fuel Pump", "Pressure Gauge"])
    usage = st.radio("Usage:", ["Trade/Commercial", "Industrial/Scientific"])
    quantity = st.number_input("Units:", min_value=1, value=1)

# --- 4. CALCULATION LOGIC ---
is_trade = "Trade" in usage
total_cost = (quantity * 500) if is_trade else (100000 if quantity >= 10 else quantity * 10000)
lab_assigned = "Legal Metrology" if is_trade else "Industrial Metrology Lab"
col_date = (datetime.now() + timedelta(days=14)).strftime('%d %B, %Y')

# --- 5. SIGNATURE PAD ---
st.subheader("✍️ Applicant Signature")
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=3,
    stroke_color="#000000",
    background_color="#F0F2F6",
    update_streamlit=True,
    height=150,
    key="canvas",
)

# --- 6. PDF GENERATION (STABLE VERSION) ---
def create_pdf(sig_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=85, y=10, w=40)
        pdf.ln(30)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RSB METROLOGY APPLICATION", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Company: {company_name}", ln=True)
    pdf.cell(200, 10, f"Applicant: {applicant_name}", ln=True)
    pdf.cell(200, 10, f"Designated Lab: {lab_assigned}", ln=True)
    pdf.cell(200, 10, f"Total Cost: {total_cost:,} Rwf", ln=True)
    pdf.cell(200, 10, f"Collection Date: {col_date}", ln=True)
    pdf.ln(10)

    # Signature Processing
    if sig_data is not None:
        try:
            # Convert canvas to Image
            img = Image.fromarray(sig_data.astype('uint8'), 'RGBA')
            # Create white background to avoid transparency errors in FPDF
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            # Save to a byte buffer instead of a file for better cloud compatibility
            img_byte_arr = io.BytesIO()
            bg.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Save temp file for FPDF to read
            bg.save("temp_sig.png")
            pdf.cell(200, 10, "Applicant Signature:", ln=True)
            pdf.image("temp_sig.png", w=50)
        except Exception as sig_err:
            st.error(f"Signature error: {sig_err}")

    return pdf.output(dest="S").encode("latin-1")

# --- 7. BUTTON LOGIC ---
st.divider()
if st.button("Generate & Download Slip"):
    # Check if signature exists by looking at the alpha channel (drawing pixels)
    if canvas_result.image_data is not None:
        # Summing pixels to see if user actually drew something
        if np.sum(canvas_result.image_data) > 0:
            if not company_name or not applicant_name:
                st.warning("⚠️ Please fill in all text fields.")
            else:
                try:
                    output_pdf = create_pdf(canvas_result.image_data)
                    st.success("✅ Application generated!")
                    st.download_button(
                        label="📥 Download PDF Slip",
                        data=output_pdf,
                        file_name=f"RSB_Slip_{company_name}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"PDF Generation Error: {e}")
        else:
            st.error("⚠️ Please sign the signature pad before generating.")
    else:
        st.error("⚠️ Signature pad not initialized.")
