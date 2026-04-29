from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import torch
import joblib
import numpy as np
import os
import requests
from database import init_db, log_prediction, get_logs
from model import IrrigationMLP

app = FastAPI(title="Smart Irrigation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
init_db()

MODEL_PATH = '../data/model.pth'
SCALER_PATH = '../data/scaler.pkl'
ENCODER_PATH = '../data/encoder.pkl'

model = None
scaler = None
encoder = None

def load_ml_assets():
    global model, scaler, encoder
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH) and os.path.exists(ENCODER_PATH):
        scaler = joblib.load(SCALER_PATH)
        encoder = joblib.load(ENCODER_PATH)
        
        # Need to know input size: 5 num + 3 cat = 8
        model = IrrigationMLP(input_size=8)
        model.load_state_dict(torch.load(MODEL_PATH))
        model.eval()
        return True
    return False

class SensorData(BaseModel):
    moisture: float
    temperature: float
    humidity: float
    light_intensity: float
    crop_type: int
    lat: Optional[float] = None
    lon: Optional[float] = None

def fetch_weather(lat, lon):
    # Mocking weather API using Open-Meteo if coordinates provided, else return dummy
    if lat is None or lon is None:
        return np.random.uniform(0, 100) # Mock rain probability
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=precipitation_probability"
        response = requests.get(url, timeout=5).json()
        rain_prob = response.get('hourly', {}).get('precipitation_probability', [0])[0]
        return rain_prob
    except:
        return 0.0

@app.on_event("startup")
async def startup_event():
    load_ml_assets()

@app.post("/predict")
def predict_irrigation(data: SensorData):
    if model is None:
        if not load_ml_assets():
            raise HTTPException(status_code=500, detail="Model not trained yet. Run train.py first.")
            
    rain_prob = fetch_weather(data.lat, data.lon)
    
    num_features = np.array([[data.moisture, data.temperature, data.humidity, rain_prob, data.light_intensity]])
    cat_features = np.array([[data.crop_type]])
    
    num_scaled = scaler.transform(num_features)
    cat_encoded = encoder.transform(cat_features)
    
    X_input = np.hstack((num_scaled, cat_encoded))
    X_tensor = torch.tensor(X_input, dtype=torch.float32)
    
    with torch.no_grad():
        out_c, out_r = model(X_tensor)
        
    pred_on = (out_c.item() > 0.5)
    pred_vol = out_r.item()
    
    # Fallback threshold logic
    if data.moisture < 15: # Critical low moisture
        pred_on = True
        pred_vol = max(pred_vol, 5.0)
        status = "CRITICAL_ON"
    elif data.moisture > 80: # Critical overwatered
        pred_on = False
        pred_vol = 0.0
        status = "CRITICAL_OFF"
    else:
        status = "ML_DECISION"
        
    if not pred_on:
        pred_vol = 0.0
        
    # Log data
    log_data = data.dict()
    log_data['rain_probability'] = rain_prob
    log_prediction(log_data, pred_on, pred_vol, status)
    
    return {
        "irrigation_on": bool(pred_on),
        "water_volume_liters": round(pred_vol, 2),
        "rain_probability": rain_prob,
        "status_reason": status
    }

@app.get("/history")
def get_history():
    return get_logs()

@app.post("/retrain")
def retrain_model():
    try:
        import subprocess
        # Run training in background to not block the request
        subprocess.Popen(["python", "train.py"], cwd=os.path.dirname(__file__))
        return {"message": "Retraining started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
