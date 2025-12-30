import streamlit as st
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="Ubuziranenge AI", page_icon="⚖️")

st.title("⚖️ Ubuziranenge AI")
st.subheader("RSB Metrology Service Assistant")

# --- 1. Define the Knowledge Base (Dropdown Options) ---
# Each key is the Laboratory, and the list contains common instruments for that lab.
instrument_data = {
    "Legal Metrology (Trade)": [
        "Market Scale", "Fuel Pump/Dispenser", "Water Meter", 
        "Electricity Meter", "Taxi Meter", "Weighbridge", "Pre-packaged Goods"
    ],
    "Mass & Balance": ["Analytical Balance", "Industrial Scale", "Standard Weights", "Moisture Analyzer"],
    "Temperature & Humidity": ["Digital Thermometer", "Oven", "Refrigerator", "Autoclave", "Incubator", "Data Logger"],
    "Volume & Flow": ["Micropipette", "Laboratory Glassware", "Prover Tank", "Flow Meter"],
    "Pressure": ["Pressure Gauge"],
    "Force":["Compression Machine", "Torque Wrench", "Load Cell","cbr"],
    "Dimension": ["dial gauge","Vernier Caliper", "Micrometer", "Steel Ruler", "Tape Measure"]
}

# Create a flat list for the dropdown
all_instruments = []
for lab_category in instrument_data:
    all_instruments.extend(instrument_data[lab_category])
all_instruments.sort()
all_instruments.append("Other (Not in list)")

# --- 2. User Inputs ---
with st.container():
    st.write("### Step 1: Select your Equipment")
    
    selected_instrument = st.selectbox(
        "Which instrument are you bringing to RSB?",
        options=all_instruments
    )

    # Specific use case question to satisfy the "Trade" rule
    use_case = st.radio(
        "What is the intended use?",
        ["Commercial Trade (Buying/Selling/Billing)", "Internal Quality Control / Scientific Research"]
    )

# --- 3. Logic Processing ---
if st.button("Generate Service Slip"):
    
    # Rule 1: Trade always goes to Legal Metrology
    if "Commercial Trade" in use_case:
        lab_assigned = "Legal Metrology Unit"
        service_type = "Verification"
    else:
        # Rule 2: Find the specific Industrial Lab
        lab_assigned = "General Metrology Lab" # Default
        service_type = "Calibration"
        
        for lab, instruments in instrument_data.items():
            if selected_instrument in instruments:
                lab_assigned = lab
                break
    
    # Rule 3: Date Calculation
    received_date = datetime.now()
    collection_date = received_date + timedelta(days=14)

    # --- 4. Display Results ---
    st.divider()
    st.success("### Service Designation")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Instrument:** {selected_instrument}")
        st.write(f"**Designated Lab:** {lab_assigned}")
        st.write(f"**Service Type:** {service_type}")
    
    with col2:
        st.metric("Collection Date", collection_date.strftime("%d %B, %Y"))
        st.write(f"*Received: {received_date.strftime('%d %B, %Y')}*")

    st.warning("⚠️ **Note:** Please ensure the instrument is clean and accompanied by its power cables or accessories.")# --- Improved Designation Logic ---
        if "Trade" in use_case:
            lab_assigned = "Legal Metrology Unit (Verification Service)"
        else:
            # Default if no keyword is found
            lab_assigned = "Industrial Metrology (General Lab)" 
            
            # Dictionary of labs and keywords
            industrial_labs = {
                "Mass & Balance": ["weight", "balance", "scale", "mass"],
                "Temperature & Humidity": ["thermometer", "oven", "fridge", "incubator", "autoclave", "cold room"],
                "Volume & Flow": ["pipette", "burette", "flask", "tank", "meter", "glassware"],
                "Pressure": ["pressure gauge"],
                "Force":["cbr","torque wrench","compression and tension machine","marshall"],
                "Dimension": ["dial gauge","caliper", "micrometer", "ruler", "tape", "height"]
            }

            # Search for the lab name based on keywords
            for lab_name, keywords in industrial_labs.items():
                if any(word in instrument_lower for word in keywords):
                    lab_assigned = f"Industrial Metrology - {lab_name}"
                    break # Stop looking once we find a matchimport streamlit as st
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
            "Pressure": ["pressure gauge"],
            "Force":["cbr","marshall","torque wrench","compression and tension machine"],
            "Dimension": ["caliper", "micrometer", "ruler", "tape","dial gauge"]
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
