import pandas as pd

def create_features(df):
    print("\n⚙️ Starting Feature Engineering...\n")

    # Extract Year and Month
    df["year"] = df["last_updated"].dt.year
    df["month"] = df["last_updated"].dt.month

    # Monthly Average Temperature
    monthly_avg = (
        df.groupby(["country", "year", "month"])["temperature_celsius"]
        .mean()
        .reset_index()
    )

    monthly_avg.to_csv("data/processed/monthly_avg_temperature.csv", index=False)
    print("✅ Monthly average temperature saved.")

    # Yearly Average Temperature
    yearly_avg = (
        df.groupby(["country", "year"])["temperature_celsius"]
        .mean()
        .reset_index()
    )

    yearly_avg.to_csv("data/processed/yearly_avg_temperature.csv", index=False)
    print("✅ Yearly average temperature saved.")

    print("\n✅ Feature Engineering Completed Successfully!")