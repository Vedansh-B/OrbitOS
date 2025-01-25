import streamlit as st
import folium
from streamlit_folium import st_folium

def display_map(lat, lon):
    """
    Display a map centered at the given latitude and longitude.
    """
    # Create a Folium map centered at the provided latitude and longitude
    map_obj = folium.Map(location=[lat, lon], zoom_start=8)
    # Add a marker for the location
    folium.Marker([lat, lon], tooltip="Best Stargazing Spot").add_to(map_obj)
    # Render the map in Streamlit
    st_folium(map_obj, width=700)
