import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/global_weather.csv")

# Show first 5 rows
print("First 5 rows:")
print(df.head())

# Show dataset info
print("\nDataset Info:")
print(df.info())

# Check missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Remove duplicates
df = df.drop_duplicates()

# Fill missing values
df = df.ffill()

# Convert date column properly
df["last_updated"] = pd.to_datetime(df["last_updated"])

# Create average temperature per country
country_avg = df.groupby("country")["temperature_celsius"].mean().reset_index()
country_avg.to_csv("data/processed/country_avg_temperature.csv", index=False)

# Save cleaned dataset
df.to_csv("data/processed/weather_clean.csv", index=False)

print("\nData cleaning completed successfully!")
