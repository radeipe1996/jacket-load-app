import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Jacket Load Distribution", layout="wide")

LEG_NAMES = {
    "A": "A (BP)",
    "B": "B (BQ)",
    "C": "C (AQ)",
    "D": "D (AP)",
}

# -------------------------------------------------
# FULL JACKET DATABASE
# Relative weight distribution EAC / OBS [%]
# -------------------------------------------------
JACKETS = {
    "G05-CL1": {"EAC": {"A": 11.6, "B": 11.4, "C": 22.9, "D": 12.3}, "OBS": {"A": 17.3, "B": 20.1, "C": 22.9, "D": 17.0}},
    "H05-CL1": {"EAC": {"A": 11.6, "B": 11.4, "C": 22.9, "D": 12.3}, "OBS": {"A": 17.3, "B": 20.1, "C": 22.9, "D": 17.0}},
    "J05-CL2": {"EAC": {"A": 11.6, "B": 11.4, "C": 22.9, "D": 12.3}, "OBS": {"A": 17.4, "B": 20.1, "C": 22.9, "D": 16.9}},
    "J04-CL2": {"EAC": {"A": 11.6, "B": 11.4, "C": 22.8, "D": 12.3}, "OBS": {"A": 17.4, "B": 20.1, "C": 22.8, "D": 16.9}},
    "K04-CL2": {"EAC": {"A": 11.6, "B": 11.5, "C": 22.8, "D": 12.3}, "OBS": {"A": 17.4, "B": 20.1, "C": 22.8, "D": 16.9}},
    "L04-CL2": {"EAC": {"A": 11.6, "B": 11.2, "C": 22.8, "D": 12.6}, "OBS": {"A": 17.3, "B": 19.6, "C": 22.8, "D": 17.4}},
    "M04-CL2": {"EAC": {"A": 11.6, "B": 11.2, "C": 22.9, "D": 12.6}, "OBS": {"A": 17.4, "B": 19.6, "C": 22.9, "D": 17.4}},
    "L05-CL2": {"EAC": {"A": 11.6, "B": 11.2, "C": 22.8, "D": 12.6}, "OBS": {"A": 17.3, "B": 19.6, "C": 22.8, "D": 17.4}},
    "M05-CL2": {"EAC": {"A": 11.6, "B": 11.2, "C": 22.8, "D": 12.6}, "OBS": {"A": 17.4, "B": 19.6, "C": 22.8, "D": 17.4}},
    "F05-CL3": {"EAC": {"A": 11.6, "B": 11.4, "C": 22.9, "D": 12.4}, "OBS": {"A": 17.3, "B": 20.1, "C": 22.9, "D": 17.0}},
    "D05-CL3": {"EAC": {"A": 11.9, "B": 11.4, "C": 22.3, "D": 12.3}, "OBS": {"A": 17.8, "B": 20.1, "C": 22.3, "D": 17.0}},
    "E05-CL3": {"EAC": {"A": 11.6, "B": 11.4, "C": 22.9, "D": 12.4}, "OBS": {"A": 17.3, "B": 20.1, "C": 22.9, "D": 17.0}},
    "E04-CL3": {"EAC": {"A": 11.6, "B": 11.4, "C": 22.9, "D": 12.4}, "OBS": {"A": 17.3, "B": 20.1, "C": 22.9, "D": 17.0}},
    "G04-CL3": {"EAC": {"A": 11.6, "B": 11.4, "C": 22.9, "D": 12.4}, "OBS": {"A": 17.3, "B": 20.1, "C": 22.9, "D": 17.0}},
}

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("Offshore Jacket Load Distribution")
st.caption("Real-time monitoring based on levelling cylinder pressures")

col1, col2 = st.columns(2)
with col1:
    jacket_id = st.selectbox("Jacket ID", sorted(JACKETS.keys()))
with col2:
    case = st.radio("Case", ["EAC", "OBS"], horizontal=True)

min_limits = JACKETS[jacket_id][case]

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

results = []
failed_legs = []

for leg, p in pressures.items():
    pct = (p / total_pressure * 100) if total_pressure > 0 else 0
    min_pct = min_limits[leg]
    if pct < min_pct:
        failed_legs.append(LEG_NAMES[leg])
    results.append({
        "Leg": LEG_NAMES[leg],
        "Actual %": pct,
        "Min %": min_pct
    })

st.subheader("Jacket Visualization")

colors = ["red" if r["Actual %"] < r["Min %"] else "gold" for r in results]

fig = go.Figure()
for i, r in enumerate(results):
    fig.add_trace(go.Bar(
        x=[i],
        y=[1],
        marker_color=colors[i],
        text=f"{r['Actual %']:.1f}%",
        textposition="outside"
    ))

fig.update_layout(
    xaxis=dict(
        tickmode="array",
        tickvals=list(range(4)),
        ticktext=[r["Leg"] for r in results]
    ),
    yaxis=dict(visible=False),
    showlegend=False,
    height=350
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Minimum Load Requirements")
cols = st.columns(4)

for i, r in enumerate(results):
    bg = "#ffe6e6" if r["Actual %"] < r["Min %"] else "#fff8dc"
    with cols[i]:
        st.markdown(
            f"""
            <div style="background-color:{bg}; padding:12px; border-radius:8px;">
            <b>{r['Leg']}</b><br>
            Min Required: <b>{r['Min %']:.1f}%</b><br>
            Actual: <b>{r['Actual %']:.1f}%</b>
            </div>
            """,
            unsafe_allow_html=True
        )

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

st.caption("Operational monitoring tool – use in accordance with project procedures.")
