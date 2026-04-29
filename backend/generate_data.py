import pandas as pd
import numpy as np
import os

def generate_synthetic_data(num_samples=5000, output_path='../data/irrigation_data.csv'):
    np.random.seed(42)
    
    # Features
    moisture = np.random.uniform(10, 90, num_samples) # 10% to 90%
    temp = np.random.uniform(15, 45, num_samples) # 15C to 45C
    humidity = np.random.uniform(20, 90, num_samples)
    rain_prob = np.random.uniform(0, 100, num_samples)
    light = np.random.uniform(1000, 100000, num_samples)
    
    # 0: Wheat, 1: Corn, 2: Rice
    crop_type = np.random.choice([0, 1, 2], num_samples)
    
    # Labels Logic
    irrigation_on = np.zeros(num_samples)
    water_volume = np.zeros(num_samples)
    
    for i in range(num_samples):
        needs_water = False
        if crop_type[i] == 0: # Wheat
            moisture_thresh = 35
        elif crop_type[i] == 1: # Corn
            moisture_thresh = 40
        else: # Rice
            moisture_thresh = 60
            
        if moisture[i] < moisture_thresh and rain_prob[i] < 40:
            needs_water = True
        elif moisture[i] < (moisture_thresh - 15):
            needs_water = True
            
        if needs_water:
            irrigation_on[i] = 1
            base_vol = (moisture_thresh - moisture[i]) * 0.5 
            temp_factor = (temp[i] - 20) * 0.1 if temp[i] > 20 else 0
            water_volume[i] = max(1.0, base_vol + temp_factor) 
            
    df = pd.DataFrame({
        'moisture': moisture,
        'temperature': temp,
        'humidity': humidity,
        'rain_probability': rain_prob,
        'light_intensity': light,
        'crop_type': crop_type,
        'irrigation_on': irrigation_on,
        'water_volume': water_volume
    })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_samples} samples at {output_path}")

if __name__ == '__main__':
    generate_synthetic_data()
