# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import donors, hospitals, inventories, match, requests, offers
from app.agents import monitor, router_ai
import threading

# Step 1: Initialize FastAPI app
app = FastAPI(title="Community Blood & Organ Donation Tracker")

# Step 2: Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon/demo purposes; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Step 3: Include all API routes
app.include_router(donors.router)
app.include_router(hospitals.router)
app.include_router(inventories.router)
app.include_router(match.router)
app.include_router(requests.router)
app.include_router(offers.router)

# Step 4: Root endpoint for health check
@app.get("/")
def root():
    return {"status": "Community Blood & Organ Donation Tracker API is running."}

# Step 5: Startup event to run agents in background threads
@app.on_event("startup")
def startup_event():
    # Inventory monitoring agent runs in the background
    threading.Thread(target=monitor.start_monitoring, daemon=True).start()
    
    # Router AI agent runs in the background
    threading.Thread(target=router_ai.start_router, daemon=True).start()

# Step 6: Shutdown event to clean up agents
@app.on_event("shutdown")
def shutdown_event():
    try:
        monitor.stop_monitoring()         # Stop inventory monitoring cleanly
        router_ai.router_agent.stop_routing()  # Stop router agent cleanly
    except Exception as e:
        print(f"Error during shutdown: {e}")
