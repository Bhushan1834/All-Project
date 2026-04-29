import sqlite3
import os

DB_PATH = '../data/irrigation_logs.db'

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            moisture REAL,
            temperature REAL,
            humidity REAL,
            rain_probability REAL,
            light_intensity REAL,
            crop_type INTEGER,
            predicted_on INTEGER,
            predicted_volume REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_prediction(data, predicted_on, predicted_volume, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (moisture, temperature, humidity, rain_probability, light_intensity, crop_type, predicted_on, predicted_volume, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['moisture'], data['temperature'], data['humidity'], data['rain_probability'], 
          data['light_intensity'], data['crop_type'], int(predicted_on), float(predicted_volume), status))
    conn.commit()
    conn.close()

def get_logs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return data
