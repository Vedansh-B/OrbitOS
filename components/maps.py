import folium
from streamlit_folium import st_folium
from datetime import datetime
from components.cloud_layer import get_cloud_coverage
import streamlit as st


def display_map(lat, lon, api_key, new_location_query):
    """
    Display a map centered at the given latitude and longitude,
    with cloud coverage displayed within a 5 km radius.
    """
    # Create a Folium map centered at the provided latitude and longitude
    if new_location_query or st.session_state["map_data"]["map_obj"] is None:
        map_obj = folium.Map(location=[lat, lon],width=900,height=700, zoom_start=12, no_touch= True, max_native_zoom  = 10, min_native_zoom = 13)
        
        
        cloud_circles = get_cloud_coverage(lat, lon, api_key)
        
        # Add cloud coverage
        for i in cloud_circles:
            i.add_to(map_obj)
        st.session_state["map_data"] = {
            "map_obj": map_obj,
            "lat": lat,
            "lon": lon,
        }
    else:
        map_obj = st.session_state["map_data"]["map_obj"]
    
    # Render the map in Streamlit
    st_folium(map_obj)