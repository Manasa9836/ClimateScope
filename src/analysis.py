import pandas as pd

def perform_analysis(df):

    print("\n📊 Advanced Climate Analysis\n")

    # -------------------------------------------------
    # 1️⃣ Latitudinal Temperature Gradient
    # -------------------------------------------------
    if "latitude" in df.columns:
        lat_gradient = (
            df.groupby("latitude")["temperature_celsius"]
            .mean()
            .reset_index()
        )
        lat_gradient.to_csv("data/processed/latitudinal_gradient.csv", index=False)
        print("✅ Latitudinal Gradient Calculated")

    # -------------------------------------------------
    # 2️⃣ Temperature Volatility (Std / Mean)
    # -------------------------------------------------
    volatility = (
        df.groupby("country")["temperature_celsius"]
        .agg(["mean", "std"])
    )

    volatility["volatility"] = volatility["std"] / volatility["mean"]
    volatility = volatility.sort_values("volatility", ascending=False)

    volatility.to_csv("data/processed/temperature_volatility.csv")

    print("\nTop 10 Countries by Temperature Volatility:")
    print(volatility.head(10))

    # -------------------------------------------------
    # 3️⃣ Seasonal Categorization
    # -------------------------------------------------
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

    season_avg = (
        df.groupby("season")[
            ["temperature_celsius", "humidity", "wind_kph"]
        ].mean()
    )

    season_avg.to_csv("data/processed/seasonal_heatmap_data.csv")

    print("✅ Seasonal Analysis Completed")

    print("\n🎉 Advanced Analysis Completed Successfully!\n")

    return df