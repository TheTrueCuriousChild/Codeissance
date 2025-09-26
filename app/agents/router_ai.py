# app/agents/router_ai.py
import threading
import time
import logging
from typing import List
from sqlalchemy.orm import Session
from app import crud, database, schemas
from app.utils.distance import haversine_distance as calculate_distance
from app.utils.notifications import send_whatsapp
from app.utils import routing

logger = logging.getLogger("router_agent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

POLL_INTERVAL = 10
MAX_DISTANCE_KM = 50.0

class RouterAgent:
    def __init__(self):
        self._stop_event = threading.Event()
        self.db: Session = database.SessionLocal()

    def notify_donor(self, donor: schemas.DonorProfileResponse, request_id: int):
        """
        Notify donor via WhatsApp
        """
        phone_number = getattr(donor.user, "phone", None)
        if phone_number:
            message = f"Emergency! Hospital needs {request_id} units of {donor.blood_group}. Please contact immediately."
            send_whatsapp(phone_number, message)
        logger.info(f"WhatsApp sent to donor {donor.id} for request {request_id}")

    def get_nearest_donors(
        self, blood_group: str, hospital_lat: float, hospital_lon: float, db: Session, max_distance_km: float = MAX_DISTANCE_KM
    ) -> List[schemas.DonorProfileResponse]:
        donors = crud.get_available_donors(db, blood_group)
        donors_with_distance = []

        for donor in donors:
            dist = calculate_distance(donor.latitude, donor.longitude, hospital_lat, hospital_lon)
            if dist <= max_distance_km:
                donor.distance_km = round(dist, 2)
                
                # Get ETA and Google Maps link
                eta, _, maps_link = routing.get_route_info(
                    donor.latitude, donor.longitude, hospital_lat, hospital_lon
                )
                donor.eta_min = eta
                donor.maps_link = maps_link
                
                donors_with_distance.append(donor)

        return sorted(donors_with_distance, key=lambda d: d.distance_km)

    def process_requests(self):
        while not self._stop_event.is_set():
            try:
                pending_requests = self.db.query(crud.models.Request).filter(
                    crud.models.Request.fulfilled == False
                ).all()

                for req in pending_requests:
                    req_hospital = crud.get_hospital_by_id(self.db, req.hospital_id)
                    if not req_hospital:
                        continue

                    donors = crud.get_available_donors(self.db, req.blood_group)
                    donors_sorted = sorted(
                        donors,
                        key=lambda d: calculate_distance(d.latitude, d.longitude, req_hospital.latitude, req_hospital.longitude)
                    )

                    notified_count = 0
                    for donor in donors_sorted:
                        dist = calculate_distance(donor.latitude, donor.longitude, req_hospital.latitude, req_hospital.longitude)
                        if dist <= MAX_DISTANCE_KM:
                            self.notify_donor(donor, req.id)
                            notified_count += 1
                            crud.mark_donor_notified(self.db, donor.id, req.id)

                        if notified_count >= req.units_needed:
                            crud.mark_request_fulfilled(self.db, req.id)
                            logger.info(f"Request {req.id} marked as fulfilled automatically.")
                            break

            except Exception as e:
                logger.error(f"Error in router agent: {e}")

            time.sleep(POLL_INTERVAL)

    def start_routing(self):
        logger.info("Router agent started.")
        self.thread = threading.Thread(target=self.process_requests, daemon=True)
        self.thread.start()

    def stop_routing(self):
        self._stop_event.set()
        self.thread.join()
        self.db.close()
        logger.info("Router agent stopped.")

router_agent = RouterAgent()

def start_router():
    router_agent.start_routing()
