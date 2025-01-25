import streamlit as st
from components.maps import display_map
import requests  # For geocoding API to fetch lat/lon from location name

# Function to get latitude and longitude from a location name
def get_lat_lon(location):
    # Example: Using OpenCage Geocoder API (replace with your API key)
    api_key = "Your API Key"  # Replace with your API key
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={api_key}"
    response = requests.get(url).json()
    if response['results']:
        lat = response['results'][0]['geometry']['lat']
        lon = response['results'][0]['geometry']['lng']
        return lat, lon
    return None, None

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
