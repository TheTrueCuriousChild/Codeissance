# app/utils/notifications.py
from twilio.rest import Client
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Validate Twilio credentials
if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    raise ValueError("Twilio credentials not set in .env")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ------------------------
# WhatsApp Notification
# ------------------------
def send_whatsapp(phone_number: str, message: str):
    """
    Send a WhatsApp message via Twilio Sandbox.
    """
    if not phone_number:
        print("Error: phone_number is None")
        return False
    try:
        msg = client.messages.create(
            body=message,
            from_='whatsapp:' + TWILIO_PHONE_NUMBER,
            to='whatsapp:' + phone_number
        )
        print(f"[WhatsApp] Sent to {phone_number}, SID: {msg.sid}")
        return True
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False


# ------------------------
# OSRM / OpenStreetMap routing links
# ------------------------
def get_osrm_route_link(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float):
    """
    Returns OSRM (OpenStreetMap) routing link for driving directions.
    Works like Google Maps, but free and mobile-friendly.
    """
    if not all([origin_lat, origin_lon, dest_lat, dest_lon]):
        return None
    return f"http://map.project-osrm.org/?z=14&center={origin_lat},{origin_lon}&loc={origin_lat},{origin_lon}&loc={dest_lat},{dest_lon}&hl=en&alt=0"

def get_osrm_eta(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float):
    """
    Returns estimated travel time in minutes using OSRM public API.
    """
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}?overview=false"
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None
        data = resp.json()
        duration_sec = data['routes'][0]['duration']
        return duration_sec // 60  # minutes
    except Exception as e:
        print(f"Error fetching OSRM ETA: {e}")
        return None


# ------------------------
# Message Formatter
# ------------------------
def format_whatsapp_message(hospital_name: str, blood_group: str, units: int,
                            donor_lat: float, donor_lon: float,
                            hospital_lat: float, hospital_lon: float):
    """
    Returns WhatsApp message including clickable OSRM link and ETA.
    Can be used for both blood and organ donation requests.
    """
    route_link = get_osrm_route_link(donor_lat, donor_lon, hospital_lat, hospital_lon)
    eta = get_osrm_eta(donor_lat, donor_lon, hospital_lat, hospital_lon)

    message = (
        f"🚨 Emergency Donation Request 🚨\n\n"
        f"Hospital: {hospital_name}\n"
        f"Type: {'Blood' if blood_group else 'Organ'}\n"
        f"Blood Group / Organ Needed: {blood_group}\n"
        f"Units / Quantity Required: {units}\n"
    )
    if route_link:
        message += f"Fastest Route: {route_link}\n"
    if eta:
        message += f"Estimated Travel Time: {eta} mins"
    return message
