import streamlit as st
from components.maps import display_map
import requests 
import pandas as pd
from datetime import date
from suntime import Sun
import requests  
import sqlite3


# Initialize the database
def init_db():
    conn = sqlite3.connect("subscribers.db")  # Create or open the database file
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE
        )
    """)  # Create the subscribers table
    conn.commit()
    conn.close()

# Function to get latitude and longitude from a location name
def get_lat_lon(location):
    # Example: Using OpenCage Geocoder API (replace with your API key)
    api_key = ""  # Replace with your API key
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={api_key}"
    response = requests.get(url).json()
    if response['results']:
        lat = response['results'][0]['geometry']['lat']
        lon = response['results'][0]['geometry']['lng']
        return lat, lon
    return None, None

# Initialize the database at app start
init_db()

def getSunsetTime(latitude, longitude):
    sun = Sun(latitude, longitude)
    return sun.get_sunset_time()

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
            df.drop(index, axis = "index", inplace=True)

    # Changes solar eclipse types from letters to words
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
st.title("🌌 Orbit OS")
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

st.write(getSunsetTime(lat, lon))

# Weather Information
import requests

def get_weather(location):
    api_key = ""  # Replace with your WeatherAPI key
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
location = st.text_input("Enter a city name or postal code:", "Toronto")

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


col1, col2 = st.columns(2)

with col1:
    renderUpcomingEvents("data/cleaned_data/nasa_solar_eclipse_data_revised.csv", "solar eclipse")

with col2:
    renderUpcomingEvents("data/cleaned_data/nasa_lunar_eclipse_data_revised.csv", "lunar eclipse")

# About Us Section
st.header("About Us")
st.write("This app is designed to help stargazers find the best spots and track celestial events.")

# Newsletter Subscription Section (in the Sidebar)
with st.sidebar:
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
            # Show confirmation message with a checkmark
            st.markdown(
                f"<p style='color: green; font-size: 18px;'>✅ Thank you for subscribing with {email}!</p>",
                unsafe_allow_html=True,
            )
        except sqlite3.IntegrityError:
            st.error("This email is already subscribed.")
    elif subscribe and not email:
        st.error("Please enter a valid email address.")

# Admin Section: View Subscribers (Optional)
# if st.checkbox("View Subscribers (Admin)"):
#     conn = sqlite3.connect("subscribers.db")
#     cursor = conn.cursor()
#     cursor.execute("SELECT email FROM subscribers")
#     rows = cursor.fetchall()
#     conn.close()

#     # Display the subscriber emails
#     st.write("### Subscribed Emails:")
#     if rows:
#         for row in rows:
#             st.write(f"- {row[0]}")
#     else:
#         st.write("No subscribers yet.")


# if __name__ == "__main__":
#     st.write("Running Streamlit App")
#     st.write("### Subscribed Emails:")
#     for row in rows:
#         st.write(f"- {row[0]}")