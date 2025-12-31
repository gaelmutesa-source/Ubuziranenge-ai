import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os
import io

# --- 1. PAGE CONFIG & FORCED LIGHT THEME ---
st.set_page_config(page_title="Ubuziranenge AI", page_icon="⚖️", layout="centered")

# CSS to fix Dark Mode issues on mobile and style the UI
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #1E3A8A !important; }
    .stButton>button { background-color: #1E3A8A !important; color: white !important; width: 100%; border-radius: 8px; }
    .chat-bubble { background-color: #F0F4F8; padding: 15px; border-radius: 15px; border-left: 5px solid #1E3A8A; margin: 10px 0; }
    [data-testid="stMetricValue"] { color: #1E3A8A !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER & LOGO ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
st.markdown("<h1 style='text-align: center;'>Ubuziranenge AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 20px;'>Metrology service application assistant</p>", unsafe_allow_html=True)
st.divider()

# --- 3. KNOWLEDGE BASE & LOGIC ---
lab_mapping = {
    "Legal Metrology Unit": ["Market Scale", "Fuel Pump", "Water Meter", "Electricity Meter", "Taxi Meter", "Weighbridge"],
    "Mass & Balance Lab": ["Analytical Balance", "Industrial Scale", "Standard Weights"],
    "Temperature & Humidity Lab": ["Thermometer", "Oven/Fridge", "Autoclave/Incubator"],
    "Volume & Flow Lab": ["Micropipette", "Laboratory Glassware", "Prover Tank"],
    "Pressure": ["Pressure Gauge"],
    "Force Lab":["compression and tension machine","cbr","marshall","Triaxial testing machine","torque wrench"],
    "Dimension Lab": ["Vernier Caliper", "Micrometer", "Ruler/Tape Measure"]
}
all_instruments = sorted([item for sublist in lab_mapping.values() for item in sublist])

# --- 4. CUSTOMER INFORMATION ---
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

# --- 5. SERVICE SELECTION ---
st.subheader("⚖️ Service Selection")
col_s1, col_s2 = st.columns(2)
with col_s1:
    selected_item = st.selectbox("Select Instrument:", all_instruments)
    usage = st.radio("Usage Purpose:", ["Trade/Commercial", "Industrial/Scientific"])
with col_s2:
    quantity = st.number_input("Number of Units:", min_value=1, value=1)

# Logic for Assignment and Price
is_trade = "Trade" in usage
if is_trade:
    service_type, lab_assigned, unit_price = "Verification", "Legal Metrology Unit", 500
    total_cost = quantity * unit_price
else:
    service_type, unit_price = "Calibration", 10000
    lab_assigned = next((lab for lab, items in lab_mapping.items() if selected_item in items), "General Metrology Lab")
    total_cost = 100000 if quantity >= 10 else quantity * unit_price

receive_date = datetime.now()
collection_date = (receive_date + timedelta(days=14)).strftime('%d %B, %Y')

# --- 6. CHATBOT ASSISTANT ---
st.divider()
st.subheader("🤖 Ubuziranenge Chatbot")
user_query = st.text_input("Ask me about RSB scope or this application:", placeholder="e.g., How much do I pay?")

if user_query:
    q = user_query.lower()
    if any(word in q for word in ["cost", "price", "pay", "amount"]):
        ans = f"Your total estimated cost for {quantity} unit(s) is **{total_cost:,} Rwf**."
    elif any(word in q for word in ["date", "collection", "pickup", "ready"]):
        ans = f"Your instruments will be ready for collection on **{collection_date}**."
    elif any(word in q for word in ["lab", "where", "room"]):
        ans = f"Your {selected_item} is designated to the **{lab_assigned}**."
    elif any(word in q for word in ["scope", "calibrate", "do you"]):
        ans = "RSB Metrology covers Mass, Volume, Flow, Temperature, Pressure, Force, and Legal Metrology. For medical or unique tools, please call 3250."
    else:
        ans = "For specific technical inquiries outside of this scope, please contact the **RSB Hotline at 3250**."
    st.markdown(f"<div class='chat-bubble'>{ans}</div>", unsafe_allow_html=True)

# --- 7. DIGITAL SIGNATURE ---
st.subheader("✍️ Applicant Signature")
st.write("Please sign below (Touchscreen or Mouse):")
canvas_result = st_canvas(
    stroke_width=2, stroke_color="#000000", background_color="#F8FAFC",
    height=150, update_freq=True, key="canvas",
)

# --- 8. PDF GENERATION FUNCTION ---
def generate_pdf(sig_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=85, y=10, w=40)
        pdf.ln(35)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RWANDA STANDARDS BOARD", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 8, "METROLOGY SERVICE APPLICATION SLIP", ln=True, align='C')
    pdf.ln(10)

    # Info Table
    pdf.set_fill_color(230, 240, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, " CUSTOMER & SERVICE INFORMATION", ln=True, fill=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(100, 8, f"Company: {company_name}", ln=True)
    pdf.cell(100, 8, f"Applicant: {applicant_name} ({contact_number})", ln=True)
    pdf.cell(100, 8, f"Instrument: {selected_item} ({quantity} units)", ln=True)
    
    pdf.set_text_color(30, 58, 138)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 8, f"DESIGNATED LAB: {lab_assigned.upper()}", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.cell(100, 8, f"Total Cost: {total_cost:,} Rwf", ln=True)
    pdf.cell(100, 8, f"Collection Date: {collection_date}", ln=True)

    # Signature
    if sig_data is not None:
        img = Image.fromarray(sig_data.astype('uint8'), 'RGBA')
        bg = Image.new("RGBA", img.size, "WHITE")
        bg.paste(img, (0, 0), img)
        bg.convert('RGB').save("sig.png")
        pdf.ln(5)
        pdf.cell(100, 8, "Applicant Signature:", ln=True)
        pdf.image("sig.png", w=40)

    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, "Note: This is an automated assistant slip. Final verification and invoicing will be done at RSB reception.")
    return pdf.output(dest="S").encode("latin-1")

# --- 9. FINAL ACTIONS ---
st.divider()
if st.button("Generate Final Application Slip"):
    if not company_name or not applicant_name:
        st.error("❌ Please fill in the Customer Information.")
    else:
        st.success("✅ Application Processed!")
        pdf_bytes = generate_pdf(canvas_result.image_data)
        st.download_button(
            label="📥 Download Official Slip (PDF)",
            data=pdf_bytes,
            file_name=f"RSB_Application_{company_name}.pdf",
            mime="application/pdf"
        )
