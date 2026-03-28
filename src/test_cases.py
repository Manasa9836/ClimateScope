# ================= CLIMATESCOPE TEST CASES =================

import pandas as pd

# ---------------- SAMPLE DATA ----------------
data = {
    "country": ["India", "India", "USA", "USA"],
    "temperature_celsius": [30, 35, 25, 28],
    "humidity": [60, 70, 50, 55],
    "wind_kph": [10, 12, 8, 9],
    "air_quality_PM2.5": [80, 90, 60, 65]
}

df = pd.DataFrame(data)


# ---------------- RISK FUNCTION ----------------
def calc_risk(temp, hum, pm):
    return (temp * 0.4) + (hum * 0.2) + (pm * 0.4)


# ================= TEST CASES =================

# 1️⃣ HIGH RISK
def test_high_risk():
    score = calc_risk(60, 100, 200)
    assert score > 120
    print("✅ TC01: High Risk Passed")


# 2️⃣ MODERATE RISK
def test_moderate_risk():
    score = calc_risk(45, 80, 120)
    assert 80 < score <= 120
    print("✅ TC02: Moderate Risk Passed")


# 3️⃣ LOW RISK
def test_low_risk():
    score = calc_risk(20, 40, 30)
    assert score <= 80
    print("✅ TC03: Low Risk Passed")


# 4️⃣ OVERVIEW FILTER TEST
def test_country_filter():
    countries = df["country"].unique()

    assert len(countries) >= 2   # at least 2 countries needed

    for country in countries:
        cdf = df[df["country"] == country]
        assert not cdf.empty

    print("✅ TC05: Comparison Works for All Countries")

# 5️⃣ COMPARISON TEST
def test_comparison_data():
    c1 = df[df["country"] == "India"]
    c2 = df[df["country"] == "USA"]
    assert len(c1) > 0 and len(c2) > 0
    print("✅ TC05: Comparison Data Available")


# 6️⃣ VOLATILITY TEST
def test_volatility_calc():
    vol = df.groupby("country")["temperature_celsius"].std()
    assert not vol.empty
    print("✅ TC06: Volatility Calculation Working")


# 7️⃣ MAP DATA TEST
def test_map_data():
    grouped = df.groupby("country")["temperature_celsius"].mean()
    assert len(grouped) > 0
    print("✅ TC07: Map Data Prepared")


# 8️⃣ PROFILE DATA TEST
def test_profile_data():
    india = df[df["country"] == "India"]
    avg_temp = india["temperature_celsius"].mean()
    assert avg_temp > 0
    print("✅ TC08: Profile Metrics Working")


# 9️⃣ ZERO INPUT TEST
def test_zero_values():
    score = calc_risk(0, 0, 0)
    assert score == 0
    print("✅ TC09: Zero Input Handled")


# 🔟 EMPTY DATA TEST
def test_empty_dataframe():
    empty_df = df[df["country"] == "XYZ"]
    assert empty_df.empty
    print("✅ TC10: Empty Data Handling Working")


# ================= RUN ALL =================
if __name__ == "__main__":

    print("🚀 Running ClimateScope Full Test Suite...\n")

    test_high_risk()
    test_moderate_risk()
    test_low_risk()
    test_country_filter()
    test_comparison_data()
    test_volatility_calc()
    test_map_data()
    test_profile_data()
    test_zero_values()
    test_empty_dataframe()

    print("\n🎯 ALL TEST CASES PASSED SUCCESSFULLY!")