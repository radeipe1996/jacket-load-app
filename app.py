import streamlit as st
import streamlit.components.v1 as components

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(
    page_title="Jacket Load Distribution",
    layout="centered"
)

# ----------------------------
# JACKET DATA
# ----------------------------
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
    "D07 (Radar)": {"EAC":{"A":11.8,"B":11.6,"C":22.6,"D":12.1}, "OBS":{"A":17.6,"B":20.4,"C":22.6,"D":16.6}},
    # (remaining jackets omitted for brevity — keep full list in production)
}

LEG_LABELS = {
    "A": "BP (A)",
    "B": "BQ (B)",
    "C": "AQ (C)",
    "D": "AP (D)"
}

# ----------------------------
# UI – HEADER
# ----------------------------
st.title("⚖️ Jacket Load Distribution")
st.caption("Real-time load monitoring during offshore installation")

# ----------------------------
# SELECTIONS
# ----------------------------
st.subheader("Jacket & Case Selection")

jacket_id = st.selectbox("Select Jacket ID", list(JACKETS.keys()))
case = st.radio("Select Case", ["EAC", "OBS"], horizontal=True)

min_targets = JACKETS[jacket_id][case]

# ----------------------------
# PRESSURE INPUTS
# ----------------------------
st.subheader("Leg Pressure Input (bar)")

col1, col2 = st.columns(2)
with col1:
    pA = st.number_input("BP (A)", min_value=0.0, step=0.1)
    pC = st.number_input("AQ (C)", min_value=0.0, step=0.1)
with col2:
    pB = st.number_input("BQ (B)", min_value=0.0, step=0.1)
    pD = st.number_input("AP (D)", min_value=0.0, step=0.1)

pressures = {"A": pA, "B": pB, "C": pC, "D": pD}
total_pressure = sum(pressures.values())

# ----------------------------
# CALCULATIONS
# ----------------------------
if total_pressure > 0:
    percentages = {k: (v / total_pressure) * 100 for k, v in pressures.items()}
else:
    percentages = {k: 0 for k in pressures}

# ----------------------------
# RESULTS SUMMARY
# ----------------------------
st.subheader("Results")

st.metric("Total Pressure (bar)", f"{total_pressure:.2f}")

# ----------------------------
# JACKET VISUALIZATION
# ----------------------------
st.subheader("Jacket Load Distribution")

def leg_box(label, value, minimum):
    color = "#2ecc71" if value >= minimum else "#e74c3c"
    return f"""
    <div style="
        background-color:{color};
        color:white;
        padding:12px;
        border-radius:12px;
        text-align:center;
        font-size:14px;
        min-height:90px;
        box-sizing:border-box;">
        <strong>{label}</strong><br>
        {value:.1f}%<br>
        <span style="font-size:12px;">Min: {minimum:.1f}%</span>
    </div>
    """

html_layout = f"""
<div style="
    font-family: Arial, sans-serif;
    max-width:360px;
    margin:auto;">

    <div style="
        display:grid;
        grid-template-columns: 1fr 1fr;
        gap:12px;">

        <!-- BP (A) + BL -->
        <div>
    {leg_box("BP (A)", percentages["A"], min_targets["A"])}
    <div style="
        background-color:#7f8c8d;
        color:white;
        padding:8px;
        border-radius:8px;
        text-align:center;
        font-size:12px;
        width:60px;
        margin-top:6px;">
        BL
    </div>
</div>

        <!-- BQ (B) -->
        <div>
            {leg_box("BQ (B)", percentages["B"], min_targets["B"])}
        </div>

        <!-- AQ (C) -->
        <div>
            {leg_box("AQ (C)", percentages["C"], min_targets["C"])}
        </div>

        <!-- AP (D) -->
        <div>
            {leg_box("AP (D)", percentages["D"], min_targets["D"])}
        </div>
    </div>

    <!-- Center Jacket ID -->
    <div style="
        margin-top:14px;
        background-color:#34495e;
        color:white;
        padding:12px;
        border-radius:12px;
        text-align:center;
        font-size:14px;">
        <strong>{jacket_id}</strong>
    </div>

</div>
"""

components.html(html_layout, height=420)

# ----------------------------
# WARNINGS
# ----------------------------
failed_legs = [
    LEG_LABELS[k] for k in percentages
    if percentages[k] < min_targets[k]
]

if failed_legs:
    st.warning(
        f"⚠️ Minimum load distribution NOT achieved on: {', '.join(failed_legs)}\n\n"
        "Suggested action:\n"
        "Re-level the jacket. Remember to watch the level indicator while levelling."
    )
else:
    st.success("✅ All legs meet minimum load distribution requirements.")
