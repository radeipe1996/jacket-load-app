import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import os
import time

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Jacket Load Distribution",
    layout="centered"
)
# Initialize a session key so the modal only shows up once per page load
if "popup_acknowledged" not in st.session_state:
    st.session_state["popup_acknowledged"] = False

if not st.session_state["popup_acknowledged"]:
    # Using st.components.v1.html with full height allows the overlay to stretch across the viewport
    components.html(
        """
        <div id="customModal" style="
            position: fixed; 
            top: 0; left: 0; width: 100vw; height: 100vh; 
            background-color: rgba(0,0,0,0.85); 
            z-index: 999999; 
            display: flex; 
            justify-content: center; 
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="
                background-color: white; 
                padding: 35px; 
                border-radius: 12px; 
                max-width: 400px; 
                width: 85%;
                text-align: center; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <div style="font-size: 16px; color: #2c3e50; line-height: 1.6; margin-bottom: 28px; white-space: pre-line; font-weight: 500;">
                    Click Ok to continue.

                    By clicking "Ok" I also admit that Raul is the prettiest PE.
                </div>
                <button onclick="window.parent.document.dispatchEvent(new CustomEvent('closeModal')); document.getElementById('customModal').style.display='none';" style="
                    background-color: #2ecc71; 
                    color: white; 
                    border: none; 
                    padding: 12px 40px; 
                    font-size: 15px; 
                    font-weight: bold;
                    border-radius: 6px; 
                    cursor: pointer;
                    box-shadow: 0 4px 6px rgba(46, 204, 113, 0.2);
                    transition: all 0.2s;">
                    Ok
                </button>
            </div>
        </div>
        <script>
            // Communicate back to Streamlit when they click OK so it unmounts cleanly
            document.querySelector('button').addEventListener('click', function() {
                window.parent.postMessage({type: 'streamlit:popup_close'}, '*');
            });
        </script>
        """,
        height=600, # Give it space to render the overlay globally
    )
    
    # Check for the close signal from our JavaScript to update the app state
    import json
    from streamlit_javascript import st_javascript

if "show_register" not in st.session_state:
    st.session_state["show_register"] = False

if "delete_last" not in st.session_state:
    st.session_state["delete_last"] = False
    
# ----------------------------
# DATA
# ----------------------------
REGISTER_FILE = "pressure_register.csv"

