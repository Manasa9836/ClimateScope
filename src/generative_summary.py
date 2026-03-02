def generate_summary(df):
    print("\n📊 Generating Automatic Climate Insights...\n")

    hottest = df.groupby("country")["temperature_celsius"].mean().idxmax()
    hottest_temp = df.groupby("country")["temperature_celsius"].mean().max()

    coldest = df.groupby("country")["temperature_celsius"].mean().idxmin()
    coldest_temp = df.groupby("country")["temperature_celsius"].mean().min()

    print(f"🔥 Hottest Country: {hottest} ({round(hottest_temp,2)} °C)")
    print(f"❄️ Coldest Country: {coldest} ({round(coldest_temp,2)} °C)")

    if "air_quality_PM2.5" in df.columns:
        worst_air = df.groupby("country")["air_quality_PM2.5"].mean().idxmax()
        worst_air_value = df.groupby("country")["air_quality_PM2.5"].mean().max()
        print(f"🌫 Worst Air Quality: {worst_air} ({round(worst_air_value,2)})")

    if "humidity" in df.columns:
        high_humidity = df.groupby("country")["humidity"].mean().idxmax()
        print(f"💧 Highest Avg Humidity: {high_humidity}")

    print("\n✅ Summary Generation Completed!\n")