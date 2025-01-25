import streamlit as st
from components.maps import display_map
import sqlite3
import requests

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

# Get latitude and longitude from a location name
def get_lat_lon(location):
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

# App Config
st.set_page_config(page_title="Celestial Insights", layout="wide")

# Load CSS for styling
try:
    with open("static/styles.css") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.error("CSS file not found. Make sure 'static/styles.css' exists.")

# Add navigation bar
st.markdown(
    """
    <div class="nav">
        <a href="#about-us">About Us</a>
        <a href="#newsletter">Newsletter</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# Title and Introduction
st.title("🌌 Celestial Insights")
st.write("Discover the best stargazing spots, track celestial events, and explore space-related data interactively.")

# Main Content
st.header("Best Stargazing Spots")
location = st.text_input("Enter your location (City, Country)", "Toronto, Canada")
lat, lon = get_lat_lon(location)

if lat and lon:
    st.write(f"Displaying results for: {location}")
    display_map(lat, lon)
else:
    st.write("Could not fetch location. Please check the input or API key.")

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
if st.checkbox("View Subscribers (Admin)"):
    conn = sqlite3.connect("subscribers.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM subscribers")
    rows = cursor.fetchall()
    conn.close()

    st.write("### Subscribed Emails:")
    for row in rows:
        st.write(f"- {row[0]}")
