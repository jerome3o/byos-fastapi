// TRMNL Control Panel JavaScript

// Canvas setup
const canvas = document.getElementById('drawingCanvas');
const ctx = canvas.getContext('2d');
let isDrawing = false;
let brushSize = 3;

// Initialize canvas
ctx.fillStyle = 'white';
ctx.fillRect(0, 0, canvas.width, canvas.height);
ctx.strokeStyle = 'black';
ctx.lineWidth = 3;
ctx.lineCap = 'round';
ctx.lineJoin = 'round';
console.log('Canvas initialized:', canvas.width, 'x', canvas.height);

// Update refresh rate display
const refreshRateSlider = document.getElementById('refreshRate');
const refreshRateDisplay = document.getElementById('refreshRateDisplay');

refreshRateSlider.addEventListener('input', function() {
    const value = parseInt(this.value);
    const minutes = Math.floor(value / 60);
    const seconds = value % 60;
    
    if (minutes > 0) {
        refreshRateDisplay.textContent = `${value}s (${minutes}m ${seconds}s)`;
    } else {
        refreshRateDisplay.textContent = `${value}s`;
    }
});

// Brush size control
const brushSizeSlider = document.getElementById('brushSize');
brushSizeSlider.addEventListener('input', function() {
    brushSize = parseInt(this.value);
    ctx.lineWidth = brushSize;
});

// Drawing functions
function getMousePos(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    };
}

function getTouchPos(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    return {
        x: (e.touches[0].clientX - rect.left) * scaleX,
        y: (e.touches[0].clientY - rect.top) * scaleY
    };
}

function startDrawing(pos) {
    isDrawing = true;
    ctx.lineWidth = brushSize;
    ctx.strokeStyle = 'black'; // Ensure black stroke
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    console.log('Started drawing at:', pos.x, pos.y, 'brush size:', brushSize);
}

function draw(pos) {
    if (!isDrawing) return;
    
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    console.log('Drawing to:', pos.x, pos.y);
}

function stopDrawing() {
    if (!isDrawing) return;
    isDrawing = false;
    ctx.beginPath();
}

// Mouse events
canvas.addEventListener('mousedown', (e) => {
    e.preventDefault();
    const pos = getMousePos(e);
    startDrawing(pos);
    // Draw a dot for single clicks
    ctx.fillStyle = 'black';
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, brushSize / 2, 0, Math.PI * 2);
    ctx.fill();
});

canvas.addEventListener('mousemove', (e) => {
    e.preventDefault();
    draw(getMousePos(e));
});

canvas.addEventListener('mouseup', (e) => {
    e.preventDefault();
    stopDrawing();
});

canvas.addEventListener('mouseout', (e) => {
    stopDrawing();
});

// Touch events
canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    const pos = getTouchPos(e);
    startDrawing(pos);
    // Draw a dot for single taps
    ctx.fillStyle = 'black';
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, brushSize / 2, 0, Math.PI * 2);
    ctx.fill();
});

canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    draw(getTouchPos(e));
});

canvas.addEventListener('touchend', (e) => {
    e.preventDefault();
    stopDrawing();
});

// Utility functions
function clearCanvas() {
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'black'; // Reset stroke style
    ctx.lineWidth = brushSize; // Reset line width
    updateStatus('Canvas cleared', 'success');
    console.log('Canvas cleared and reset');
}

function testDraw() {
    // Draw a test line to verify canvas is working
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(50, 50);
    ctx.lineTo(150, 150);
    ctx.stroke();
    console.log('Test line drawn');
}

function updateStatus(message, type = '') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = 'status ' + type;
}

function showPreview(imageUrl) {
    const preview = document.getElementById('preview');
    const previewImage = document.getElementById('previewImage');
    
    previewImage.src = imageUrl;
    preview.style.display = 'block';
}

// API functions
async function sendTextMessage() {
    const message = document.getElementById('textMessage').value.trim();
    const deviceId = document.getElementById('deviceId').value.trim();
    
    if (!message) {
        updateStatus('Please enter a message', 'error');
        return;
    }
    
    if (!deviceId) {
        updateStatus('Please enter a device ID', 'error');
        return;
    }
    
    updateStatus('Sending text message...', '');
    
    try {
        const response = await fetch('/api/screens', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'id': deviceId
            },
            body: JSON.stringify({
                content: message,
                content_type: 'big_text',
                width: 800,
                height: 480,
                filename: `text-message-${Date.now()}`
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        updateStatus('Text message sent successfully!', 'success');
        showPreview(result.image_url);
        
        // Update the device's refresh rate if changed
        await updateRefreshRate(deviceId);
        
    } catch (error) {
        console.error('Error sending text message:', error);
        updateStatus(`Error: ${error.message}`, 'error');
    }
}

async function sendDrawing() {
    const deviceId = document.getElementById('deviceId').value.trim();
    
    if (!deviceId) {
        updateStatus('Please enter a device ID', 'error');
        return;
    }
    
    updateStatus('Converting drawing to image...', '');
    
    try {
        // Convert canvas to blob
        canvas.toBlob(async (blob) => {
            // Convert to base64 for sending as HTML with embedded image
            const reader = new FileReader();
            reader.onload = async function() {
                try {
                    const base64 = reader.result;
                    
                    // Create HTML with the image
                    const htmlContent = `
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <style>
                                body { margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
                                img { max-width: 100%; max-height: 100%; }
                            </style>
                        </head>
                        <body>
                            <img src="${base64}" alt="Drawing">
                        </body>
                        </html>
                    `;
                    
                    const response = await fetch('/api/screens', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'id': deviceId
                        },
                        body: JSON.stringify({
                            content: htmlContent,
                            content_type: 'html',
                            width: 800,
                            height: 480,
                            filename: `drawing-${Date.now()}`
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const result = await response.json();
                    updateStatus('Drawing sent successfully!', 'success');
                    showPreview(result.image_url);
                    
                    // Update the device's refresh rate if changed
                    await updateRefreshRate(deviceId);
                    
                } catch (error) {
                    console.error('Error sending drawing:', error);
                    updateStatus(`Error: ${error.message}`, 'error');
                }
            };
            
            reader.readAsDataURL(blob);
        }, 'image/png');
        
    } catch (error) {
        console.error('Error converting canvas:', error);
        updateStatus(`Error: ${error.message}`, 'error');
    }
}

async function updateRefreshRate(deviceId) {
    const refreshRate = document.getElementById('refreshRate').value;
    
    try {
        const response = await fetch('/api/refresh_rate', {
            method: 'POST',
            headers: {
                'id': deviceId,
                'Refresh-Rate': refreshRate
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log(`Refresh rate updated: ${result.message}`);
        
    } catch (error) {
        console.warn('Could not update refresh rate:', error);
    }
}

// Initialize
updateStatus('Ready to send content to your TRMNL device', '');
ctx.lineWidth = brushSize;