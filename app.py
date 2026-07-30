"""
Carbon Footprint Analyzer
-------------------------
A Streamlit app that estimates a household's carbon footprint from
electricity usage, vehicle travel and food habits, then:
  - visualises the emission breakdown
  - projects yearly impact (with a simple ML trend model)
  - benchmarks the user against national / global averages
  - gives a ranked, personalised improvement plan
  - lets the user run "what-if" scenarios
  - exports a downloadable report

No external dataset is required — emission factors are well-known,
publicly published constants, and the small "trend" model is trained
on synthetic data generated inside the app (see model.py).
"""

import io
import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from model import train_trend_model, project_future_emissions

# ----------------------------------------------------------------------
# 1. CONSTANTS  (approximate published emission factors, kg CO2e)
# ----------------------------------------------------------------------
ELECTRICITY_FACTOR = 0.82          # kg CO2e per kWh (grid average, approx.)

VEHICLE_FACTORS = {                # kg CO2e per km
    "Petrol Car": 0.192,
    "Diesel Car": 0.171,
    "CNG Car": 0.142,
    "Electric Car": 0.053,
    "Two-Wheeler (Petrol)": 0.072,
    "Two-Wheeler (Electric)": 0.020,
    "Bus / Public Transport": 0.050,
    "Bicycle / Walk": 0.0,
}

# kg CO2e per day, by diet type
DIET_FACTORS = {
    "Vegan": 1.5,
    "Vegetarian": 1.7,
    "Eggetarian": 2.0,
    "Non-Vegetarian (moderate)": 2.5,
    "Non-Vegetarian (heavy)": 3.3,
}

# Reference benchmarks, tonnes CO2e / year (approximate, widely cited)
BENCHMARKS = {
    "Average Indian": 1.9,
    "Global Average": 4.7,
    "Paris Agreement 2030 target": 2.3,
    "Average American": 14.7,
}

st.set_page_config(page_title="Carbon Footprint Analyzer", page_icon="🌍", layout="wide")

# ----------------------------------------------------------------------
# 2. HEADER
# ----------------------------------------------------------------------
st.title("🌍 Carbon Footprint Analyzer")
st.caption(
    "Estimate your household's carbon emissions from electricity, travel and food, "
    "get an AI-projected yearly impact, and see a personalised plan to cut it down."
)

# ----------------------------------------------------------------------
# 3. SIDEBAR INPUTS
# ----------------------------------------------------------------------
st.sidebar.header("📥 Your Monthly Usage")

electricity_kwh = st.sidebar.number_input(
    "Electricity usage (kWh/month)", min_value=0.0, value=250.0, step=10.0
)

st.sidebar.subheader("🚗 Vehicle Travel")
vehicle_type = st.sidebar.selectbox("Primary vehicle type", list(VEHICLE_FACTORS.keys()))
vehicle_km = st.sidebar.number_input(
    "Distance travelled (km/month)", min_value=0.0, value=500.0, step=10.0
)

st.sidebar.subheader("🍽️ Food Habits")
diet_type = st.sidebar.selectbox("Diet type", list(DIET_FACTORS.keys()), index=3)

st.sidebar.markdown("---")
years_ahead = st.sidebar.slider("Project how many years ahead?", 1, 10, 5)

calculate = st.sidebar.button("Calculate my footprint", type="primary", use_container_width=True)

# ----------------------------------------------------------------------
# 4. CALCULATIONS
# ----------------------------------------------------------------------
def calculate_emissions(electricity_kwh, vehicle_type, vehicle_km, diet_type):
    electricity_emission = electricity_kwh * ELECTRICITY_FACTOR
    vehicle_emission = vehicle_km * VEHICLE_FACTORS[vehicle_type]
    food_emission = DIET_FACTORS[diet_type] * 30  # per month
    return electricity_emission, vehicle_emission, food_emission


