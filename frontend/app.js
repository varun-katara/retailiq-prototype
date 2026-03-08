const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'test-key-123';
const USER_ID = 'demo_user';

let forecastChartInstance = null;

// Upload CSV
async function uploadCSV() {
    const fileInput = document.getElementById('csvFile');
    const resultDiv = document.getElementById('uploadResult');
    
    if (!fileInput.files[0]) {
        resultDiv.innerHTML = '<div class="alert alert-danger">Please select a CSV file</div>';
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    resultDiv.innerHTML = '<div class="alert alert-info">Uploading...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/data/upload?user_id=${USER_ID}`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY
            },
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <strong>✅ Upload Successful!</strong><br>
                    Records processed: ${result.record_count}<br>
                    ${result.deduplicated_records > 0 ? `Duplicates removed: ${result.deduplicated_records}<br>` : ''}
                    Processing time: ${result.processing_time_ms}ms
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <strong>❌ Upload Failed</strong><br>
                    ${result.validation_errors.join('<br>')}
                </div>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

// Get Forecast
async function getForecast() {
    const productId = document.getElementById('productId').value;
    const horizon = document.getElementById('horizon').value;
    const resultDiv = document.getElementById('forecastResult');
    
    if (!productId) {
        resultDiv.innerHTML = '<div class="alert alert-danger">Please enter a Product ID</div>';
        return;
    }
    
    resultDiv.innerHTML = '<div class="alert alert-info">Generating forecast...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/forecast?user_id=${USER_ID}`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId,
                horizon: parseInt(horizon),
                region: 'Maharashtra'
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            displayForecast(result);
        } else {
            resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${result.error}</div>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

function displayForecast(forecast) {
    const resultDiv = document.getElementById('forecastResult');
    
    let html = `
        <div class="alert alert-success">
            <strong>✅ Forecast Generated</strong><br>
            Method: ${forecast.method}<br>
            ${forecast.accuracy_mape ? `Accuracy (MAPE): ${forecast.accuracy_mape.toFixed(2)}%<br>` : ''}
        </div>
    `;
    
    if (forecast.warning) {
        html += `<div class="forecast-warning">⚠️ ${forecast.warning}</div>`;
    }
    
    // Create table
    html += `
        <table class="table table-striped mt-3">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Predicted Demand</th>
                    <th>Lower Bound</th>
                    <th>Upper Bound</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    forecast.predictions.slice(0, 7).forEach(pred => {
        html += `
            <tr>
                <td>${new Date(pred.date).toLocaleDateString()}</td>
                <td>${Math.round(pred.predicted_quantity)}</td>
                <td>${Math.round(pred.lower_bound)}</td>
                <td>${Math.round(pred.upper_bound)}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    resultDiv.innerHTML = html;
    
    // Draw chart
    drawForecastChart(forecast.predictions);
}

function drawForecastChart(predictions) {
    const ctx = document.getElementById('forecastChart').getContext('2d');
    
    if (forecastChartInstance) {
        forecastChartInstance.destroy();
    }
    
    const dates = predictions.map(p => new Date(p.date).toLocaleDateString());
    const predicted = predictions.map(p => p.predicted_quantity);
    const lower = predictions.map(p => p.lower_bound);
    const upper = predictions.map(p => p.upper_bound);
    
    forecastChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Predicted Demand',
                    data: predicted,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                },
                {
                    label: 'Lower Bound',
                    data: lower,
                    borderColor: 'rgb(255, 99, 132)',
                    borderDash: [5, 5],
                    fill: false
                },
                {
                    label: 'Upper Bound',
                    data: upper,
                    borderColor: 'rgb(54, 162, 235)',
                    borderDash: [5, 5],
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Demand Forecast with Confidence Intervals'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Quantity'
                    }
                }
            }
        }
    });
}

// Get Inventory Recommendations
async function getRecommendations() {
    const resultDiv = document.getElementById('recommendationsResult');
    
    // Sample inventory (in real app, this would come from user input)
    const currentInventory = {
        'P001': 20,
        'P002': 50,
        'P003': 10,
        'P004': 100
    };
    
    resultDiv.innerHTML = '<div class="alert alert-info">Calculating recommendations...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/inventory/recommendations?user_id=${USER_ID}`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_inventory: currentInventory,
                lead_time_days: 7
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            displayRecommendations(result.recommendations);
        } else {
            resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${result.error}</div>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

function displayRecommendations(recommendations) {
    const resultDiv = document.getElementById('recommendationsResult');
    
    if (recommendations.length === 0) {
        resultDiv.innerHTML = '<div class="alert alert-success">✅ All products are well-stocked!</div>';
        return;
    }
    
    let html = `
        <div class="alert alert-warning">
            <strong>⚠️ ${recommendations.length} products need reordering</strong>
        </div>
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Current Stock</th>
                    <th>Reorder Point</th>
                    <th>Recommended Qty</th>
                    <th>Risk Score</th>
                    <th>Priority</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    recommendations.forEach(rec => {
        const riskClass = rec.priority === 'high' ? 'risk-high' : 
                         rec.priority === 'medium' ? 'risk-medium' : 'risk-low';
        
        html += `
            <tr>
                <td><strong>${rec.product_id}</strong></td>
                <td>${rec.current_stock}</td>
                <td>${rec.reorder_point}</td>
                <td><strong>${rec.recommended_quantity}</strong></td>
                <td><span class="badge ${riskClass}">${rec.stockout_risk_score.toFixed(1)}%</span></td>
                <td><span class="badge bg-${rec.priority === 'high' ? 'danger' : rec.priority === 'medium' ? 'warning' : 'success'}">${rec.priority.toUpperCase()}</span></td>
            </tr>
            <tr>
                <td colspan="6" class="text-muted small">${rec.reasoning}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    resultDiv.innerHTML = html;
}

// AI Copilot (placeholder - will add Bedrock integration)
async function askCopilot() {
    const query = document.getElementById('copilotQuery').value;
    const chatHistory = document.getElementById('chatHistory');
    
    if (!query.trim()) {
        return;
    }
    
    // Add user message
    chatHistory.innerHTML += `
        <div class="chat-message user-message">
            <strong>You:</strong> ${query}
        </div>
    `;
    
    // Show loading
    chatHistory.innerHTML += `
        <div class="chat-message bot-message" id="loading">
            <strong>RetailIQ AI:</strong> <em>Thinking...</em>
        </div>
    `;
    
    try {
        const response = await fetch(`${API_BASE_URL}/copilot/chat?user_id=${USER_ID}`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                conversation_history: []
            })
        });
        
        const result = await response.json();
        
        // Remove loading message
        document.getElementById('loading')?.remove();
        
        // Add bot response
        chatHistory.innerHTML += `
            <div class="chat-message bot-message">
                <strong>RetailIQ AI:</strong> ${result.answer}
                <br><small class="text-muted">📊 Intent: ${result.intent} | Confidence: ${result.confidence_level}</small>
            </div>
        `;
    } catch (error) {
        document.getElementById('loading')?.remove();
        chatHistory.innerHTML += `
            <div class="chat-message bot-message">
                <strong>RetailIQ AI:</strong> <span class="text-danger">Error: ${error.message}</span>
            </div>
        `;
    }
    
    // Clear input
    document.getElementById('copilotQuery').value = '';
    
    // Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
}


// Allow Enter key for copilot
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('copilotQuery')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            askCopilot();
        }
    });
});
