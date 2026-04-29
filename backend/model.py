import torch
import torch.nn as nn

class IrrigationMLP(nn.Module):
    def __init__(self, input_size=8):
        super(IrrigationMLP, self).__init__()
        self.fc1 = nn.Linear(input_size, 32)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(32, 16)
        self.relu2 = nn.ReLU()
        
        # Dual Output
        self.out_class = nn.Linear(16, 1)
        self.out_reg = nn.Linear(16, 1)
        
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc2(x)
        x = self.relu2(x)
        
        y_class = torch.sigmoid(self.out_class(x))
        y_reg = torch.relu(self.out_reg(x))
        
        return y_class, y_reg
