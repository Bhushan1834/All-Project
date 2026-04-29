# All-Project

This repository contains multiple projects.

## 1. 🔐 Password Generator (Python)

This is a simple command-line Password Generator built using Python.
It allows users to generate a secure random password based on their preferences.

### 🚀 Features

User can set password length

Option to include:

Uppercase letters (A–Z)

Digits (0–9)

Special characters (!, @, #, etc.)

Generates a random secure password

Uses Python built-in modules (random and string)

### 🛠️ Technologies Used

Python

random module (for random character selection)

string module (for predefined character sets)

---

## 2. Smart Agriculture Irrigation System Using MLP

This is a complete intelligent irrigation system that uses a Multi-Layer Perceptron (MLP) built with PyTorch to predict whether to irrigate crops and how much water to supply.

### Features
- **Data Generation**: Generates synthetic crop and environmental data.
- **MLP Model**: PyTorch neural network with a dual output for classification (ON/OFF) and regression (Water Volume).
- **FastAPI Backend**: Provides endpoints for prediction, history logging, and model retraining. Uses SQLite for logging.
- **Real-Time Simulation**: A script to simulate live sensor data streaming to the backend API.
- **Dynamic Web Dashboard**: A premium UI with dark mode, real-time Chart.js graphs, status indicators, and an alerting system.

### Project Structure
```text
/backend/
  ├── generate_data.py   # Dataset generation script
  ├── model.py           # PyTorch MLP model definition
  ├── train.py           # Model training and validation script
  ├── database.py        # SQLite logging setup
  ├── main.py            # FastAPI application
  ├── simulate.py        # Real-time data simulation script
/frontend/
  ├── index.html         # Dashboard HTML
  ├── style.css          # Premium Dark Theme CSS
  ├── app.js             # Client-side logic for real-time updates and charts
/data/                   # Created automatically to store model weights, dataset, and sqlite db
requirements.txt         # Python dependencies
```

### Setup Instructions

#### 1. Install Dependencies
Open your terminal/command prompt and run:
```bash
pip install -r requirements.txt
```

#### 2. Train the Model
Before running the API, you need to generate data and train the MLP model. Navigate to the `backend` folder and run the training script:
```bash
cd backend
python train.py
```
This will:
- Generate `../data/irrigation_data.csv`.
- Train the PyTorch model and save weights (`model.pth`), scalers, and encoders to the `data/` folder.
- Save a training metrics plot to `data/training_metrics.png`.

#### 3. Run the FastAPI Server
Once the model is trained, start the backend server:
```bash
uvicorn main:app --reload
```
The API and frontend dashboard will be available at:
- **Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### 4. Run the Real-Time Simulator
Open a new terminal window, navigate to the `backend` folder, and run the simulator to mock real-time sensor data:
```bash
cd backend
python simulate.py
```
This script will send synthetic sensor data every 5 seconds to the API.

#### 5. View the Dashboard
Go back to your browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to watch the live sensor data update on the charts and see the ML model make real-time irrigation decisions.

### Advanced Capabilities
- **Fallback Logic**: Even if the ML predicts OFF, if the soil moisture drops critically below 15%, the system forces the pump ON. If moisture is above 80%, it forces the pump OFF. This logic is visible in the UI alert box.
- **Model Retraining**: You can trigger model retraining dynamically from the Dashboard via the sidebar button, which triggers the `/retrain` API endpoint to spin up a background training process.
