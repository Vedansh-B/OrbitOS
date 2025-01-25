import streamlit as st
from components.maps import display_map

# App Config
st.set_page_config(page_title="OrbitsOS", layout="wide")

# Title and Introduction
st.title("🌌 Celestial Insights")
st.write(
    "Discover the best stargazing spots, track celestial events, "
    "and explore space-related data interactively."
)

# Sidebar
st.sidebar.title("🔧 Settings")
location = st.sidebar.text_input("Enter your location (City, Country)", "Toronto, Canada")

# Main Content
st.header("Best Stargazing Spots")
st.write("Visualizing ideal locations based on light pollution and weather.")
display_map(44.38, -79.69)  # Sample coordinates for placeholder map

# Footer
st.write("Built with ❤️ for the stars.")

if __name__ == "__main__":
    st.write("Running Streamlit App")
