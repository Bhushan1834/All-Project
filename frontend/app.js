let moistureChart, waterChart;
const API_BASE = window.location.origin;

const MAX_DATA_POINTS = 15;
let labels = [];
let moistureData = [];
let waterData = [];

function initCharts() {
    const ctxM = document.getElementById('moistureChart').getContext('2d');
    moistureChart = new Chart(ctxM, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Moisture Level (%)',
                data: moistureData,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: { y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { color: 'rgba(255,255,255,0.05)' } } },
            plugins: { legend: { display: false } },
            color: '#94a3b8'
        }
    });

    const ctxW = document.getElementById('waterChart').getContext('2d');
    waterChart = new Chart(ctxW, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Water Pumped (L)',
                data: waterData,
                backgroundColor: 'rgba(16, 185, 129, 0.7)',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { color: 'rgba(255,255,255,0.05)' } } },
            plugins: { legend: { display: false } },
            color: '#94a3b8'
        }
    });
}

function updateDashboard() {
    fetch(`${API_BASE}/history`)
        .then(res => res.json())
        .then(data => {
            if(data.length === 0) return;
            
            // Update KPIs with latest
            const latest = data[0];
            document.getElementById('moisture-val').innerText = `${latest.moisture.toFixed(1)} %`;
            document.getElementById('temp-val').innerText = `${latest.temperature.toFixed(1)} °C`;
            document.getElementById('rain-val').innerText = `${latest.rain_probability.toFixed(0)} %`;
            document.getElementById('water-val').innerText = `${latest.predicted_volume.toFixed(2)} L`;
            
            // Status Badge
            const badge = document.getElementById('pump-status');
            const text = document.getElementById('pump-text');
            if(latest.predicted_on) {
                badge.classList.add('on');
                text.innerText = "Pump: RUNNING";
            } else {
                badge.classList.remove('on');
                text.innerText = "Pump: STANDBY";
            }
            
            // Alert System
            const alertBox = document.getElementById('alert-box');
            const alertText = document.getElementById('alert-text');
            if(latest.status === 'CRITICAL_ON') {
                alertBox.style.display = 'flex';
                alertText.innerText = "CRITICAL: Soil moisture too low! Forcing pump ON.";
            } else if(latest.status === 'CRITICAL_OFF') {
                alertBox.style.display = 'flex';
                alertText.innerText = "WARNING: Soil overwatered! Forcing pump OFF.";
            } else {
                alertBox.style.display = 'none';
            }

            // Update Charts
            labels = [];
            moistureData = [];
            waterData = [];
            const chartData = data.slice(0, MAX_DATA_POINTS).reverse();
            
            chartData.forEach(d => {
                const time = new Date(d.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
                labels.push(time);
                moistureData.push(d.moisture);
                waterData.push(d.predicted_volume);
            });
            
            moistureChart.data.labels = labels;
            moistureChart.data.datasets[0].data = moistureData;
            moistureChart.update();
            
            waterChart.data.labels = labels;
            waterChart.data.datasets[0].data = waterData;
            waterChart.update();
            
            // Update Table
            updateTable(data.slice(0, 10));
        })
        .catch(err => console.error("Error fetching data:", err));
}

function updateTable(logs) {
    const tbody = document.querySelector('#history-table tbody');
    tbody.innerHTML = '';
    logs.forEach(log => {
        const tr = document.createElement('tr');
        const time = new Date(log.timestamp).toLocaleTimeString();
        tr.innerHTML = `
            <td>${time}</td>
            <td>${log.moisture.toFixed(1)}%</td>
            <td>${log.rain_probability.toFixed(0)}%</td>
            <td>${log.status}</td>
            <td><span style="color: ${log.predicted_on ? '#10b981' : '#94a3b8'}">${log.predicted_on ? 'ON' : 'OFF'}</span></td>
            <td>${log.predicted_volume.toFixed(2)} L</td>
        `;
        tbody.appendChild(tr);
    });
}

function retrainModel() {
    alert("Triggering model retraining in the background...");
    fetch(`${API_BASE}/retrain`, {method: 'POST'})
        .then(res => res.json())
        .then(data => console.log(data))
        .catch(err => console.error(err));
}

function fetchHistory() {
    updateDashboard(); // Refreshes view
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    updateDashboard();
    // Poll every 3 seconds for live updates
    setInterval(updateDashboard, 3000);
});
