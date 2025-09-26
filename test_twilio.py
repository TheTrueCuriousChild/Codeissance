# test_whatsapp.py
from app.utils.notifications import send_whatsapp

# Replace with your personal WhatsApp number (joined Twilio sandbox)
my_number = "+919930709904"
message = "Hello! This is a test message from Donation Tracker."

success = send_whatsapp(my_number, message)
print("Message sent successfully!" if success else "Message failed.")
