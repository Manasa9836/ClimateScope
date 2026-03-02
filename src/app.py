import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import pycountry
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="ClimateScope", layout="wide")
st.title("🌍 ClimateScope Dashboard - Final Version")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/weather_clean.csv")
    df["last_updated"] = pd.to_datetime(df["last_updated"])
    return df

df = load_data().copy()

# -------------------------------------------------
# CREATE TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Country Analysis",
    "Volatility",
    "Global Map",
    "Prediction"
])

# =================================================
# TAB 1 — OVERVIEW
# =================================================
with tab1:

    st.subheader("📊 Correlation Heatmap")

    corr_df = df[[
        "temperature_celsius",
        "humidity",
        "wind_kph",
        "air_quality_PM2.5"
    ]].corr()

    st.plotly_chart(px.imshow(corr_df, text_auto=True))

    # Seasonal Heatmap
    st.subheader("🌦 Seasonal Heatmap")

    def get_season(month):
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Autumn"

    df["season"] = df["last_updated"].dt.month.apply(get_season)

    seasonal = df.groupby("season")[
        ["temperature_celsius", "humidity", "wind_kph"]
    ].mean()

    st.plotly_chart(px.imshow(seasonal, text_auto=True))

    # Latitudinal Gradient
    if "latitude" in df.columns:
        st.subheader("🌍 Latitudinal Temperature Gradient")

        lat_grad = (
            df.groupby("latitude")["temperature_celsius"]
            .mean()
            .reset_index()
        )

        st.plotly_chart(
            px.scatter(
                lat_grad,
                x="latitude",
                y="temperature_celsius",
                title="Latitude vs Average Temperature"
            )
        )

# =================================================
# TAB 2 — COUNTRY ANALYSIS
# =================================================
# =================================================
# TAB 2 — COUNTRY COMPARISON
# =================================================
with tab2:

    st.subheader("📊 Compare Two Countries - Temperature Trends")

    col1, col2 = st.columns(2)

    countries = sorted(df["country"].unique())

    country1 = col1.selectbox("Select First Country", countries, key="country1")
    country2 = col2.selectbox("Select Second Country", countries, key="country2")

    df1 = df[df["country"] == country1].copy()
    df2 = df[df["country"] == country2].copy()

    df1 = df1.sort_values("last_updated")
    df2 = df2.sort_values("last_updated")

    # Rolling averages
    df1["Rolling_7"] = df1["temperature_celsius"].rolling(7, min_periods=1).mean()
    df2["Rolling_7"] = df2["temperature_celsius"].rolling(7, min_periods=1).mean()

    # Combine for plotting
    compare_df = pd.concat([
        df1[["last_updated", "temperature_celsius"]].assign(Country=country1),
        df2[["last_updated", "temperature_celsius"]].assign(Country=country2)
    ])

    st.plotly_chart(
        px.line(
            compare_df,
            x="last_updated",
            y="temperature_celsius",
            color="Country",
            title="Temperature Comparison"
        )
    )

    # Rolling Comparison
    rolling_compare = pd.concat([
        df1[["last_updated", "Rolling_7"]].assign(Country=country1),
        df2[["last_updated", "Rolling_7"]].assign(Country=country2)
    ])

    st.subheader("📈 7-Day Rolling Average Comparison")

    st.plotly_chart(
        px.line(
            rolling_compare,
            x="last_updated",
            y="Rolling_7",
            color="Country"
        )
    )

# =================================================
# TAB 3 — VOLATILITY + HEXBIN
# =================================================
with tab3:

    st.subheader("🔥 Top 10 Temperature Volatility")

    volatility = (
        df.groupby("country")["temperature_celsius"]
        .agg(["mean", "std"])
    )

    volatility["volatility"] = volatility["std"] / volatility["mean"]

    top10 = (
        volatility.sort_values("volatility", ascending=False)
        .head(10)
        .reset_index()
    )

    st.plotly_chart(
        px.bar(
            top10,
            x="country",
            y="volatility",
            title="Top 10 Countries by Temperature Volatility"
        )
    )

    # Hexbin Plot
    st.subheader("🔷 Hexbin: Humidity vs Temperature")

    fig, ax = plt.subplots()
    hb = ax.hexbin(
        df["humidity"],
        df["temperature_celsius"],
        gridsize=30
    )
    fig.colorbar(hb)
    ax.set_xlabel("Humidity")
    ax.set_ylabel("Temperature")

    st.pyplot(fig)

# =================================================
# TAB 4 — GLOBAL MAP
# =================================================
with tab4:

    st.subheader("🌍 Global Average Temperature Map")

    def get_iso3(country_name):
        try:
            return pycountry.countries.lookup(country_name).alpha_3
        except:
            return None

    map_df = df.groupby("country")["temperature_celsius"].mean().reset_index()
    map_df["iso_alpha"] = map_df["country"].apply(get_iso3)
    map_df = map_df.dropna(subset=["iso_alpha"])

    st.plotly_chart(
        px.choropleth(
            map_df,
            locations="iso_alpha",
            color="temperature_celsius",
            hover_name="country",
            color_continuous_scale="Reds"
        )
    )

# =================================================
# TAB 5 — TWO COUNTRY PREDICTION
# =================================================
with tab5:

    st.subheader("🤖 Country vs Country Temperature Prediction")

    col1, col2 = st.columns(2)

    countries = sorted(df["country"].unique())

    country1 = col1.selectbox("Select First Country", countries)
    country2 = col2.selectbox("Select Second Country", countries)

    humidity_input = st.slider(
        "Select Humidity Level",
        float(df["humidity"].min()),
        float(df["humidity"].max()),
        float(df["humidity"].mean())
    )

    df1 = df[df["country"] == country1]
    df2 = df[df["country"] == country2]

    model1 = LinearRegression()
    model1.fit(df1[["humidity"]], df1["temperature_celsius"])

    model2 = LinearRegression()
    model2.fit(df2[["humidity"]], df2["temperature_celsius"])

    input_df = pd.DataFrame([[humidity_input]], columns=["humidity"])

    prediction1 = model1.predict(input_df)[0]
    prediction2 = model2.predict(input_df)[0]

    col1.metric(f"{country1} Prediction", f"{round(prediction1, 2)} °C")
    col2.metric(f"{country2} Prediction", f"{round(prediction2, 2)} °C")

    compare_df = pd.DataFrame({
        "Country": [country1, country2],
        "Predicted Temperature": [prediction1, prediction2]
    })

    st.plotly_chart(
        px.bar(
            compare_df,
            x="Country",
            y="Predicted Temperature",
            title="Prediction Comparison"
        )
    )