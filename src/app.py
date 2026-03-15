import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry
import hashlib
import os

st.set_page_config(page_title="ClimateScope", layout="wide")

# ================= KPI STYLE =================

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

# ================= USER DATABASE =================

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

# ================= LOGIN PAGE =================

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

st.write("Welcome **"+st.session_state.username+"**")

# ================= LOAD DATA =================

@st.cache_data
def load_data():

    df=pd.read_csv("data/raw/global_weather.csv")

    df["last_updated"]=pd.to_datetime(df["last_updated"],errors="coerce")

    df=df.dropna(subset=["last_updated"])

    return df

df=load_data()

df=df.sort_values("last_updated")

# ================= SIDEBAR =================

st.sidebar.header("Filters")

metric=st.sidebar.selectbox("Metric",
["temperature_celsius","humidity","wind_kph","air_quality_PM2.5"])

min_date=df["last_updated"].min().date()
max_date=df["last_updated"].max().date()

start,end=st.sidebar.date_input("Date Range",[min_date,max_date])

filtered_df=df[
(df["last_updated"]>=pd.to_datetime(start))&
(df["last_updated"]<=pd.to_datetime(end))
]

# ================= ISO COUNTRY CODE =================

def get_iso(country):
    try:
        return pycountry.countries.lookup(country).alpha_3
    except:
        return None

filtered_df=filtered_df.copy()
filtered_df["iso_alpha"]=filtered_df["country"].apply(get_iso)
filtered_df=filtered_df.dropna(subset=["iso_alpha"])

# ================= KPI =================

st.subheader("Global Climate Summary")

c1,c2,c3,c4=st.columns(4)

