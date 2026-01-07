import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Jacket Load Distribution", layout="wide")

# -----------------------------
# Jacket minimum % database
# (Relative weight distribution)
# -----------------------------
JACKETS = {
    "H05-CL1": {
        "EAC": {"A": 11.6, "B": 11.4, "C": 22.9, "D": 12.3},
        "OBS": {"A": 17.3, "B": 20.1, "C": 22.9, "D": 17.0},
    }
}

LEG_NAMES = {
    "A": "A (BP)",
    "B": "B (BQ)",
    "C": "C (AQ)",
    "D": "D (AP)",
}

st.title("Offshore Jacket Load Distribution")
st.caption("Real-time monitoring based on levelling cylinder pressures")

# -----------------------------
# Top selectors
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    jacket_id = st.selectbox("Jacket ID", list(JACKETS.keys()))

with col2:
    case = st.radio("Case", ["EAC", "OBS"], horizontal=True)

min_limits = JACKETS[jacket_id][case]

# -----------------------------
# Pressure inputs
# -----------------------------
st.subheader("Pressure Inputs")

pcols = st.columns(4)
pressures = {}

for i, leg in enumerate(["A", "B", "C", "D"]):
    with pcols[i]:
        pressures[leg] = st.number_input(
            LEG_NAMES[leg],
            min_value=0.0,
            value=0.0,
            step=0.1,
            format="%.2f"
        )

total_pressure = sum(pressures.values())

st.markdown(f"**Total Pressure:** `{total_pressure:.2f} bar`")

# -----------------------------
# Load distribution
# -----------------------------
results = []
failed_legs = []

for leg, p in pressures.items():
    pct = (p / total_pressure * 100) if total_pressure > 0 else 0
    min_pct = min_limits[leg]
    ok = pct >= min_pct

    if not ok:
        failed_legs.append(LEG_NAMES[leg])

    results.append({
        "Leg": LEG_NAMES[leg],
        "Pressure (bar)": p,
        "Actual %": pct,
        "Min %": min_pct,
        "Status": "OK" if ok else "Below minimum"
    })

df = pd.DataFrame(results)

# -----------------------------
# Visualization
# -----------------------------
st.subheader("Jacket Visualization")

colors = []
for row in results:
    colors.append("red" if row["Actual %"] < row["Min %"] else "gold")

fig = go.Figure()

x_pos = [0, 1, 2, 3]
for i, leg in enumerate(["A", "B", "C", "D"]):
    fig.add_trace(go.Bar(
        x=[x_pos[i]],
        y=[1],
        width=0.4,
        marker_color=colors[i],
        name=LEG_NAMES[leg],
        text=f"{results[i]['Actual %']:.1f}%",
        textposition="outside"
    ))

fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=x_pos,
        ticktext=[LEG_NAMES[l] for l in ["A", "B", "C", "D"]],
        showgrid=False
    ),
    yaxis=dict(visible=False),
    height=350,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Minimum load requirements
# -----------------------------
st.subheader("Minimum Load Requirements")

mcols = st.columns(4)

for i, row in df.iterrows():
    bg = "#ffe6e6" if row["Status"] == "Below minimum" else "#fff8dc"
    with mcols[i]:
        st.markdown(
            f"""
            <div style="background-color:{bg}; padding:12px; border-radius:8px;">
            <b>{row['Leg']}</b><br>
            Min Required: <b>{row['Min %']:.1f}%</b><br>
            Actual: <b>{row['Actual %']:.1f}%</b><br>
            Status: <b>{row['Status']}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------
# Warning box
# -----------------------------
if failed_legs:
    st.error(
        f"""
        ⚠️ **Legs below minimum requirement:** {", ".join(failed_legs)}

        **Suggested action:**  
        Continue levelling jacket. Remember to fly ROV to the pressurized leg (levelling ind.).
        """
    )
else:
    st.success("All legs meet minimum load requirements.")

st.caption("Conceptual offshore monitoring tool – use in accordance with project procedures.")
