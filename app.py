import streamlit as st
from components.maps import display_map
import requests
import pandas as pd
from datetime import date
from suntime import Sun
import sqlite3

# Initialize the database
def init_db():
    conn = sqlite3.connect("subscribers.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

# Function to get latitude and longitude from a location name
def get_lat_lon(location):
    api_key = "36412dcc67a4467b85c7a9e5007bc91d"  # Replace with your API key
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={api_key}"
    response = requests.get(url).json()
    if response['results']:
        lat = response['results'][0]['geometry']['lat']
        lon = response['results'][0]['geometry']['lng']
        return lat, lon
    return None, None

# Get sunset time
def getSunsetTime(latitude, longitude):
    sun = Sun(latitude, longitude)
    return sun.get_sunset_time()

def getCurrentDate():
        return date.today()

# Filter and render upcoming events
def renderUpcomingEvents(csvPath, eventType):
    date_today = getCurrentDate()
    st.markdown(f"### Upcoming {eventType.capitalize()} Events")
    df = pd.read_csv(csvPath).drop(columns=["Unnamed: 0"])
    df = df[df['Calendar Date'].apply(lambda x: convertEnglishDateToYearInt(x) >= int(str(date_today)[:4]))]

    if eventType == "solar eclipse":
        convertSolarEclipseType(df)
    elif eventType == "lunar eclipse":
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

# App setup
st.set_page_config(page_title="Orbit OS", layout="wide")
init_db()

# Sidebar Navigation Menu
with st.sidebar:
    st.markdown("## Navigation Menu")
    if st.button("Home"):
        st.experimental_rerun()
    if st.button("Stargazing Tips"):
        st.write("Here are some tips for stargazing...")
    if st.button("Contribute Data"):
        st.write("You can contribute data here.")
    if st.button("Contact Us"):
        st.write("Contact us at orbitos@example.com.")

    # Newsletter Subscription
    st.markdown("## 📬 Subscribe to Our Newsletter")
    email = st.text_input("Enter your email")
    subscribe = st.button("Subscribe")
    if subscribe and email:
        try:
            conn = sqlite3.connect("subscribers.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO subscribers (email) VALUES (?)", (email,))
            conn.commit()
            conn.close()
            st.success(f"✅ Thank you for subscribing with {email}!")
        except sqlite3.IntegrityError:
            st.error("This email is already subscribed.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    elif subscribe and not email:
        st.error("Please enter a valid email address.")

# Main Content
st.title("🌌 Orbit OS")
st.write("Discover the best stargazing spots, track celestial events, and explore space-related data interactively.")

st.header("Best Stargazing Spots")
location = st.text_input("Enter your location (City, Country)", "Toronto, Canada")

lat, lon = get_lat_lon(location)

if lat and lon:
    st.write(f"Displaying results for: {location}")
    with st.container():
        display_map(lat, lon)
else:
    st.error("Could not fetch location. Please check the input or API key.")

# Align tables below the map
st.write("## Celestial Events in Your Area")
col1, col2 = st.columns(2)

with col1:
    renderUpcomingEvents("data/cleaned_data/nasa_solar_eclipse_data_revised.csv", "solar eclipse")

with col2:
    renderUpcomingEvents("data/cleaned_data/nasa_lunar_eclipse_data_revised.csv", "lunar eclipse")

# Admin Section
if st.checkbox("View Subscribers (Admin)"):
    conn = sqlite3.connect("subscribers.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM subscribers")
    rows = cursor.fetchall()
    conn.close()

    st.markdown("### Subscribed Emails")
    if rows:
        for row in rows:
            st.write(f"- {row[0]}")
    else:
        st.info("No subscribers yet.")
