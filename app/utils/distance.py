# app/utils/distance.py
import math
import logging

logger = logging.getLogger("distance")

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points 
    on the Earth specified in decimal degrees using Haversine formula.
    
    Returns distance in kilometers.
    
    If any coordinate is None, returns float('inf') to indicate 'unreachable'.
    """
    if None in (lat1, lon1, lat2, lon2):
        logger.warning(f"Invalid coordinates: ({lat1}, {lon1}), ({lat2}, {lon2})")
        return float('inf')

    try:
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        radius_earth_km = 6371
        return c * radius_earth_km

    except Exception as e:
        logger.error(f"Error calculating distance: {e}")
        return float('inf')
