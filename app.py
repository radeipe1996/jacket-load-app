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
# FULL 62-JACKET DATABASE (EAC / OBS)
# Source: Relative weight distribution between piles
# -------------------------------------------------
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

# ---------------- UI & LOGIC (unchanged) ----------------
st.title("Offshore Jacket Load Distribution")
st.caption("Real-time monitoring based on levelling cylinder pressures")

# ---------------- Input ----------------
jacket_id = st.selectbox("Jacket ID", sorted(JACKETS.keys()))
case = st.radio("Case", ["EAC", "OBS"], horizontal=True)
limits = JACKETS[jacket_id][case]

cols = st.columns(4)
pressures = {}
for i, leg in enumerate(["A","B","C","D"]):
    with cols[i]:
        pressures[leg] = st.number_input(LEG_NAMES[leg], min_value=0.0, step=0.1)

total = sum(pressures.values())
st.markdown(f"**Total Pressure:** `{total:.2f} bar`")

results, failed = [], []
for leg, p in pressures.items():
    pct = (p / total * 100) if total > 0 else 0
    if pct < limits[leg]:
        failed.append(LEG_NAMES[leg])
    results.append((LEG_NAMES[leg], pct, limits[leg]))

# ---------------- Jacket Visualization ----------------
st.subheader("Jacket Load Distribution")

leg_positions = {
    "A": (0, 1),
    "B": (1, 1),
    "C": (1, 0),
    "D": (0, 0),
}

fig = go.Figure()

for leg, (x, y) in leg_positions.items():
    actual = next(r[1] for r in results if r[0].startswith(leg))
    minimum = limits[leg]

    # Color coding
    if actual < minimum:
        color = "red"
    elif actual < minimum + 5:
        color = "yellow"
    else:
        color = "green"

    # Bold letters and bold % values, bigger text
    fig.add_trace(
        go.Scatter(
            x=[x],
            y=[y],
            mode="markers+text",
            marker=dict(
                size=100,  # slightly bigger
                color=color,
                symbol="square",
                line=dict(width=2, color="black"),
            ),
            text=[f"<b style='color:black'>{leg}</b><br>"
                  f"<b>{actual:.1f}%</b> / <b>{minimum:.1f}%</b>"],
            textposition="middle center",
            textfont=dict(size=16),  # bigger text
            hoverinfo="skip",
            showlegend=False,
        )
    )

# Draw jacket frame
fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=0)
fig.add_shape(type="line", x0=1, y0=0, x1=1, y1=1)
fig.add_shape(type="line", x0=1, y0=1, x1=0, y1=1)
fig.add_shape(type="line", x0=0, y0=1, x1=0, y1=0)

fig.update_layout(
    xaxis=dict(visible=False, range=[-0.3, 1.3]),
    yaxis=dict(visible=False, range=[-0.3, 1.3]),
    height=450,
    margin=dict(l=20, r=20, t=20, b=20),
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- Pressure Min/Actual fields ----------------
cols = st.columns(4)
for i, r in enumerate(results):
    bg = "#ffe6e6" if r[1] < r[2] else "#fff8dc"
    with cols[i]:
        st.markdown(
            f"<div style='background:{bg};padding:10px;border-radius:8px;'>"
            f"<br>"  # one line space for all legs
            f"<b>{r[0]}</b><br>"
            f"Min: {r[2]:.1f}%<br>Actual: {r[1]:.1f}%</div>",
            unsafe_allow_html=True
        )

# ---------------- Warning ----------------
if failed:
    st.error(
        f"⚠️ **Legs below minimum requirement:** {', '.join(failed)}\n\n"
        " \n"  # extra space between warning and fields
        "**Suggested action:** Continue levelling jacket. "
        "Remember to fly ROV to the pressurized leg (levelling ind.)."
    )
else:
    st.success("All legs meet minimum load requirements.")