c1.markdown(f"<div class='metric-card'>Avg Temp<br>{round(filtered_df['temperature_celsius'].mean(),2)} °C</div>",unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card'>Avg Humidity<br>{round(filtered_df['humidity'].mean(),2)}%</div>",unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card'>Avg Wind<br>{round(filtered_df['wind_kph'].mean(),2)} km/h</div>",unsafe_allow_html=True)
c4.markdown(f"<div class='metric-card'>Avg PM2.5<br>{round(filtered_df['air_quality_PM2.5'].mean(),2)}</div>",unsafe_allow_html=True)

# ================= TABS =================

tab1,tab2,tab3,tab4,tab5=st.tabs([
"Overview",
"Country Comparison",
"Volatility",
"Global Map",
"Country Profile"
])

# ================= OVERVIEW =================

with tab1:

    st.subheader("Climate Risk Indicator")

    avg_temp=filtered_df["temperature_celsius"].mean()

    if avg_temp>35:
        st.error("🔴 High Climate Risk")
    elif avg_temp>28:
        st.warning("🟡 Moderate Climate Risk")
    else:
        st.success("🟢 Low Climate Risk")

    # ===== Climate Trend =====

    st.subheader("Climate Trend")

    countries=sorted(filtered_df["country"].unique())

    selected=st.multiselect(
        "Select Countries (Max 3)",
        countries,
        default=countries[:3],
        max_selections=3
    )

    trend_df=filtered_df[filtered_df["country"].isin(selected)]

    for country in selected:

        cdata=trend_df[trend_df["country"]==country]

        fig=px.line(
            cdata,
            x="last_updated",
            y=metric,
            title=country,
            markers=True,
            line_shape="spline"
        )

        st.plotly_chart(fig,use_container_width=True)

    # ===== Monthly Trend =====

    st.subheader("Monthly Climate Trend")

    trend_df["month"]=trend_df["last_updated"].dt.strftime("%b")

    monthly=trend_df.groupby(["month","country"])[metric].mean().reset_index()

    fig_month=px.line(monthly,x="month",y=metric,color="country",markers=True)

    st.plotly_chart(fig_month,use_container_width=True)

    # ===== Temperature vs Humidity =====

    st.subheader("Temperature vs Humidity")

    st.plotly_chart(px.scatter(trend_df,x="temperature_celsius",y="humidity",color="country"),use_container_width=True)

    # ===== Heatmap =====

    st.subheader("Seasonal Heatmap")

    heat=trend_df.pivot_table(values="temperature_celsius",index=trend_df["last_updated"].dt.month,columns="country",aggfunc="mean")

    st.plotly_chart(px.imshow(heat),use_container_width=True)

    # ===== Hottest =====

    st.subheader("🔥 Top 5 Hottest Countries")

    hot=filtered_df.groupby("country")["temperature_celsius"].mean().sort_values(ascending=False).head(5)

    st.plotly_chart(px.bar(hot.reset_index(),x="country",y="temperature_celsius"),use_container_width=True)

    # ===== Coldest =====

    st.subheader("❄ Top 5 Coldest Countries")

    cold=filtered_df.groupby("country")["temperature_celsius"].mean().sort_values().head(5)

    st.plotly_chart(px.bar(cold.reset_index(),x="country",y="temperature_celsius"),use_container_width=True)

    # ===== Pollution =====

    st.subheader("Top 10 Polluted Countries")

    pol=filtered_df.groupby("country")["air_quality_PM2.5"].mean().sort_values(ascending=False).head(10)

    st.plotly_chart(px.bar(pol.reset_index(),x="country",y="air_quality_PM2.5"),use_container_width=True)

    # ===== Distribution =====

    st.subheader("Temperature Distribution")

    st.plotly_chart(px.histogram(filtered_df,x="temperature_celsius",nbins=30),use_container_width=True)

    # ===== Forecast =====

    st.subheader("Temperature Forecast")

    fc=filtered_df.groupby("last_updated")["temperature_celsius"].mean().reset_index()

    fc["rolling"]=fc["temperature_celsius"].rolling(5).mean()

    st.plotly_chart(px.line(fc,x="last_updated",y="rolling"),use_container_width=True)

# ================= COUNTRY COMPARISON =================

with tab2:

    countries=sorted(filtered_df["country"].unique())

    c1,c2=st.columns(2)

    country1=c1.selectbox("Country 1",countries)
    country2=c2.selectbox("Country 2",countries)

    df1=filtered_df[filtered_df["country"]==country1]
    df2=filtered_df[filtered_df["country"]==country2]

    comp=pd.concat([df1.assign(Country=country1),df2.assign(Country=country2)])

    st.plotly_chart(px.line(comp,x="last_updated",y=metric,color="Country"),use_container_width=True)

# ================= VOLATILITY =================

with tab3:

    vol=filtered_df.groupby("country")[metric].agg(["mean","std"])

    vol["volatility"]=vol["std"]/vol["mean"]

    top=vol.sort_values("volatility",ascending=False).head(10)

    st.plotly_chart(px.bar(top.reset_index(),x="country",y="volatility"),use_container_width=True)

# ================= GLOBAL MAP =================

with tab4:

    map_df=filtered_df.groupby(["country","iso_alpha"])[metric].mean().reset_index()

    st.plotly_chart(px.choropleth(map_df,locations="iso_alpha",color=metric,hover_name="country"),use_container_width=True)

    st.subheader("Animated Global Temperature Map")

    anim=filtered_df.copy()
    anim["date"]=anim["last_updated"].dt.date

    fig=px.choropleth(anim,locations="iso_alpha",color="temperature_celsius",hover_name="country",animation_frame="date")

    st.plotly_chart(fig,use_container_width=True)

# ================= COUNTRY PROFILE =================

with tab5:

    countries=sorted(filtered_df["country"].unique())

    search=st.text_input("🔍 Search Country")

    filtered_countries=[c for c in countries if search.lower() in c.lower()]

    country=st.selectbox("Select Country",filtered_countries)

    cdf=filtered_df[filtered_df["country"]==country]

    c1,c2,c3,c4=st.columns(4)

    c1.metric("Avg Temp",round(cdf["temperature_celsius"].mean(),2))
    c2.metric("Humidity",round(cdf["humidity"].mean(),2))
    c3.metric("Wind",round(cdf["wind_kph"].mean(),2))
    c4.metric("Air Quality",round(cdf["air_quality_PM2.5"].mean(),2))

# ================= DOWNLOAD =================

csv=filtered_df.to_csv(index=False).encode("utf-8")

st.download_button("Download Dataset",csv,"climate_data.csv","text/csv")