# app/utils/routing.py
import os
import requests

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")  # set this in .env

def get_route_info(origin_lat, origin_lon, dest_lat, dest_lon):
    """
    Returns distance (km), duration (minutes), and Google Maps navigation link
    from origin to destination using Google Maps Directions API.
    """
    try:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": f"{origin_lat},{origin_lon}",
            "destination": f"{dest_lat},{dest_lon}",
            "key": GOOGLE_MAPS_API_KEY,
            "mode": "driving"
        }
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] != "OK":
            return None, None, None

        route = data["routes"][0]["legs"][0]
        distance_km = route["distance"]["value"] / 1000  # meters -> km
        duration_min = route["duration"]["value"] / 60   # seconds -> minutes

        # Google Maps link for navigation
        maps_link = f"https://www.google.com/maps/dir/?api=1&origin={origin_lat},{origin_lon}&destination={dest_lat},{dest_lon}&travelmode=driving"

        return round(distance_km, 2), round(duration_min, 2), maps_link

    except Exception as e:
        print(f"Error fetching route info: {e}")
        return None, None, None
