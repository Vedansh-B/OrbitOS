import streamlit as st
import pandas as pd
from datetime import date 
from datetime import datetime
from components.maps import display_map
import math
from suntime import Sun
import requests  # For geocoding API to fetch lat/lon from location name

# Function to get latitude and longitude from a location name
def get_lat_lon(location):
    # Example: Using OpenCage Geocoder API (replace with your API key)

    """
    api_key = "Your API Key"  # Replace with your API key
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={api_key}"
    response = requests.get(url).json()
    if response['results']:
        lat = response['results'][0]['geometry']['lat']
        lon = response['results'][0]['geometry']['lng']
        return lat, lon
    return None, None
    """

    def getSunsetTime(latitude, longitude):
        sun = Sun(latitude, longitude)
        return sun.get_sunset_time()

    st.write(getSunsetTime(44.20, 76.40))

    def getCurrentDate():
        return date.today()
    
    def renderUpcomingEvents(csvPath, eventType):
        date = getCurrentDate()
        st.write("Upcoming " + eventType + " events in your area: ")
        df = pd.read_csv(csvPath)

        #Drop Unecessary Columns
        df = df.drop(columns=["Unnamed: 0"])

        #Drop past events
        for index, row in df.iterrows():
            if not convertEnglishDateToYearInt(row['Calendar Date']) >= int(str(date.today())[:4]):
                df.drop(index, axis="index", inplace=True)

        #Changes solar eclipse types from letters to words
        if eventType == "solar eclipse":
            convertSolarEclipseType(df)
        if eventType == "lunar eclipse":
            convertLunarEclipseType(df)

        st.table(df.head(5))

    def convertEnglishDateToYearInt(date):
        for i in range(len(date)):
            if date[i] == " ":
                return int(date[:i])
        return None
    
    def convertLunarEclipseType(df):
        for index, row in df.iterrows():
            if row['Eclipse Type'][0] == "T":
                row['Eclipse Type'] = "Total"
            elif row['Eclipse Type'][0] == "P":
                row['Eclipse Type'] = "Partial"
            elif row['Eclipse Type'][0] == "N":
                row['Eclipse Type'] = "Penumbral"

    def convertSolarEclipseType(df):
        for index, row in df.iterrows():
            if row['Eclipse Type'][0] == "T":
                row['Eclipse Type'] = "Total"
            elif row['Eclipse Type'][0] == "A":
                row['Eclipse Type'] = "Annular"
            elif row['Eclipse Type'][0] == "P":
                row['Eclipse Type'] = "Partial"
    
    col1, col2 = st.columns(2)

    with col1:
        renderUpcomingEvents("data/nasa_solar_eclipse_data_revised.csv", "solar eclipse")

    with col2:
        renderUpcomingEvents("data/nasa_lunar_eclipse_data_revised.csv", "lunar eclipse")

# App Config
st.set_page_config(page_title="Celestial Insights", layout="wide")

# Navigation Bar
with st.container():
    st.markdown(
        """
        <style>
        .nav {
            display: flex;
            justify-content: flex-end;
            padding: 10px;
            background-color: #333;
            color: white;
        }
        .nav a {
            color: white;
            text-decoration: none;
            padding: 0 10px;
            font-weight: bold;
        }
        .nav a:hover {
            text-decoration: underline;
        }
        </style>
        <div class="nav">
            <a href="#about-us">About Us</a>
            <a href="#login">Login</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Title and Introduction
st.title("🌌 Celestial Insights")
st.write(
    "Discover the best stargazing spots, track celestial events, "
    "and explore space-related data interactively."
)

# Main Content
st.header("Best Stargazing Spots")
location = st.text_input("Enter your location (City, Country)", "Toronto, Canada")

# Get latitude and longitude from the location entered by the user
lat, lon = get_lat_lon(location)

if lat and lon:
    st.write(f"Displaying results for: {location}")
    display_map(lat, lon)
else:
    st.write("Could not fetch location. Please check the input or API key.")

# About Us Section
st.header("About Us")
st.write("This app is designed to help stargazers find the best spots and track celestial events.")

# Placeholder Login Section
st.header("Login")
st.write("Login functionality will be added here in the future.")

# Footer
st.write("Built with ❤️ for the stars.")

if __name__ == "__main__":
    st.write("Running Streamlit App")
