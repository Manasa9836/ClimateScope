import pandas as pd

def clean_data():
    print("📥 Loading Raw Dataset...")
    df = pd.read_csv("data/raw/global_weather.csv")

    print(f"Original Shape: {df.shape}")

    # Remove duplicates
    df = df.drop_duplicates()
    print(f"After Removing Duplicates: {df.shape}")

    # Handle missing values
    missing_before = df.isnull().sum().sum()
    print(f"Total Missing Values Before Cleaning: {missing_before}")

    critical_columns = ["country", "temperature_celsius", "last_updated"]
    df = df.dropna(subset=critical_columns)

    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    missing_after = df.isnull().sum().sum()
    print(f"Total Missing Values After Cleaning: {missing_after}")

    # Convert date column
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
    df = df.dropna(subset=["last_updated"])

    # Standardize country names
    df["country"] = df["country"].str.strip()

    # Basic range filtering
    if "temperature_celsius" in df.columns:
        df = df[df["temperature_celsius"].between(-50, 60)]

    if "humidity" in df.columns:
        df = df[df["humidity"].between(0, 100)]

    if "wind_kph" in df.columns:
        df = df[df["wind_kph"] >= 0]

    print(f"Final Cleaned Shape: {df.shape}")

    df.to_csv("data/processed/weather_clean.csv", index=False)
    print("✅ Cleaned dataset saved to data/processed/weather_clean.csv")

    return df