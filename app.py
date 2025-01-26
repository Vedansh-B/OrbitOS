import streamlit as st
from components.maps import display_map
import requests
import pandas as pd
from datetime import date
from suntime import Sun
import sqlite3
from subscriptions.notification import notification_script
from datetime import datetime, timedelta

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

def check_email_send():
    # Email notification script
    if "email_sender" not in st.session_state:
        # When starting the program, we send out an email with all relevant data
        st.session_state["email_sender"] = {
            "need_to_send": True,
            "most_recent_send": None,
            "week_period": 1,
        }

    # Checking if we need to send another notification
    today = datetime.now()

    # If the most recent send time is None, we can send the first email
    if st.session_state["email_sender"]["most_recent_send"] is None:
        st.session_state["email_sender"]["need_to_send"] = True
    else:
        # Calculate one week from the most recent send date
        resend_date = st.session_state["email_sender"]["most_recent_send"] + timedelta(weeks=st.session_state["email_sender"]["week_period"])
        # Check if the resend date is in the past, meaning it's time to send another notification
        if resend_date <= today:
            st.session_state["email_sender"]["need_to_send"] = True

    # If we need to send another notification
    if st.session_state["email_sender"]["need_to_send"]:
        # Call your notification script here
        notification_script()

        # After sending the email, reset the flag and update the most recent send time
        st.session_state["email_sender"]["need_to_send"] = False
        st.session_state["email_sender"]["most_recent_send"] = today

# Function to get latitude and longitude from a location name
def get_lat_lon(location):
    api_key = "ad85e3fc5fd54c0bbdab0a47b1a9a537"  # Replace with your API key
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

# Get calender date
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
        st.write("Contact us at info.orbit.os@gmail.com")

    # Newsletter Subscription
    st.markdown("## 📬 Subscribe to Our Newsletter")
    email = st.text_input("Enter your Email")
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

column1, column2, column3 = st.columns([0.7, 0.1, 0.2])

with column1:
    # Main Content
    st.title("Orbit OS")
    st.write("Discover the best stargazing spots, track celestial events, and explore space-related data interactively.")

with column2:
    st.write(' ')

with column3:
    st.image("images/logo.jpg", width=256)

location = st.text_input("Enter your location (City, Country)", "Kingston, Canada")

lat, lon = get_lat_lon(location)

# Initialize session state for map data if not already done
if "map_data" not in st.session_state:
    st.session_state["map_data"] = {
        "map_obj": None,
        "lat": None,
        "lon": None,
    }
# Now, you can safely access st.session_state["map_data"]
new_location_query = (
    lat != st.session_state["map_data"]["lat"]
    or lon != st.session_state["map_data"]["lon"]
)

st.header("Best Stargazing Spots")

col11, col22 = st.columns([0.6, 0.4])


with col11:

    if lat and lon:
        st.write(f"Displaying results for: {location}")

        # Input your Meteomatic API Key as a tuple of ("Username", "Password")
        display_map(lat, lon, ("univeristyo_lperson_coo", "K61vQbz56N"), new_location_query)
    else:
        st.write("Could not fetch location. Please check the input or API key.")

with col22:
    def get_weather(location):
        api_key = "d0f8eee362e6488eb8a171041252501 "  # Replace with your WeatherAPI key
        base_url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": location,  # City name, postal code, or coordinates
            "aqi": "no"     # Option to include air quality index
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    # Test the function
    st.title("Weather Widget")

    if location:
        weather_data = get_weather(location)
        if weather_data:
            st.subheader(f"Weather in {weather_data['location']['name']}, {weather_data['location']['country']}")
            st.write(f"Temperature: {weather_data['current']['temp_c']}°C")
            st.write(f"Condition: {weather_data['current']['condition']['text']}")
            st.write(f"Wind Speed: {weather_data['current']['wind_kph']} kph")
            st.image(f"https:{weather_data['current']['condition']['icon']}")

    if weather_data:
        print(f"Location: {weather_data['location']['name']}, {weather_data['location']['country']}")
        print(f"Temperature: {weather_data['current']['temp_c']}°C")
        print(f"Condition: {weather_data['current']['condition']['text']}")
        print(f"Wind Speed: {weather_data['current']['wind_kph']} kph")


st.write("Your local sunset time in UTC: ")
st.write(getSunsetTime(lat, lon))

# Align tables below the map
st.write("## Celestial Events in Your Area")
col1, col2 = st.columns(2)

with col1:
    renderUpcomingEvents("data/cleaned_data/nasa_solar_eclipse_data_revised.csv", "solar eclipse")

with col2:
    renderUpcomingEvents("data/cleaned_data/nasa_lunar_eclipse_data_revised.csv", "lunar eclipse")

check_email_send()