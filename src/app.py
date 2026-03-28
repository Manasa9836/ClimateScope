import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry
import hashlib
import os

st.set_page_config(page_title="ClimateScope", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.metric-card{
background: linear-gradient(135deg,#4facfe,#00f2fe);
padding:20px;
border-radius:10px;
color:white;
text-align:center;
font-size:20px;
font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ================= USER SYSTEM =================
USER_FILE="users.csv"

if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["username","password"]).to_csv(USER_FILE,index=False)

def load_users():
    return pd.read_csv(USER_FILE)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(username,password):
    users=load_users()
    new=pd.DataFrame([[username,hash_password(password)]],columns=["username","password"])
    users=pd.concat([users,new],ignore_index=True)
    users.to_csv(USER_FILE,index=False)

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

# ================= LOGIN =================
if not st.session_state.logged_in:

    st.title("🌍 ClimateScope Login")
    option=st.selectbox("Select",["Login","Create Account"])

    if option=="Login":
        user=st.text_input("Username")
        pwd=st.text_input("Password",type="password")

        if st.button("Login"):
            users=load_users()
            if ((users["username"]==user)&(users["password"]==hash_password(pwd))).any():
                st.session_state.logged_in=True
                st.session_state.username=user
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid Login")

    else:
        user=st.text_input("New Username")
        pwd=st.text_input("New Password",type="password")

        if st.button("Register"):
            users=load_users()
            if user in users["username"].values:
                st.warning("Username exists")
            else:
                save_user(user,pwd)
                st.success("Account Created")

    st.stop()

# ================= HEADER =================
col1,col2=st.columns([9,1])
with col1:
    st.title("🌍 ClimateScope Dashboard")
with col2:
    if st.button("Logout"):
        st.session_state.logged_in=False
        st.rerun()

st.write(f"Welcome **{st.session_state.username}**")

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    df=pd.read_csv("data/raw/global_weather.csv")
    df["last_updated"]=pd.to_datetime(df["last_updated"],errors="coerce")
    df=df.dropna(subset=["last_updated"])
    return df

df=load_data().sort_values("last_updated")

# ================= FILTER =================
st.sidebar.header("Filters")

metric=st.sidebar.selectbox("Metric",
["temperature_celsius","humidity","wind_kph","air_quality_PM2.5"])

date_range = st.sidebar.date_input(
    "Date Range",
    [df["last_updated"].min().date(), df["last_updated"].max().date()]
)

# ✅ FIX: Handle single date safely
if len(date_range) == 1:
    st.warning("⚠ Please select BOTH start and end date")
    start = end = date_range[0]
elif len(date_range) == 2:
    start, end = date_range
else:
    st.warning("⚠ Please select valid date range")
    start = df["last_updated"].min().date()
    end = df["last_updated"].max().date()

filtered_df=df[
(df["last_updated"]>=pd.to_datetime(start))&
(df["last_updated"]<=pd.to_datetime(end))
].copy()
# ================= ISO =================
def get_iso(country):
    try:
        return pycountry.countries.lookup(country).alpha_3
    except:
        return None

filtered_df["iso_alpha"]=filtered_df["country"].apply(get_iso)
filtered_df=filtered_df.dropna(subset=["iso_alpha"])

if filtered_df.empty:
    st.warning("No data available")
    st.stop()

countries=sorted(filtered_df["country"].dropna().unique())

# ================= KPI =================
st.subheader("Global Climate Summary")

c1,c2,c3,c4=st.columns(4)
c1.markdown(f"<div class='metric-card'>Avg Temp<br>{round(filtered_df['temperature_celsius'].mean(),2)} °C</div>",unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card'>Avg Humidity<br>{round(filtered_df['humidity'].mean(),2)}%</div>",unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card'>Avg Wind<br>{round(filtered_df['wind_kph'].mean(),2)} km/h</div>",unsafe_allow_html=True)
c4.markdown(f"<div class='metric-card'>Avg PM2.5<br>{round(filtered_df['air_quality_PM2.5'].mean(),2)}</div>",unsafe_allow_html=True)

# ================= TABS =================
tab1,tab2,tab3,tab4,tab5,tab6=st.tabs([
"Overview","Comparison","Volatility","Map","Profile","Risk Analysis"
])

# ================= OVERVIEW =================
with tab1:

    st.subheader("📊 Overview")

    # ===== INPUT =====
    selected = st.multiselect(
        "Select Countries (Max 3)",
        countries,
        default=countries[:3],
        max_selections=3,
        key="overview_country"
    )

    # ===== VALIDATION =====
    if not selected:
        st.warning("⚠ Please select at least one country")
        st.stop()

    # ===== PROCESS =====
    trend_df = filtered_df[filtered_df["country"].isin(selected)]

    # ===== OUTPUT =====
    st.subheader("📈 Climate Trend")

    st.plotly_chart(
        px.line(
            trend_df,
            x="last_updated",
            y=metric,
            color="country",
            markers=True
        ),
        use_container_width=True
    )

    # ===== LATITUDE =====
    if "latitude" in filtered_df.columns:
        st.subheader("🌍 Latitude vs Temperature")

        st.plotly_chart(
            px.scatter(
                trend_df,
                x="latitude",
                y="temperature_celsius",
                color="country",
                trendline="ols"
            ),
            use_container_width=True
        )

    # ===== CORRELATION =====
    st.subheader("📊 Correlation Matrix")

    corr=filtered_df[["temperature_celsius","humidity","wind_kph","air_quality_PM2.5"]].corr()

    st.plotly_chart(
        px.imshow(corr,text_auto=True),
        use_container_width=True
    )

    # ===== SEASONAL HEATMAP =====
    st.subheader("🌦 Seasonal Heatmap")

    heat_country = st.selectbox("Select Country", countries, key="heatmap_country")

    heat_df = filtered_df[filtered_df["country"] == heat_country].copy()

    if not heat_df.empty:

        heat_df["month_name"]=heat_df["last_updated"].dt.strftime("%b")
        heat_df["year"]=heat_df["last_updated"].dt.year

        month_order=["Jan","Feb","Mar","Apr","May","Jun",
                     "Jul","Aug","Sep","Oct","Nov","Dec"]

        heat_df["month_name"]=pd.Categorical(
            heat_df["month_name"],
            categories=month_order,
            ordered=True
        )

        heatmap_data=heat_df.pivot_table(
            values="temperature_celsius",
            index="month_name",
            columns="year",
            aggfunc="mean"
        )

        st.plotly_chart(
            px.imshow(heatmap_data,
                      labels=dict(x="Year",y="Month",color="Temp")),
            use_container_width=True
        )

    # ===== VOLATILITY =====
    st.subheader("📉 Temperature Volatility")

    vol=trend_df.copy()
    vol["rolling_std"]=vol.groupby("country")["temperature_celsius"]\
        .transform(lambda x: x.rolling(7).std())

    st.plotly_chart(
        px.line(vol,x="last_updated",y="rolling_std",color="country"),
        use_container_width=True
    )
# ================= COMPARISON =================
with tab2:

    c1,c2=st.columns(2)
    ctry1=c1.selectbox("Country 1",countries,key="comp1")
    ctry2=c2.selectbox("Country 2",countries,key="comp2")

    df1=filtered_df[filtered_df["country"]==ctry1].copy()
    df2=filtered_df[filtered_df["country"]==ctry2].copy()

    df1["Country"]=ctry1
    df2["Country"]=ctry2

    comp=pd.concat([df1,df2])

    st.plotly_chart(px.line(comp,x="last_updated",y=metric,color="Country"),
                    use_container_width=True)

# ================= VOLATILITY =================
with tab3:

    vol=filtered_df.groupby("country")[metric].agg(["mean","std"])
    vol["volatility"]=vol["std"]/vol["mean"]

    st.plotly_chart(px.bar(vol.reset_index(),x="country",y="volatility"),
                    use_container_width=True)

# ================= MAP =================
with tab4:

    map_df=filtered_df.groupby(["country","iso_alpha"])[metric].mean().reset_index()

    st.plotly_chart(px.choropleth(map_df,locations="iso_alpha",color=metric),
                    use_container_width=True)

# ================= PROFILE =================
with tab5:

    search=st.text_input("Search Country")
    filt=[c for c in countries if search.lower() in c.lower()]
    country=st.selectbox("Select Country",filt,key="profile_country")

    cdf=filtered_df[filtered_df["country"]==country]

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Temp",round(cdf["temperature_celsius"].mean(),2))
    c2.metric("Humidity",round(cdf["humidity"].mean(),2))
    c3.metric("Wind",round(cdf["wind_kph"].mean(),2))
    c4.metric("Air",round(cdf["air_quality_PM2.5"].mean(),2))

# ================= RISK ANALYSIS =================
with tab6:

    st.subheader("⚠ Risk Factor Analysis")

    # ===== Select Countries =====
    selected_risk = st.multiselect(
        "Select Countries (Max 3)",
        countries,
        default=countries[:3],
        max_selections=3,
        key="risk_country_select"
    )

    risk_filtered = filtered_df[filtered_df["country"].isin(selected_risk)]

    # ===== Thresholds =====
    col1,col2,col3=st.columns(3)

    with col1:
        heat_thresh=st.slider("Temperature Risk",30,50,35)

    with col2:
        hum_thresh=st.slider("Humidity Risk",50,100,80)

    with col3:
        air_thresh=st.slider("PM2.5 Risk",10,200,100)

    # ===== Risk Calculation =====
    risk_df=risk_filtered.copy()

    def classify(row):
        if row["temperature_celsius"]>=heat_thresh:
            return "Temperature Risk"
        elif row["humidity"]>=hum_thresh:
            return "Humidity Risk"
        elif row["air_quality_PM2.5"]>=air_thresh:
            return "Pollution Risk"
        else:
            return "Safe"

    risk_df["Risk"]=risk_df.apply(classify,axis=1)

    # ===== Latest Risk =====
    latest=risk_df.sort_values("last_updated").groupby("country").tail(1)

    st.subheader("🌍 Selected Country Risk")

    for _,row in latest.iterrows():
        st.write(f"{row['country']} → {row['Risk']}")

    # ===== Risk Distribution =====
    st.subheader("📊 Risk Distribution")

    if not latest.empty:
        rc=latest["Risk"].value_counts().reset_index()
        rc.columns=["Risk","Count"]

        st.plotly_chart(
            px.pie(rc,names="Risk",values="Count"),
            use_container_width=True
        )
    else:
        st.warning("No data available")

    # ===== Risk Score =====
    st.subheader("📈 Risk Score")

    score=risk_df.copy()
    score["score"]=(
        (score["temperature_celsius"]/heat_thresh)+
        (score["humidity"]/hum_thresh)+
        (score["air_quality_PM2.5"]/air_thresh)
    )

    top=score.groupby("country")["score"].mean().sort_values(ascending=False)

    st.plotly_chart(
        px.bar(top.reset_index(),x="country",y="score"),
        use_container_width=True
    )

    # ===== NEW: Trend Comparison =====
    st.subheader("📉 Trend Comparison (Selected Countries)")

    if not risk_filtered.empty:

        trend_metric = st.selectbox(
            "Select Metric for Trend",
            ["temperature_celsius","humidity","wind_kph","air_quality_PM2.5"],
            key="risk_trend_metric"
        )

        st.plotly_chart(
            px.line(
                risk_filtered,
                x="last_updated",
                y=trend_metric,
                color="country",
                markers=True,
                title="Trend Comparison"
            ),
            use_container_width=True
        )

    else:
        st.warning("No data to display trend")
# ================= DOWNLOAD =================
csv=filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download Dataset",csv,"climate_data.csv","text/csv")