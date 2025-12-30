import streamlit as st
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="Ubuziranenge AI - RSB Guide", page_icon="⚖️")

# --- UI Header ---
st.title("⚖️ Ubuziranenge AI")
st.subheader("RSB Metrology Service Assistant")
st.write("Helping you identify the right laboratory and collection date for your equipment.")

# --- Sidebar Info ---
with st.sidebar:
    st.header("About RSB Metrology")
    st.info("""
    **Rules:**
    - Trade-related items go to **Legal Metrology**.
    - Collection is **14 days** after receipt.
    - Standard Lab Hours: 08:00 - 17:00
    """)

# --- User Inputs ---
with st.container():
    st.write("### Instrument Details")
    instrument_name = st.text_input("What is the name of the instrument?", placeholder="e.g. Digital Scale, Thermometer")
    
    use_case = st.radio(
        "What is the instrument used for?",
        ["Trade/Commercial (Buying/Selling)", "Industrial/Scientific/Medical (Internal Quality)"]
    )

# --- Logic Processing ---
if st.button("Get Designation & Collection Date"):
    if not instrument_name:
        st.warning("Please enter the name of your instrument.")
    else:
        # Lab Mapping Logic
        instrument_lower = instrument_name.lower()
        
        # Industrial Lab Dictionary
        industrial_labs = {
            "Mass & Balance": ["weight", "balance", "scale"],
            "Temperature & Humidity": ["thermometer", "oven", "fridge", "incubator", "autoclave"],
            "Volume & Flow": ["pipette", "burette", "flask", "tank", "meter"],
            "Pressure & Force": ["gauge", "compression", "force", "cbr"],
            "Dimension": ["caliper", "micrometer", "ruler", "tape"]
        }

        # Determine Designation
        if "Trade" in use_case:
            lab_assigned = "Legal Metrology Unit (Verification Service)"
        else:
            lab_assigned = "General Metrology Lab" # Default
            for lab, keywords in industrial_labs.items():
                if any(k in instrument_lower for k in keywords):
                    lab_assigned = f"Industrial Metrology - {lab} Laboratory"
                    break

        # Calculate Dates
        received_date = datetime.now()
        collection_date = received_date + timedelta(days=14)

        # --- Display Results ---
        st.divider()
        st.success(f"### Designation Results")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Designated Laboratory", lab_assigned)
        
        with col2:
            st.metric("Collection Date", collection_date.strftime("%d %B, %Y"))
        
        st.info(f"**Instructions:** Please present your **{instrument_name}** at the RSB reception in Kicukiro. Ensure you have the technical manual if available.")
