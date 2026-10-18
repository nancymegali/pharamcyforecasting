
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
        background: #F3F6F5;
        color: #203A39;
    }

    .block-container {
        max-width: 1160px;
        padding: 2rem 2rem 3rem;
    }

    /* Header */
    h1 {
        color: #203A39 !important;
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.8px;
        margin-bottom: 0.35rem !important;
    }

    h2, h3 {
        color: #203A39 !important;
        font-weight: 600 !important;
        letter-spacing: -0.3px;
    }

    [data-testid="stCaptionContainer"] {
        color: #647773 !important;
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
        background-color: #DDE7E2 !important;
        margin: 24px 0 28px 0 !important;
        opacity: 1 !important;
    }


    /* Medication dropdown: outline the whole select box */
    div[data-testid="stSelectbox"] [data-baseweb="select"] {
        border: 2px solid #536C7C !important;
        border-radius: 10px !important;
        background-color: #FFFFFF !important;
        overflow: hidden;
    }

    /* Remove the light-blue fill from the inner element */
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Keep the same outline when focused or open */
    div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within {
        border: 2px solid #536C7C !important;
        box-shadow: none !important;
    }

    /* Dropdown text */
    div[data-testid="stSelectbox"] [data-baseweb="select"] span {
        color: #203A39 !important;
    }


    /* Compact metric cards */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #DDE7E2;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 3px 12px rgba(32, 58, 57, 0.045);
    }

    [data-testid="stMetricLabel"] {
        color: #647773 !important;
        font-size: 0.88rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #203A39 !important;
        font-size: 1.8rem !important;
        font-weight: 650 !important;
    }

    /* Chart containers */
    [data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid #DFE8E3;
        border-radius: 12px;
        padding: 6px;
    }
    
    /* Forecast table styling */
    [data-testid="stDataFrame"] {
        border: 1px solid #B8C9C1;
        border-radius: 10px;
    }

    [data-testid="stDataFrame"] *:focus {
        outline-color: #3478F6 !important;
    }

    [data-testid="stDataFrame"] [aria-selected="true"] {
        outline-color: #3478F6 !important;
        border-color: #3478F6 !important;
    }


    /* Buttons and links */
    .stButton button {
        background: #557F78;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
    }

    .stButton button:hover {
        background: #456B64;
        color: #FFFFFF;
        border: none;
    }

    /* Hide the decorative top header background */
    [data-testid="stHeader"] {
        background: rgba(243, 246, 245, 0.94);
    }
    .dashboard-header {
        padding: 8px 0 18px;
    }

    .dashboard-header .eyebrow {
        color: #7798C4;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1.8px;
        margin-bottom: 12px;
    }

    .dashboard-header h1 {
        color: #203A39 !important;
        font-size: 36px !important;
        line-height: 1.2 !important;
        letter-spacing: -1.1px;
        margin: 0 0 10px 0 !important;
    }

    .dashboard-header p {
        color: #647773;
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
    template="plotly_white",
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(color="#647773", size=12),
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(
        showgrid=False,
        title=None,
        color="#526963",
        tickfont=dict(color="#526963", size=12),
        linecolor="#C5D6CF",
        linewidth=1,
        showline=True,
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#E4ECE8",
        title=None,
        color="#526963",
        tickfont=dict(color="#526963", size=12),
        linecolor="#C5D6CF",
        linewidth=1,
        zerolinecolor="#D8E5DF",
    )
)

history_chart.update_traces(
    name="Historical Demand",
    line=dict(color="#7798C4", width=3.5),
    hovertemplate=(
        "Date: %{x|%b %d, %Y}<br>"
        "Historical Demand: %{y:.1f} units"
        "<extra></extra>"
    )
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
    # Most recent 30 days of historical demand
    recent_history = med_history.tail(30).copy()

    # Start the chart with historical demand in sage green
    forecast_chart = px.line(
        recent_history,
        x="date",
        y="demand",
        labels={
            "date": "Date",
            "demand": "Units",
        },
        template="plotly_white",
    )

    # Historical series: bold sage green
    forecast_chart.update_traces(
        name="Historical",
        line=dict(color="#7798C4", width=3.5),
        mode="lines+markers",
        marker=dict(size=6, color="#7798C4"),
        showlegend=True,
        hovertemplate=(
            "Date: %{x|%b %d, %Y}<br>"
            "Historical: %{y:.1f} units"
            "<extra></extra>"
        ),
    )

    # Forecast series: bold dusty blue with markers
    forecast_chart.add_scatter(
        x=med_forecast["date"],
        y=med_forecast["predicted_demand"],
        mode="lines+markers",
        name="Predicted",
        showlegend=True,
        line=dict(color="#719A8C", width=3.5),
        marker=dict(size=6, color="#719A8C"),
        hovertemplate=(
            "Date: %{x|%b %d, %Y}<br>"
            "Predicted: %{y:.1f} units"
            "<extra></extra>"
        ),
    )

    # Chart styling and visible legend
    forecast_chart.update_layout(
        title=None,
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#647773", size=12),
        margin=dict(l=10, r=10, t=10, b=55),
        xaxis=dict(
            showgrid=False,
            title=None,
            color="#526963",
            tickfont=dict(color="#526963", size=12),
            linecolor="#C5D6CF",
            linewidth=1,
            showline=True,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E4ECE8",
            title=dict(
                text="Units",
                font=dict(color="#526963", size=14)
            ),
            tickfont=dict(color="#526963", size=12),
            linecolor="#C5D6CF",
            linewidth=1,
            zerolinecolor="#D8E5DF",
        ),
        hovermode="x unified",
        legend=dict(
            title=None,
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="left",
            x=0,
            font=dict(color="#647773", size=13),
            bgcolor="rgba(255,255,255,0)",
        ),
    )

    st.plotly_chart(
        forecast_chart,
        use_container_width=True,
        config={"displayModeBar": False},
    )


    


    
    
    # Forecast table
    forecast_table = med_forecast[["date", "predicted_demand"]].rename(
        columns={
            "date": "Date",
            "predicted_demand": "Predicted Daily Demand"
        }
    ).copy()

    forecast_table["Date"] = forecast_table["Date"].dt.strftime("%b %d, %Y")

    st.dataframe(
        forecast_table.style
        .format({"Predicted Daily Demand": "{:.1f}"})
        .set_properties(**{
            "background-color": "#FFFFFF",
            "color": "#203A39",
            "font-weight": "600",
            "border": "1px solid #B8C9C1"
        })
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#FFFFFF"),
                    ("color", "#203A39"),
                    ("font-weight", "bold"),
                    ("border", "1px solid #A9BDB3"),
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("border", "1px solid #B8C9C1"),
                ]
            }
        ]),
        use_container_width=True,
        hide_index=True,
        height=420
    )

    st.metric(
        "Expected Demand Over Next 30 Days",
        f"{med_forecast['predicted_demand'].sum():,.0f} units"
    )
