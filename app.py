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
    /* Style for the signature box area */
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

# --- 5. PRICING & LAB LOGIC ---
is_trade = "Trade" in usage
if is_trade:
    service_type, lab_assigned, unit_price = "Verification", "Legal Metrology Unit", 500
    total_cost = quantity * unit_price
else:
    service_type, unit_price = "Calibration", 10000
    lab_assigned = next((lab for lab, items in lab_mapping.items() if selected_item in items), "General Metrology Lab")
    # Apply the 100,000 Rwf Cap for Industrial Calibration (10+ items)
    total_cost = 100000 if quantity >= 10 else quantity * unit_price

collection_date = (datetime.now() + timedelta(days=14)).strftime('%d %B, %Y')

# Display summary metrics to user
