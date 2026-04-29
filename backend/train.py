import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
from model import IrrigationMLP
from generate_data import generate_synthetic_data
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder

class IrrigationDataset(Dataset):
    def __init__(self, features, labels_class, labels_reg):
        self.features = torch.tensor(features, dtype=torch.float32)
        self.labels_class = torch.tensor(labels_class, dtype=torch.float32).unsqueeze(1)
        self.labels_reg = torch.tensor(labels_reg, dtype=torch.float32).unsqueeze(1)
        
    def __len__(self):
        return len(self.features)
        
    def __getitem__(self, idx):
        return self.features[idx], self.labels_class[idx], self.labels_reg[idx]

def train_model(data_path='../data/irrigation_data.csv', model_path='../data/model.pth', scaler_path='../data/scaler.pkl', epochs=50, batch_size=32):
    if not os.path.exists(data_path):
        print("Data not found, generating...")
        generate_synthetic_data(output_path=data_path)
        
    df = pd.read_csv(data_path)
    
    # Features
    X_num = df[['moisture', 'temperature', 'humidity', 'rain_probability', 'light_intensity']].values
    X_cat = df[['crop_type']].values
    
    # One hot encode crop_type
    encoder = OneHotEncoder(sparse_output=False, categories=[[0,1,2]])
    X_cat_encoded = encoder.fit_transform(X_cat)
    joblib.dump(encoder, '../data/encoder.pkl')
    
    # Scale numerical features
    scaler = StandardScaler()
    X_num_scaled = scaler.fit_transform(X_num)
    joblib.dump(scaler, scaler_path)
    
    # Combine features
    X = np.hstack((X_num_scaled, X_cat_encoded)) # 5 + 3 = 8 features
    
    y_class = df['irrigation_on'].values
    y_reg = df['water_volume'].values
    
    X_train, X_test, yc_train, yc_test, yr_train, yr_test = train_test_split(X, y_class, y_reg, test_size=0.2, random_state=42)
    
    train_dataset = IrrigationDataset(X_train, yc_train, yr_train)
    test_dataset = IrrigationDataset(X_test, yc_test, yr_test)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    model = IrrigationMLP(input_size=X.shape[1])
    
    criterion_class = nn.BCELoss()
    criterion_reg = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    train_losses = []
    val_losses = []
    val_accuracies = []
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for inputs, labels_c, labels_r in train_loader:
            optimizer.zero_grad()
            
            out_c, out_r = model(inputs)
            
            loss_c = criterion_class(out_c, labels_c)
            loss_r = criterion_reg(out_r, labels_r)
            loss = loss_c + 0.1 * loss_r # weighting regression loss
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        train_losses.append(running_loss / len(train_loader))
        
        # Validation
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels_c, labels_r in test_loader:
                out_c, out_r = model(inputs)
                loss_c = criterion_class(out_c, labels_c)
                loss_r = criterion_reg(out_r, labels_r)
                loss = loss_c + 0.1 * loss_r
                val_loss += loss.item()
                
                predicted_c = (out_c > 0.5).float()
                total += labels_c.size(0)
                correct += (predicted_c == labels_c).sum().item()
                
        val_losses.append(val_loss / len(test_loader))
        accuracy = 100 * correct / total
        val_accuracies.append(accuracy)
        
        if (epoch+1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_losses[-1]:.4f} | Val Loss: {val_losses[-1]:.4f} | Val Acc: {accuracy:.2f}%")
            
    # Save model
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}")
    
    # Plotting
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Val Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(val_accuracies, color='green', label='Val Accuracy')
    plt.title('Validation Accuracy (Classification)')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    
    plt.savefig('../data/training_metrics.png')
    print("Saved training metrics plot to ../data/training_metrics.png")

if __name__ == '__main__':
    train_model()
