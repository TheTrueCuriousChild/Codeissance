# app/utils/notifications.py
from twilio.rest import Client
import os
from dotenv import load_dotenv
import urllib.parse

# Load .env variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")  # Twilio SID
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")    # Twilio Auth Token
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Twilio WhatsApp sandbox number, e.g., +14155238886
ORS_API_KEY = os.getenv("ORS_API_KEY")  # OpenRouteService key

# Validate environment variables
if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    raise ValueError("Twilio credentials not set in .env")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ------------------------
# WhatsApp Notification
# ------------------------
def send_whatsapp(phone_number: str, message: str):
    """
    Send a WhatsApp message via Twilio Sandbox.
    phone_number must include country code, e.g., +91XXXXXXXXXX
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
# Location / Map Links
# ------------------------
def get_google_maps_link(latitude: float, longitude: float):
    """
    Returns a clickable Google Maps link for the coordinates.
    """
    if not latitude or not longitude:
        return None
    return f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"

def get_ors_route_link(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float):
    """
    Returns an OpenRouteService link showing driving directions.
    ORS cannot generate full clickable link directly, so we use their maps site with query params.
    """
    if not all([origin_lat, origin_lon, dest_lat, dest_lon]):
        return None
    
    # ORS Maps link with start and end
    origin = f"{origin_lat},{origin_lon}"
    destination = f"{dest_lat},{dest_lon}"
    return f"https://maps.openrouteservice.org/directions?n1={origin_lat}&n2={origin_lon}&n3=14&a={origin_lat},{origin_lon},{dest_lat},{dest_lon}&b=0&c=0&k1=en-US&k2=km"

def format_whatsapp_message(hospital_name: str, blood_group: str, units: int, latitude: float, longitude: float):
    """
    Formats message for donor with clickable map link.
    """
    map_link = get_google_maps_link(latitude, longitude)  # you can switch to get_ors_route_link if preferred
    message = f"Urgent Blood Request!\n\nHospital: {hospital_name}\nBlood Group: {blood_group}\nUnits Needed: {units}\n"
    if map_link:
        message += f"Location: {map_link}"
    return message
