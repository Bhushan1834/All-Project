import requests
import time
import random

API_URL = "http://127.0.0.1:8000/predict"

def simulate_data_stream():
    print("Starting real-time simulation...")
    crop_type = 1 # Corn
    
    # Initial state
    moisture = 60.0
    
    while True:
        # Simulate environment changes
        temp = random.uniform(20, 35)
        humidity = random.uniform(30, 70)
        light = random.uniform(5000, 80000)
        
        # Soil slowly dries over time
        moisture -= random.uniform(0.5, 2.0)
        if moisture < 0:
            moisture = 0
            
        payload = {
            "moisture": round(moisture, 2),
            "temperature": round(temp, 2),
            "humidity": round(humidity, 2),
            "light_intensity": round(light, 2),
            "crop_type": crop_type,
            "lat": 34.05,
            "lon": -118.24
        }
        
        try:
            res = requests.post(API_URL, json=payload)
            if res.status_code == 200:
                data = res.json()
                print(f"Sent: Moisture={payload['moisture']}% | Prediction: ON={data['irrigation_on']}, Vol={data['water_volume_liters']}L | Reason={data['status_reason']}")
                
                # If pump turned on, simulate moisture increasing
                if data['irrigation_on']:
                    moisture += data['water_volume_liters'] * 2 # Mock absorption
                    print(f"-> Watering... Moisture increased to {moisture:.2f}%")
            else:
                print("Error from API:", res.text)
        except Exception as e:
            print("Failed to connect to API. Make sure FastAPI server is running.")
            
        time.sleep(5) # Poll every 5 seconds

if __name__ == "__main__":
    simulate_data_stream()
