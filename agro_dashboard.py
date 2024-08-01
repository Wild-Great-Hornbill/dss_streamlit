import streamlit as st
from streamlit_gsheets import GSheetsConnection

# ydata profiling
import pandas as pd
from ydata_profiling import ProfileReport
import matplotlib.pyplot as plt
import plotly_express as px
import seaborn as sns

# report untuk streamlit
from streamlit_pandas_profiling import st_profile_report

# ----------------CONFIG--------------
st.set_page_config(
    page_title="Agricultural Crop Production Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------- Judul Dashboard
st.markdown("<h1 style='text-align: center;'> Agriculture Crop Production Dashboard </h1>",
            unsafe_allow_html=True)
st.markdown("---")


#  ------- Read Dataset
conn = st.connection("gsheet", type=GSheetsConnection)
df = conn.read(
    spreadsheet = st.secrets.gsheet_promotion["spreadsheet"],
    worksheet = st.secrets.gsheet_promotion["worksheet"]
)

# ------- EDA
convert_col = ['Area', 'Production']
df[convert_col] = df[convert_col].apply(pd.to_numeric, errors='coerce')
def change_units(df):
    if df['Production Units']=='Bales':
        data_production=df['Production']*0.17
        return data_production
    elif df['Production Units'] == 'Nuts':
        data_production = df['Production']*0.00135
        return data_production
    else: 
        return df['Production']
df["Production"] = df.apply(change_units, axis=1)

# Extract unique years and combine unique countries from both columns for the dropdown
years = sorted(df['Year'].unique())
state = sorted(df['State'].unique())

# Year/country selection slider and dropdown
selected_state = st.selectbox("Select State", state, key="state_select")
selected_year = st.selectbox("Select Years", years, key="years_select")

# Filter the dataset based on selected year and country
filter_df = df[(df['Year'] == selected_year) & (df['State'] == selected_state)]

# Data for countries of origin including 0 values
crop = filter_df.groupby('Crop').agg({'Area':'sum','Production':'sum','Yield':'sum'}).reset_index()
season = filter_df.groupby('Season').agg({'Area':'sum','Production':'sum','Yield':'sum'}).reset_index()
district = filter_df.groupby('District').agg({'Area':'sum','Production':'sum','Yield':'sum'}).reset_index()

# Create the bar charts for top 10 countries
top_district = district.nlargest(10,'Production')
top_crop = crop.nlargest(10, 'Production')

crop_bar = px.bar(top_crop, x='Production', y='Crop',
                        orientation='h', color='Production', color_continuous_scale='YlOrRd',
                        title='Top 10 Crop With Highest Production').update_layout(yaxis=dict(categoryorder='total ascending'))

district_bar = px.bar(top_district, x='Production', y='District',
                        orientation='h', color='Production', color_continuous_scale='YlOrRd',
                        title='Top 10 District With Highest Production').update_layout(yaxis=dict(categoryorder='total ascending'))

season_pie = px.pie(season, names='Season', values='Production', color='Production', 
             title='Season the State', hole=0.4)

# Display the maps and bar charts side by side
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(crop_bar, use_container_width=True)
    st.plotly_chart(season_pie, use_container_width=True)

with col2:
    st.plotly_chart(district_bar, use_container_width=True)

    