def eco_score(yearly_tonnes):
    if yearly_tonnes <= 1.5:
        return "A", "Excellent — well below global averages!"
    elif yearly_tonnes <= 2.5:
        return "B", "Good — around the sustainable target range."
    elif yearly_tonnes <= 4.0:
        return "C", "Average — there's solid room to improve."
    elif yearly_tonnes <= 7.0:
        return "D", "High — significant reduction opportunities exist."
    else:
        return "F", "Very high — a focused action plan is recommended."


def generate_tips(electricity_emission, vehicle_emission, food_emission):
    tips = []
    total = electricity_emission + vehicle_emission + food_emission
    shares = {
        "Electricity": electricity_emission / total if total else 0,
        "Vehicle": vehicle_emission / total if total else 0,
        "Food": food_emission / total if total else 0,
    }
    ranked = sorted(shares.items(), key=lambda x: x[1], reverse=True)

    catalogue = {
        "Electricity": [
            "Switch to LED lighting — cuts lighting energy use by up to 80%.",
            "Use a 5-star rated AC/refrigerator to cut appliance electricity draw.",
            "Install rooftop solar or opt into a green-energy tariff if available.",
            "Unplug idle chargers/devices — phantom load adds up over a month.",
        ],
        "Vehicle": [
            "Carpool or use public transport for 2-3 trips a week.",
            "Switch to an electric or CNG vehicle for your next upgrade.",
            "Combine errands into fewer trips to cut idle mileage.",
            "Try cycling or walking for trips under 3 km.",
        ],
        "Food": [
            "Add 2-3 plant-based meals to your week to lower diet emissions.",
            "Reduce red meat frequency — it has the highest footprint per meal.",
            "Buy local, seasonal produce to cut transport-related food emissions.",
            "Cut down food waste — wasted food wastes all the emissions behind it too.",
        ],
    }

    for category, _ in ranked:
        tips.append((category, catalogue[category]))
    return tips


