
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page setup
st.set_page_config(
    page_title="Pharmacy Demand Forecasting",
    page_icon="💊",
    layout="wide"
)



# Custom dashboard styling
st.markdown("""

<style>
    /* Page */
    .stApp {
        background: #FFFFFF;
        color: #243B53;
    }

    .block-container {
        max-width: 1160px;
        padding: 2rem 2rem 3rem;
    }

    /* Header */
    h1 {
        color: #163A5F !important;
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.8px;
        margin-bottom: 0.35rem !important;
    }

    h2, h3 {
        color: #163A5F !important;
        font-weight: 600 !important;
        letter-spacing: -0.3px;
    }

    [data-testid="stCaptionContainer"] {
        color: #64788B !important;
        font-size: 0.95rem;
    }

    /* Reduce excess vertical space */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.8rem;
    }

    /* Header divider */
    hr {
        display: block !important;
        visibility: visible !important;
        height: 1px !important;
        border: none !important;
        background-color: #DCE7F3 !important;
        margin: 24px 0 28px 0 !important;
        opacity: 1 !important;
    }


    /* Medication dropdown */
    div[data-testid="stSelectbox"] label {
    color: #34516D !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #F0F6FF !important;
    border: 1px solid #C9DDF5 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
    color: #173B63 !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {
    fill: #3478F6 !important;
    color: #3478F6 !important;
    }


    /* Compact metric cards */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E1EAF3;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(22, 58, 95, 0.035);
    }

    [data-testid="stMetricLabel"] {
        color: #627D98 !important;
        font-size: 0.88rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #163A5F !important;
        font-size: 1.8rem !important;
        font-weight: 650 !important;
    }

    /* Chart containers */
    [data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid #E5ECF3;
        border-radius: 12px;
        padding: 6px;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid #E1EAF3;
        border-radius: 10px;
    }

    /* Buttons and links */
    .stButton button {
        background: #2563EB;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
    }

    .stButton button:hover {
        background: #1D4ED8;
        color: #FFFFFF;
        border: none;
    }

    /* Hide the decorative top header background */
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.9);
    }
    .dashboard-header {
        padding: 8px 0 18px;
    }

    .dashboard-header .eyebrow {
        color: #3478F6;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.8px;
        margin-bottom: 12px;
    }

    .dashboard-header h1 {
        color: #173B63 !important;
        font-size: 36px !important;
        line-height: 1.2 !important;
        letter-spacing: -1.1px;
        margin: 0 0 10px 0 !important;
    }

    .dashboard-header p {
        color: #6B7F93;
        font-size: 16px;
        margin: 0;
        line-height: 1.6;
    }
</style>

""", unsafe_allow_html=True)



# Load project data
DATA_DIR = Path(__file__).parent


@st.cache_data
def load_data():
    history = pd.read_csv(DATA_DIR / "pharmacy_demand_1yr.csv")
    forecast = pd.read_csv(
        DATA_DIR / "future_30_day_demand_forecast.csv",
        skipinitialspace=True
    )
    medications = pd.read_csv(
        DATA_DIR / "medications_metadata.csv",
        skipinitialspace=True
    )

    # Clean column names
    history.columns = history.columns.str.strip()
    forecast.columns = forecast.columns.str.strip()
    medications.columns = medications.columns.str.strip()

    # Convert dates
    history["date"] = pd.to_datetime(history["date"])
    forecast["date"] = pd.to_datetime(forecast["date"])

    # Ensure medication IDs match across all files
    history["med_id"] = pd.to_numeric(history["med_id"]).astype(int)
    forecast["med_id"] = pd.to_numeric(forecast["med_id"]).astype(int)
    medications["med_id"] = pd.to_numeric(
        medications["med_id"]
    ).astype(int)

    return history, forecast, medications

history, forecast, medications = load_data()

# Header

st.markdown("""

<div class="dashboard-header">
    <div class="eyebrow">PHARMACY INVENTORY · ANALYTICS</div>
    <h1>Pharmacy Demand Analytics</h1>
    <p>Understand medication demand and explore upcoming forecasts.</p>
</div>
""", unsafe_allow_html=True)

st.divider()





# Medication selector
medications = medications.sort_values("med_name")

medication_names = medications["med_name"].tolist()
selected_medication = st.selectbox(
    "Select a medication",
    medication_names
)

medication = medications.loc[
    medications["med_name"] == selected_medication
].iloc[0]
med_id = medication["med_id"]

# Filter historical demand
med_history = history[history["med_id"] == med_id].copy()
med_history = med_history.sort_values("date")

# Summary metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Drug Class", medication["drug_class"])

with col2:
    st.metric(
        "Average Daily Demand",
        f"{med_history['demand'].mean():.1f}"
    )

with col3:
    st.metric(
        "Total Historical Demand",
        f"{med_history['demand'].sum():,.0f}"
    )

# Historical chart
st.subheader("Historical Daily Demand")

history_chart = px.line(
    med_history,
    x="date",
    y="demand",
    labels={
        "date": "Date",
        "demand": "Units Requested"
    },
    template="plotly_white"
)

history_chart.update_layout(
    title=None,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(showgrid=False, title=None),
    yaxis=dict(
        showgrid=True,
        gridcolor="#E8EEF5",
        title=None
    )
)

history_chart.update_traces(
    line=dict(color="#3478F6", width=1.8)
)

st.plotly_chart(
    history_chart,
    use_container_width=True,
    config={"displayModeBar": False}
)

# Forecast chart
st.subheader("30-Day Forecast")

med_forecast = forecast[
    forecast["med_id"] == med_id
].copy()

med_forecast = med_forecast.sort_values("date")

if med_forecast.empty:
    st.warning(
        "No forecast was found for this medication. "
        "Check that its ID exists in the forecast CSV."
    )
elif "predicted_demand" not in med_forecast.columns:
    st.error(
        "The forecast CSV does not contain a predicted_demand column."
    )
else:
    forecast_chart = px.line(
        med_forecast,
        x="date",
        y="predicted_demand",
        markers=True,
        labels={
        "date": "Date",
        "predicted_demand": "Predicted units"
        },
        template="plotly_white"
    )

    forecast_chart.update_traces(
        line=dict(color="#3478F6", width=2.5),
        marker=dict(size=5, color="#3478F6")
    )

    forecast_chart.update_layout(
        title=None,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#52677D", size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E8EEF5",
            title=None
        ),
        hovermode="x unified"
    )

    st.plotly_chart(
        forecast_chart,
        use_container_width=True,
        config={"displayModeBar": False}
    )
    


    st.dataframe(
        med_forecast[["date", "predicted_demand"]].rename(
            columns={
                "date": "Date",
                "predicted_demand": "Predicted Daily Demand"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    st.metric(
        "Expected Demand Over Next 30 Days",
        f"{med_forecast['predicted_demand'].sum():,.0f} units"
    )