JACKETS = {
    "G05": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "H05": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "J05": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.9,"D":16.9}},
    "J04": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "K04": {"EAC":{"A":11.6,"B":11.5,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "L04": {"EAC":{"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":22.8,"D":17.4}},
    "M04": {"EAC":{"A":11.6,"B":11.2,"C":22.9,"D":12.6}, "OBS":{"A":17.4,"B":19.6,"C":22.9,"D":17.4}},
    "L05": {"EAC":{"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":22.8,"D":17.4}},
    "M05": {"EAC":{"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS":{"A":17.4,"B":19.6,"C":22.8,"D":17.4}},
    "L06": {"EAC":{"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":22.8,"D":17.4}},
    "M06": {"EAC":{"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS":{"A":17.4,"B":19.6,"C":22.8,"D":17.4}},
    "L07": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "M07": {"EAC":{"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS":{"A":17.4,"B":19.6,"C":22.8,"D":17.4}},
    "F05": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.4}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "D05": {"EAC":{"A":11.9,"B":11.4,"C":22.3,"D":12.3}, "OBS":{"A":17.8,"B":20.1,"C":22.3,"D":17.0}},
    "E05": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.4}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "E04": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.4}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "G04": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.4}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "K07": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "J07": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "H07": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "G07": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "F07": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "E07": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "D07 (Radar)": {"EAC":{"A":11.8,"B":11.6,"C":22.6,"D":12.1}, "OBS":{"A":17.6,"B":20.4,"C":22.6,"D":16.6}},
    "D06": {"EAC":{"A":12.0,"B":11.4,"C":22.2,"D":12.3}, "OBS":{"A":17.9,"B":20.1,"C":22.2,"D":16.9}},
    "E06": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "F06": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "G06": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "H06": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "J06": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "K06": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "K05": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "L03": {"EAC":{"A":11.6,"B":11.2,"C":22.9,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":22.9,"D":17.4}},
    "M03": {"EAC":{"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS":{"A":17.4,"B":19.6,"C":22.8,"D":17.4}},
    "L02": {"EAC":{"A":11.6,"B":11.2,"C":22.9,"D":12.7}, "OBS":{"A":17.2,"B":19.6,"C":22.9,"D":17.5}},
    "M01": {"EAC":{"A":11.6,"B":11.2,"C":23.0,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":23.0,"D":17.4}},
    "M02": {"EAC":{"A":11.6,"B":11.1,"C":22.9,"D":12.7}, "OBS":{"A":17.3,"B":19.6,"C":22.9,"D":17.5}},
    "K01": {"EAC":{"A":12.0,"B":11.4,"C":22.2,"D":12.3}, "OBS":{"A":17.9,"B":20.1,"C":22.2,"D":16.9}},
    "L01": {"EAC":{"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":22.8,"D":17.4}},
    "J01": {"EAC":{"A":11.6,"B":10.8,"C":22.9,"D":13.1}, "OBS":{"A":17.3,"B":19.0,"C":22.9,"D":18.0}},
    "A02": {"EAC":{"A":11.6,"B":11.1,"C":22.9,"D":12.7}, "OBS":{"A":17.3,"B":19.6,"C":22.9,"D":17.5}},
    "A03": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "A04": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "H04": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "H01": {"EAC":{"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":22.8,"D":17.4}},
    "H02": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "G02": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "D04": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "E03": {"EAC":{"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":22.8,"D":17.4}},
    "C04": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "B04": {"EAC":{"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS":{"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "B02": {"EAC":{"A":11.6,"B":11.2,"C":23.0,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":23.0,"D":17.4}},
    "B03": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "C02": {"EAC":{"A":11.6,"B":11.2,"C":23.0,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":23.0,"D":17.4}},
    "C03": {"EAC":{"A":11.6,"B":11.2,"C":22.9,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":22.9,"D":17.4}},
    "E02": {"EAC":{"A":11.6,"B":11.2,"C":23.0,"D":12.6}, "OBS":{"A":17.3,"B":19.6,"C":23.0,"D":17.4}},
    "D03": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "F02": {"EAC":{"A":11.9,"B":11.4,"C":22.4,"D":12.3}, "OBS":{"A":17.8,"B":20.1,"C":22.4,"D":16.9}},
    "E01": {"EAC":{"A":11.9,"B":11.4,"C":22.4,"D":12.3}, "OBS":{"A":17.8,"B":20.1,"C":22.4,"D":16.9}},
    "F01": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "G01": {"EAC":{"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS":{"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
}

CLUSTERS = {
    "J04": "CL 2", "J05": "CL 2", "K04": "CL 2", "L05": "CL 2",
    "H05": "CL 1", "M04": "CL 2", "G05": "CL 1", "L04": "CL 2",
    "M05": "CL 2", "F05": "CL 3", "M07": "CL 2", "M06": "CL 2",
    "L06": "CL 2", "D05": "CL 3", "L07": "CL 2", "E05": "CL 3",
    "H07": "CL 2", "J07": "CL 2", "K07": "CL 2", "K06": "CL 2",
    "K05": "CL 2", "G07": "CL 2", "F06": "CL 2", "H06": "CL 2",
    "G06": "CL 2", "J06": "CL 2", "E06": "CL 1", "E07": "CL 1",
    "F07": "CL 1", "D06": "CL 2", "D07": "CL 1", "E04": "CL 3",
    "G04": "CL 3", "M01": "CL 1", "A04": "CL 1", "A02": "CL 3",
    "A03": "CL 1", "L03": "CL 1", "J01": "CL 3", "M02": "CL 3",
    "L02": "CL 3", "K01": "CL 2", "M03": "CL 2", "L01": "CL 2",
    "H04": "CL 2", "G02": "CL 2", "E03": "CL 2", "H02": "CL 2",
    "H01": "CL 2", "B04": "CL 2", "D04": "CL 2", "B03": "CL 1",
    "C04": "CL 2", "B02": "CL 1", "E02": "CL 1", "D03": "CL 1",
    "C02": "CL 1", "F02": "CL 1", "C03": "CL 1", "E01": "CL 1",
    "F01": "CL 1", "G01": "CL 1"
}

LEG_LABELS = {
    "A": "BP (A)",
    "B": "BQ (B)",
    "C": "AQ (C)",
    "D": "AP (D)"
}

# ----------------------------
# FUNCTIONS
# ----------------------------
from datetime import datetime, timezone

def save_pressures(jacket_id, case, pressures):
    now = datetime.now().strftime("%d/%m/%y %H:%M:%S")

    new_row = {
        "Jacket ID": jacket_id,
        "Case": case,
        "Date Time (UTC)": now,
        "BP (A)": pressures["A"],
        "BQ (B)": pressures["B"],
        "AQ (C)": pressures["C"],
        "AP (D)": pressures["D"],
        "Comment": ""
    }

    if os.path.exists(REGISTER_FILE):
        df = pd.read_csv(REGISTER_FILE)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row])

    df.to_csv(REGISTER_FILE, index=False)
    return len(df) - 1

def load_register():
    if os.path.exists(REGISTER_FILE):
        return pd.read_csv(REGISTER_FILE)
    return pd.DataFrame()

def leg_box(label, pressure, total_pressure, minimum_pct):
    """
    label: leg label
    pressure: actual input pressure in bar
    total_pressure: sum of all leg pressures
    minimum_pct: minimum % required for this leg
    """

    if total_pressure > 0:
        percentage = (pressure / total_pressure) * 100
        pmin = total_pressure * (minimum_pct / 100)
    else:
        percentage = 0
        pmin = 0

    # Color logic (as requested earlier: yellow default, red if below min)
    color = "#2ecc71" if percentage >= minimum_pct else "#e74c3c"

    return f"""
    <div style="
        background-color:{color};
        color:black;
        padding:10px;
        border-radius:12px;
        text-align:center;
        font-size:14px;
        min-height:100px;">
        <strong>{label}</strong><br>
        {percentage:.1f}%<br>
        <span style="font-size:12px;">Min: {minimum_pct:.1f}%</span><br>
        <span style="font-size:14px;">P: {pressure:.0f} bar</span><br>
        <span style="font-size:12px;">Pmin: {pmin:.0f} bar</span>
    </div>
    """

# ----------------------------
# HEADER
# ----------------------------

components.html(f"""
<div style="text-align:center; margin-bottom:8px;">
    <img src="https://nigerianbelgian.org/wp-content/uploads/2025/08/DEME-Group.png" style="width:200px;"/>
</div>
""", height=60)

st.markdown("""
<div style="text-align:center;">
    <div style="font-size:30px; font-weight:bold;">JKT Levelling ⚖️</div>
    <div style="font-size:14px; color:gray;">Le Treport OWF - DEME OFFSHORE</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# SELECTION
# ----------------------------

jacket_id = st.selectbox("Jacket ID", list(JACKETS.keys()))
case = st.radio("Case", ["EAC", "OBS"], horizontal=True)
min_targets = JACKETS[jacket_id][case]

# ----------------------------
# PRESSURE INPUTS
# ----------------------------
st.subheader("Pressure Input (bar)")
col1, col2 = st.columns(2)

with col1:
    pA = st.number_input("BP (A)", min_value=0.0, step=10.0, format="%.0f")
    pB = st.number_input("BQ (B)", min_value=0.0, step=10.0, format="%.0f")
with col2:
    pC = st.number_input("AQ (C)", min_value=0.0, step=10.0, format="%.0f")
    pD = st.number_input("AP (D)", min_value=0.0, step=10.0, format="%.0f")

pressures = {"A": pA, "B": pB, "C": pC, "D": pD}


# ----------------------------
# CALCULATIONS
# ----------------------------
total_pressure = sum(pressures.values())
if total_pressure > 0:
    percentages = {k: (v / total_pressure) * 100 for k, v in pressures.items()}
else:
    percentages = {k: 0 for k in pressures}

# ----------------------------
# RESULTS
# ----------------------------
st.metric("Total Pressure (bar)", f"{total_pressure:.2f}")

# ----------------------------
# DATA LOGGING (IMMEDIATELY BELOW INPUT)
# ----------------------------
st.subheader("Data Logging")
col_save, col_view = st.columns(2)

# Initialize session state keys
if "last_saved_index" not in st.session_state:
    st.session_state["last_saved_index"] = None
if "can_delete_last" not in st.session_state:
    st.session_state["can_delete_last"] = False
if "show_comment_input" not in st.session_state:
    st.session_state["show_comment_input"] = False

# --- SAVE PRESSURES BUTTON ---
with col_save:
    if st.button("💾 Save Pressures", use_container_width=True):
        now = datetime.now(timezone.utc).strftime("%d/%m/%y %H:%M:%S")

        new_row = {
            "Jacket ID": jacket_id,
            "Case": case,
            "Date Time (UTC)": now,
            "BP (A)": pressures["A"],
            "BQ (B)": pressures["B"],
            "AQ (C)": pressures["C"],
            "AP (D)": pressures["D"],
            "Comment": ""
        }

        if os.path.exists(REGISTER_FILE):
            df = pd.read_csv(REGISTER_FILE)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])

        df.to_csv(REGISTER_FILE, index=False)
        
        # Update State
        st.session_state["last_saved_index"] = len(df) - 1
        st.session_state["can_delete_last"] = True   
        st.session_state["show_comment_input"] = True  # <--- Trigger the box
        
        st.success("Pressures saved! Please add a comment below.")

# --- DYNAMIC COMMENT INPUT ---
if st.session_state["show_comment_input"]:
    st.markdown("---")
    with st.container():
        idx = st.session_state["last_saved_index"]
        # Use a key to ensure the widget state is preserved during typing
        comment_text = st.text_input("📝 Add a comment for this record:", key="current_comment_box")
        
        if st.button("✅ Confirm & Save Comment", type="primary"):
            df = pd.read_csv(REGISTER_FILE)
            df.at[idx, "Comment"] = comment_text
            df.to_csv(REGISTER_FILE, index=False)
            
            st.session_state["show_comment_input"] = False # <--- Hide after saving
            st.success("Comment linked to record!")
            time.sleep(1)
            st.rerun()
    st.markdown("---")

# ----------------------------
# REGISTER DISPLAY AND DELETE
# ----------------------------
placeholder = st.session_state.get("register_placeholder", st.empty())

# Toggle register visibility
with col_view:
    if st.button("📋 Register", use_container_width=True):
        st.session_state["show_register"] = not st.session_state.get("show_register", False)

# Load CSV if register is visible
if st.session_state.get("show_register", False):
    df = load_register()  # Always load the CSV, even on fresh start
    placeholder.subheader("Pressure Register")

    if df.empty:
        placeholder.info("No records available.")
    else:
        placeholder.dataframe(df, use_container_width=True, hide_index=True)

    # --- DELETE LAST MEASUREMENT BUTTON ---
    # Only show delete button if user saved a new record this session
    if st.session_state.get("can_delete_last", False) and not df.empty:
        if st.button("🗑️ Delete Last Measurement"):
            df = df.iloc[:-1]  # Remove last row
            df.to_csv(REGISTER_FILE, index=False)

            # Disable further deletion until next save
            st.session_state["last_saved_index"] = None
            st.session_state["can_delete_last"] = False

            # Flash message
            msg = st.empty()
            msg.success("Last measurement deleted successfully!")
            time.sleep(1)
            msg.empty()

            # Refresh placeholder table
            df = load_register()
            placeholder.empty()
            placeholder.subheader("Pressure Register")
            if df.empty:
                placeholder.info("No records available.")
            else:
                placeholder.dataframe(df, use_container_width=True, hide_index=True)

# ----------------------------
# VISUALIZATION
# ----------------------------
st.subheader("Jacket Visualization")

# Get the cluster for the current selection
current_cluster = CLUSTERS.get(jacket_id, "N/A")

html_layout = f"""
<div style="max-width:360px;margin:auto;font-family:Arial;">

    <div style="
        margin-bottom:8px;
        background-color:#34495e;
        color:white;
        padding:10px;
        border-radius:12px 12px 0 0;
        text-align:center;">
        <strong>{jacket_id}</strong>
    </div>

<div style="
        margin-bottom:8px;
        background-color:#34495e;
        color:white;
        padding:4px;
        border-radius:0 0 10px 10px;
        text-align:center;
        font-size:12px;
        font-weight:bold;">
        {current_cluster}
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">

        <div style="display:flex;align-items:center;gap:8px;">
            <div style="
                background-color:#7f8c8d;
                color:white;
                padding:4px;
                border-radius:6px;
                font-size:11px;
                width:38px;
                height:38px;
                display:flex;
                align-items:center;
                justify-content:center;">
                BL
            </div>
            {leg_box("BP (A)", pressures["A"], total_pressure, min_targets["A"])}
        </div>

            {leg_box("BQ (B)", pressures["B"], total_pressure, min_targets["B"])}
            {leg_box("AP (D)", pressures["D"], total_pressure, min_targets["D"])}
            {leg_box("AQ (C)", pressures["C"], total_pressure, min_targets["C"])}

    </div>
</div>
"""
components.html(html_layout, height=360)

# ----------------------------
# WARNINGS
# ----------------------------
failed = [
    LEG_LABELS[k] for k in percentages
    if percentages[k] < min_targets[k]
]

if failed:
    st.warning(
        f"⚠️ Minimum load distribution NOT achieved on: {', '.join(failed)}\n\n"
        "Suggested action:\n"
        "Re-level the jacket. Watch out the level indicator."
    )
else:
    st.success("✅ All legs meet minimum load distribution requirements.")

# ----------------------------
# COMPLETE THEORETICAL STROKE DATA
# ----------------------------
THEORETICAL_STROKE = {
    "G05": {"BP": 0.0, "BQ": 12.3, "AQ": 0.0, "AP": 12.4},
    "H05": {"BP": 15.3, "BQ": 0.0, "AQ": 15.3, "AP": 0.0},
    "J05": {"BP": 0.0, "BQ": 16.8, "AQ": 0.0, "AP": 16.8},
    "J04": {"BP": 2.7, "BQ": 0.0, "AQ": 2.7, "AP": 0.0},
    "K04": {"BP": 5.5, "BQ": 0.0, "AQ": 5.5, "AP": 0.0},
    "L04": {"BP": 0.0, "BQ": 2.0, "AQ": 0.0, "AP": 2.0},
    "M04": {"BP": 12.1, "BQ": 0.0, "AQ": 12.0, "AP": 0.0},
    "L05": {"BP": 0.0, "BQ": 24.3, "AQ": 0.0, "AP": 24.2},
    "M05": {"BP": 27.4, "BQ": 0.0, "AQ": 27.4, "AP": 0.0},
    "L06": {"BP": 0.0, "BQ": 7.1, "AQ": 0.0, "AP": 7.2},
    "M06": {"BP": 12.0, "BQ": 0.0, "AQ": 12.0, "AP": 0.0},
    "L07": {"BP": 0.0, "BQ": 4.0, "AQ": 0.0, "AP": 4.0},
    "M07": {"BP": 12.0, "BQ": 0.0, "AQ": 12.0, "AP": 0.0},
    "F05": {"BP": 6.0, "BQ": 0.0, "AQ": 6.0, "AP": 0.0},
    "E05": {"BP": 0.0, "BQ": 2.2, "AQ": 0.0, "AP": 2.2},
    "D05": {"BP": 0.0, "BQ": 3.4, "AQ": 0.0, "AP": 3.4},
    "E04": {"BP": 7.9, "BQ": 3.4, "AQ": 7.9, "AP": 3.4},
    "G04": {"BP": 0.0, "BQ": 0.0, "AQ": 0.0, "AP": 0.0},
    "K05": {"BP": 3.1, "BQ": 3.4, "AQ": 3.1, "AP": 3.4},
    "K06": {"BP": 0.0, "BQ": 14.0, "AQ": 0.0, "AP": 14.0},
    "K07": {"BP": 0.0, "BQ": 0.0, "AQ": 0.0, "AP": 0.0},
    "J07": {"BP": 11.2, "BQ": 0.0, "AQ": 11.2, "AP": 0.0},
    "H07": {"BP": 2.2, "BQ": 0.0, "AQ": 2.2, "AP": 0.0},
    "G07": {"BP": 0.0, "BQ": 0.0, "AQ": 0.0, "AP": 0.0},
    "J06": {"BP": 0.0, "BQ": 11.3, "AQ": 0.0, "AP": 11.3},
    "H06": {"BP": 0.0, "BQ": 11.4, "AQ": 0.0, "AP": 10.9},
    "G06": {"BP": 12.0, "BQ": 0.0, "AQ": 12.0, "AP": 0.0},
    "F06": {"BP": 5.2, "BQ": 0.0, "AQ": 5.2, "AP": 0.0},
    "D06": {"BP": 3.9, "BQ": 0.0, "AQ": 3.9, "AP": 0.0},
    "F07": {"BP": 4.1, "BQ": 0.0, "AQ": 4.0, "AP": 0.0},
    "E07": {"BP": 4.4, "BQ": 0.0, "AQ": 4.4, "AP": 0.0},
    "D07 (Radar)": {"BP": 0.0, "BQ": 8.8, "AQ": 0.0, "AP": 8.8},
    "E06": {"BP": 15.1, "BQ": 0.0, "AQ": 15.1, "AP": 0.0},
    "L03": {"BP": 6.1, "BQ": 0.0, "AQ": 6.1, "AP": 0.0},
    "M01": {"BP": 1.7, "BQ": 4.4, "AQ": 1.6, "AP": 4.5},
    "A04": {"BP": 0.0, "BQ": 2.7, "AQ": 0.0, "AP": 2.6},
    "A03": {"BP": 1.3, "BQ": 1.3, "AQ": 1.3, "AP": 1.3},
    "A02": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "J01": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "L02": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "M02": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "M03": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "L01": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "K01": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "H04": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "H01": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "H02": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "G02": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "E03": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "D04": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "C04": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "B04": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "B03": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "B02": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "C03": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "C02": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "D03": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "E02": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "F02": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "E01": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "F01": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
    "G01": {"BP": 9999.0, "BQ": 9999.0, "AQ": 9999.0, "AP": 9999.0},
}

# ----------------------------
# HINT BUTTON (TOGGLE)
# ----------------------------
if "show_hint" not in st.session_state:
    st.session_state["show_hint"] = False

if st.button("💡 Hint"):
    # Toggle hint visibility
    st.session_state["show_hint"] = not st.session_state["show_hint"]

# Display or hide hint based on session state
if st.session_state["show_hint"]:
    stroke = THEORETICAL_STROKE.get(jacket_id, None)
    if stroke:
        st.info(
            f"Theoretical stroke per leg for jacket {jacket_id}:\n\n"
            f"BP (A): {stroke['BP']} mm\n"
            f"BQ (B): {stroke['BQ']} mm\n"
            f"AQ (C): {stroke['AQ']} mm\n"
            f"AP (D): {stroke['AP']} mm"
        )
    else:
        st.warning("No theoretical stroke data available for this jacket.")
