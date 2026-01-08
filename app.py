import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Jacket Load Distribution", layout="wide")

LEG_NAMES = {
    "A": "A (BP)",
    "B": "B (BQ)",
    "C": "C (AQ)",
    "D": "D (AP)",
}

# -------------------------------------------------
# FULL APPROVED JACKET DATABASE
# Relative weight distribution between piles [%]
# -------------------------------------------------
JACKETS = {
    # CLUSTER 1
    "G05-CL1": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "H05-CL1": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "F07-CL1": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "E07-CL1": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "A03-CL1": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "A04-CL1": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "D03-CL1": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "E06-CL1": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "F01-CL1": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "G01-CL1": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},

    # CLUSTER 2
    "J05-CL2": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.3}, "OBS": {"A":17.4,"B":20.1,"C":22.9,"D":16.9}},
    "J04-CL2": {"EAC": {"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS": {"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "K04-CL2": {"EAC": {"A":11.6,"B":11.5,"C":22.8,"D":12.3}, "OBS": {"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "L04-CL2": {"EAC": {"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS": {"A":17.3,"B":19.6,"C":22.8,"D":17.4}},
    "M04-CL2": {"EAC": {"A":11.6,"B":11.2,"C":22.9,"D":12.6}, "OBS": {"A":17.4,"B":19.6,"C":22.9,"D":17.4}},
    "L05-CL2": {"EAC": {"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS": {"A":17.3,"B":19.6,"C":22.8,"D":17.4}},
    "M05-CL2": {"EAC": {"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS": {"A":17.4,"B":19.6,"C":22.8,"D":17.4}},
    "L06-CL2": {"EAC": {"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS": {"A":17.3,"B":19.6,"C":22.8,"D":17.4}},
    "M06-CL2": {"EAC": {"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS": {"A":17.4,"B":19.6,"C":22.8,"D":17.4}},
    "L07-CL2": {"EAC": {"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS": {"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "M07-CL2": {"EAC": {"A":11.6,"B":11.2,"C":22.8,"D":12.6}, "OBS": {"A":17.4,"B":19.6,"C":22.8,"D":17.4}},
    "K07-CL2": {"EAC": {"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS": {"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "J07-CL2": {"EAC": {"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS": {"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "H07-CL2": {"EAC": {"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS": {"A":17.4,"B":20.1,"C":22.8,"D":16.9}},
    "G07-CL2": {"EAC": {"A":11.6,"B":11.4,"C":22.8,"D":12.3}, "OBS": {"A":17.4,"B":20.1,"C":22.8,"D":16.9}},

    # CLUSTER 3
    "F05-CL3": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.4}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "D05-CL3": {"EAC": {"A":11.9,"B":11.4,"C":22.3,"D":12.3}, "OBS": {"A":17.8,"B":20.1,"C":22.3,"D":17.0}},
    "E05-CL3": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.4}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "E04-CL3": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.4}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "G04-CL3": {"EAC": {"A":11.6,"B":11.4,"C":22.9,"D":12.4}, "OBS": {"A":17.3,"B":20.1,"C":22.9,"D":17.0}},
    "L02-CL3": {"EAC": {"A":11.6,"B":11.2,"C":22.9,"D":12.7}, "OBS": {"A":17.2,"B":19.6,"C":22.9,"D":17.5}},
    "M02-CL3": {"EAC": {"A":11.6,"B":11.1,"C":22.9,"D":12.7}, "OBS": {"A":17.3,"B":19.6,"C":22.9,"D":17.5}},
    "J01-CL3": {"EAC": {"A":11.6,"B":10.8,"C":22.9,"D":13.1}, "OBS": {"A":17.3,"B":19.0,"C":22.9,"D":18.0}},
    "A02-CL3": {"EAC": {"A":11.6,"B":11.1,"C":22.9,"D":12.7}, "OBS": {"A":17.3,"B":19.6,"C":22.9,"D":17.5}},
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

limits = JACKETS[jacket_id][case]

st.subheader("Pressure Inputs")
cols = st.columns(4)
pressures = {}

for i, leg in enumerate(["A","B","C","D"]):
    with cols[i]:
        pressures[leg] = st.number_input(
            LEG_NAMES[leg], min_value=0.0, value=0.0, step=0.1
        )

total_pressure = sum(pressures.values())
st.markdown(f"**Total Pressure:** `{total_pressure:.2f} bar`")

results, failed = [], []
for leg, p in pressures.items():
    pct = (p / total_pressure * 100) if total_pressure > 0 else 0
    if pct < limits[leg]:
        failed.append(LEG_NAMES[leg])
    results.append((LEG_NAMES[leg], pct, limits[leg]))

st.subheader("Jacket Visualization")
colors = ["red" if r[1] < r[2] else "gold" for r in results]

fig = go.Figure()
for i, r in enumerate(results):
    fig.add_bar(x=[i], y=[1], marker_color=colors[i], text=f"{r[1]:.1f}%", textposition="outside")

fig.update_layout(
    xaxis=dict(tickmode="array", tickvals=list(range(4)), ticktext=[r[0] for r in results]),
    yaxis=dict(visible=False),
    showlegend=False,
    height=320
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Minimum Load Requirements")
cols = st.columns(4)
for i, r in enumerate(results):
    bg = "#ffe6e6" if r[1] < r[2] else "#fff8dc"
    with cols[i]:
        st.markdown(
            f"<div style='background:{bg};padding:10px;border-radius:8px;'>"
            f"<b>{r[0]}</b><br>Min: {r[2]:.1f}%<br>Actual: {r[1]:.1f}%</div>",
            unsafe_allow_html=True
        )

if failed:
    st.error(
        f"⚠️ **Legs below minimum requirement:** {', '.join(failed)}\n\n"
        "**Suggested action:** Continue levelling jacket. "
        "Remember to fly ROV to the pressurized leg (levelling ind.)."
    )
else:
    st.success("All legs meet minimum load requirements.")

st.caption("Operational monitoring tool – use in accordance with project procedures.")
