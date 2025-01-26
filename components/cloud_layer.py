import math
from datetime import datetime
import folium
import requests


def fetch_point_coverage(lat, lon, api_key):
    """
    Fetch total cloud cover percentage from Meteomatics API for the given latitude and longitude.
    """
    current_time = datetime.utcnow().isoformat() + 'Z'  # Current UTC time in ISO format
    url = f'https://api.meteomatics.com/{current_time}/total_cloud_cover:p/{lat},{lon}/json'
    response = requests.get(url, auth=api_key)
    if response.status_code == 200:
        data = response.json()
        # Extract the cloud cover value
        cloud_cover = data['data'][0]['coordinates'][0]['dates'][0]['value']
        return cloud_cover
    else:
        print(f"Error fetching cloud coverage: {response.status_code}")
        return None


def generate_25_dense_points(center_lat, center_lon, circle_radius_km, overlap_fraction):
    """
    Generate exactly 25 points in a compact hexagonal pattern with slight overlap.
    """
    points = []
    distance_between_centers = circle_radius_km * 2 * (1 - overlap_fraction)  # Slight overlap between circles
    num_points = 25
    current_ring = 0

    while len(points) < num_points:
        points_in_ring = 6 * current_ring if current_ring > 0 else 1  # 1 point at center, then hexagonal rings
        angle_increment = 360 / points_in_ring if points_in_ring > 1 else 0

        for i in range(points_in_ring):
            if len(points) >= num_points:
                break

            angle = math.radians(i * angle_increment)
            dx = current_ring * distance_between_centers * math.cos(angle)
            dy = current_ring * distance_between_centers * math.sin(angle)
            new_lat = center_lat + (dy / 111)  # Approx. 111 km per degree latitude
            new_lon = center_lon + (dx / (111 * math.cos(math.radians(center_lat))))  # Adjust for longitude scaling
            points.append((new_lat, new_lon))

        current_ring += 1

    return points[:num_points]  # Ensure exactly 25 points


def fetch_cloud_coverage(lat, lon, api_key):
    """
    Fetch simulated cloud coverage for 25 points around the given latitude and longitude.
    """
    cloud_points = []
    spaced_points = generate_25_dense_points(lat, lon, circle_radius_km=1, overlap_fraction=0.15)  # Slight overlap

    for point_lat, point_lon in spaced_points:
        # Fetch cloud cover for each generated point
        cloud_point = fetch_point_coverage(point_lat, point_lon, api_key)
        if cloud_point is not None:
            cloud_points.append({
                'lat': point_lat,
                'lon': point_lon,
                'cloud_cover': cloud_point
            })

    return cloud_points


def get_cloud_coverage(centre_lat, centre_lon, api_key):
    """
    Add a cloud coverage layer to the map with minimal gaps and exactly 25 data points.
    """
    clouds = []
    cloud_points = fetch_cloud_coverage(centre_lat, centre_lon, api_key)

    for cloud in cloud_points:
        if cloud is not None:
            cloud_percent = cloud.get('cloud_cover')
            fill_color = (
                "lightblue" if 0 <= cloud_percent < 25 else
                "skyblue" if 25 <= cloud_percent < 50 else
                "deepskyblue" if 50 <= cloud_percent < 75 else
                "darkblue"
            )
            circle = folium.Circle(
                location=[cloud['lat'], cloud['lon']],
                radius=1150,  # Slightly larger radius (1.15 km)
                color="blue" if cloud_percent < 30 else "gray",
                fill=True,
                fill_color=fill_color,
                fill_opacity=0.4,
                tooltip=f"Cloud Coverage: {cloud_percent}%",
            )
            clouds.append(circle)
    return clouds