# ----------------------------------------------------------------------
# 5. MAIN OUTPUT
# ----------------------------------------------------------------------
if calculate or "history" in st.session_state:

    electricity_emission, vehicle_emission, food_emission = calculate_emissions(
        electricity_kwh, vehicle_type, vehicle_km, diet_type
    )
    monthly_total = electricity_emission + vehicle_emission + food_emission
    yearly_total_kg = monthly_total * 12
    yearly_total_tonnes = yearly_total_kg / 1000

    # --- Top metrics ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Monthly Emissions", f"{monthly_total:,.1f} kg CO₂e")
    col2.metric("Yearly Emissions", f"{yearly_total_tonnes:,.2f} tonnes CO₂e")
    grade, grade_msg = eco_score(yearly_total_tonnes)
    col3.metric("Eco Score", grade)
    col4.metric("vs Global Avg", f"{(yearly_total_tonnes / BENCHMARKS['Global Average'] - 1) * 100:+.0f}%")

    st.info(f"**Grade {grade}** — {grade_msg}")

    st.markdown("---")

    # --- Breakdown chart ---
    left, right = st.columns([1, 1.2])

    with left:
        st.subheader("📊 Emission Breakdown")
        labels = ["Electricity", "Vehicle Travel", "Food"]
        values = [electricity_emission, vehicle_emission, food_emission]
        fig1, ax1 = plt.subplots()
        ax1.pie(values, labels=labels, autopct="%1.1f%%", startangle=90,
                colors=["#4C72B0", "#DD8452", "#55A868"])
        ax1.axis("equal")
        st.pyplot(fig1)

    with right:
        st.subheader("📈 Benchmark Comparison")
        bench_df = pd.DataFrame({
            "Category": list(BENCHMARKS.keys()) + ["You"],
            "Tonnes CO2e / year": list(BENCHMARKS.values()) + [yearly_total_tonnes],
        })
        fig2, ax2 = plt.subplots()
        colors = ["#999999"] * len(BENCHMARKS) + ["#C44E52"]
        ax2.barh(bench_df["Category"], bench_df["Tonnes CO2e / year"], color=colors)
        ax2.set_xlabel("Tonnes CO2e / year")
        st.pyplot(fig2)

    st.markdown("---")

    # --- AI trend projection ---
    st.subheader("🤖 AI-Projected Future Impact")
    st.caption(
        "A lightweight regression model — trained on synthetic usage-to-emissions data "
        "that also factors in a gradual grid decarbonisation trend — projects your footprint "
        "if your habits stay roughly the same."
    )
    model = train_trend_model()
    projection_df = project_future_emissions(
        model, electricity_kwh, vehicle_km, DIET_FACTORS[diet_type], years_ahead
    )

    fig3, ax3 = plt.subplots()
    ax3.plot(projection_df["Year"], projection_df["Projected Tonnes CO2e"], marker="o", color="#C44E52", label="Business as usual")
    ax3.plot(projection_df["Year"], projection_df["Improved Tonnes CO2e"], marker="o", color="#55A868", label="If you follow the tips below")
    ax3.set_ylabel("Tonnes CO2e / year")
    ax3.legend()
    st.pyplot(fig3)

    st.dataframe(projection_df.set_index("Year"), use_container_width=True)

    st.markdown("---")

    # --- Personalised tips ---
    st.subheader("💡 Your Personalised Improvement Plan")
    st.caption("Ranked by which category contributes most to your footprint.")
    tips = generate_tips(electricity_emission, vehicle_emission, food_emission)
    for i, (category, tip_list) in enumerate(tips, start=1):
        with st.expander(f"{i}. Focus area: {category}", expanded=(i == 1)):
            for t in tip_list:
                st.write(f"- {t}")

    st.markdown("---")

    # --- What-if simulator ---
    st.subheader("🔮 What-If Simulator")
    c1, c2, c3 = st.columns(3)
    elec_cut = c1.slider("Cut electricity use by (%)", 0, 100, 10)
    vehicle_cut = c2.slider("Cut vehicle travel by (%)", 0, 100, 10)
    diet_cut = c3.slider("Cut food-related emissions by (%)", 0, 100, 10)

    new_monthly = (
        electricity_emission * (1 - elec_cut / 100)
        + vehicle_emission * (1 - vehicle_cut / 100)
        + food_emission * (1 - diet_cut / 100)
    )
    new_yearly_tonnes = new_monthly * 12 / 1000
    saved = yearly_total_tonnes - new_yearly_tonnes

    st.success(
        f"With these changes, your yearly footprint drops to **{new_yearly_tonnes:.2f} tonnes CO₂e** "
        f"— a saving of **{saved:.2f} tonnes** (~{(saved / yearly_total_tonnes * 100 if yearly_total_tonnes else 0):.0f}%)."
    )

    st.markdown("---")

    # --- Downloadable report ---
    st.subheader("⬇️ Download Your Report")
    report = io.StringIO()
    report.write("CARBON FOOTPRINT ANALYZER REPORT\n")
    report.write(f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    report.write(f"Electricity usage: {electricity_kwh} kWh/month\n")
    report.write(f"Vehicle: {vehicle_type}, {vehicle_km} km/month\n")
    report.write(f"Diet type: {diet_type}\n\n")
    report.write(f"Monthly emissions: {monthly_total:.1f} kg CO2e\n")
    report.write(f"Yearly emissions: {yearly_total_tonnes:.2f} tonnes CO2e\n")
    report.write(f"Eco Score: {grade} ({grade_msg})\n\n")
    report.write("Improvement plan:\n")
    for category, tip_list in tips:
        report.write(f"\n[{category}]\n")
        for t in tip_list:
            report.write(f"  - {t}\n")

    st.download_button(
        "Download report (.txt)",
        data=report.getvalue(),
        file_name="carbon_footprint_report.txt",
        mime="text/plain",
    )

    st.session_state["history"] = True

else:
    st.info("👈 Enter your details in the sidebar and click **Calculate my footprint** to get started.")
