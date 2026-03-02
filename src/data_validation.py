def validate_data(df):
    print("\n🔎 Starting Data Validation...\n")

    # Missing values check
    missing = df.isnull().sum().sum()
    print(f"Total Missing Values: {missing}")

    # Duplicate check
    duplicates = df.duplicated().sum()
    print(f"Duplicate Rows: {duplicates}")

    # Humidity validation
    if "humidity" in df.columns:
        invalid_humidity = df[~df["humidity"].between(0, 100)]
        print(f"Invalid Humidity Records: {len(invalid_humidity)}")

    # Temperature validation
    if "temperature_celsius" in df.columns:
        invalid_temp = df[~df["temperature_celsius"].between(-50, 60)]
        print(f"Invalid Temperature Records: {len(invalid_temp)}")

    # Wind validation
    if "wind_kph" in df.columns:
        invalid_wind = df[df["wind_kph"] < 0]
        print(f"Invalid Wind Speed Records: {len(invalid_wind)}")

    print("\n✅ Data Validation Completed Successfully!")