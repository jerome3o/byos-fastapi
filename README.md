# TRMNL Custom FastAPI Server

A custom FastAPI server implementation for TRMNL e-ink devices, providing full API compatibility with the original TRMNL service while offering programmatic control and customization.

## Features

- **Full TRMNL API Compatibility**: Compatible with existing TRMNL devices
- **Programmatic Control**: Simple `create_image()` function for easy display updates
- **Automatic Scheduling**: Built-in support for periodic content updates
- **Device Management**: Complete device provisioning and status tracking
- **Image Generation**: Automatic conversion to proper e-ink formats (PNG/BMP3)
- **Docker Ready**: Easy deployment with Docker and Docker Compose
- **Comprehensive Testing**: Full test suite included

## Quick Start

### Using Docker (Recommended)

1. **Clone and build**:
   ```bash
   cd byos-fastapi
   docker-compose up --build
   ```

2. **Server will be available at**: `http://localhost:8000`

### Manual Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install ImageMagick** (for image processing):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install imagemagick
   
   # macOS
   brew install imagemagick
   ```

3. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Using the Programmatic Interface

The main feature you're looking for - easy programmatic control:

```python
from app.trmnl_control import create_image

# Simple text display
create_image("Hello World!")

# System status example
status = f'''
System Dashboard

Date: {datetime.now().strftime('%Y-%m-%d')}
Time: {datetime.now().strftime('%H:%M:%S')}

CPU: 45%
Memory: 2.1GB / 8GB
Disk: 250GB free

Server Status: Online
'''
create_image(status)

# For scheduled updates
from app.trmnl_control import schedule_updates

def get_current_data():
    return f"Current time: {datetime.now()}"

schedule_updates(get_current_data, interval_minutes=30)
```

## Device Configuration

### Point Your TRMNL Device to This Server

1. **Find your server's IP address**:
   ```bash
   # If running locally
   http://YOUR_LOCAL_IP:8000
   
   # If deployed
   https://your-domain.com
   ```

2. **Configure device**: Set your TRMNL device to point to your server's `/api/display` endpoint

3. **Device will auto-provision**: On first connection, device will be automatically set up with API credentials

## API Endpoints

### Core Device Endpoints

- `GET /api/display` - Main device endpoint for screen content
- `POST /api/setup` - Device provisioning 
- `POST /api/log` - Device telemetry collection
- `POST /api/screens` - Programmatic screen creation
- `GET /api/current_screen` - Current screen without playlist advancement
- `POST /api/refresh_rate` - Set refresh rate for specific device

### Management Endpoints

- `GET /` - Web frontend interface
- `GET /status` - Server status and information

## cURL Examples for Testing & Debugging

### Device Simulation

Test your server by simulating TRMNL device requests:

```bash
# Device MAC address for testing
DEVICE_MAC="TEST_DEVICE_01"

# 1. Device setup (first time connection)
curl -X POST "http://localhost:8000/api/setup" \
  -H "id: $DEVICE_MAC" \
  -H "FW-Version: 1.5.2" \
  -v

# 2. Get display content (what device fetches for screen updates)
curl -X GET "http://localhost:8000/api/display" \
  -H "id: $DEVICE_MAC" \
  -H "Battery-Voltage: 3.7" \
  -H "FW-Version: 1.5.2" \
  -H "RSSI: -45" \
  -v

# 3. Submit device logs/telemetry
curl -X POST "http://localhost:8000/api/log" \
  -H "id: $DEVICE_MAC" \
  -H "Content-Type: application/json" \
  -d '{
    "firmware_version": "1.5.2",
    "battery_voltage": 3.7,
    "wifi_ssid": "MyWiFi",
    "rssi": -45,
    "free_heap": 45000,
    "min_free_heap": 40000,
    "max_alloc_heap": 35000
  }' \
  -v

# 4. Check current screen without advancing playlists
curl -X GET "http://localhost:8000/api/current_screen" \
  -H "id: $DEVICE_MAC" \
  -v
```

### Content Creation

Send content programmatically to your device:

```bash
# Send big text message (maximum screen coverage)
curl -X POST "http://localhost:8000/api/screens" \
  -H "id: $DEVICE_MAC" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "BIG TEXT!",
    "content_type": "big_text",
    "width": 800,
    "height": 480,
    "filename": "my-big-text"
  }' \
  -v

# Send regular text content
curl -X POST "http://localhost:8000/api/screens" \
  -H "id: $DEVICE_MAC" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello World!\nThis is a test message.\n\nCurrent time: $(date)",
    "content_type": "text",
    "width": 800,
    "height": 480,
    "filename": "hello-world-test"
  }' \
  -v

# Send HTML content
curl -X POST "http://localhost:8000/api/screens" \
  -H "id: $DEVICE_MAC" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "<html><body><h1>HTML Test</h1><p>This is HTML content rendered to image.</p></body></html>",
    "content_type": "html",
    "width": 800,
    "height": 480,
    "filename": "html-test"
  }' \
  -v
```

### Device Configuration

```bash
# Set refresh rate for device (in seconds)
curl -X POST "http://localhost:8000/api/refresh_rate" \
  -H "id: $DEVICE_MAC" \
  -H "Refresh-Rate: 300" \
  -v

# Set longer refresh rate (30 minutes)
curl -X POST "http://localhost:8000/api/refresh_rate" \
  -H "id: $DEVICE_MAC" \
  -H "Refresh-Rate: 1800" \
  -v
```

### Server Status

```bash
# Check server status
curl -X GET "http://localhost:8000/status" -v

# Access web frontend
curl -X GET "http://localhost:8000/" -v
```

### Testing Complete Device Flow

Simulate the complete device lifecycle:

```bash
#!/bin/bash
DEVICE_MAC="TEST_DEVICE_$(date +%s)"

echo "=== Testing Complete Device Flow ==="
echo "Device MAC: $DEVICE_MAC"

echo -e "\n1. Device Setup (First Boot)"
curl -s -X POST "http://localhost:8000/api/setup" \
  -H "id: $DEVICE_MAC" \
  -H "FW-Version: 1.5.2" | jq '.'

echo -e "\n2. Send Custom Content"
curl -s -X POST "http://localhost:8000/api/screens" \
  -H "id: $DEVICE_MAC" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"Test Device\\n$DEVICE_MAC\\n\\nTime: $(date)\",
    \"content_type\": \"big_text\",
    \"width\": 800,
    \"height\": 480,
    \"filename\": \"test-$(date +%s)\"
  }" | jq '.'

echo -e "\n3. Device Fetch Content"
curl -s -X GET "http://localhost:8000/api/display" \
  -H "id: $DEVICE_MAC" \
  -H "Battery-Voltage: 3.7" \
  -H "FW-Version: 1.5.2" | jq '.'

echo -e "\n4. Device Submit Logs"
curl -s -X POST "http://localhost:8000/api/log" \
  -H "id: $DEVICE_MAC" \
  -H "Content-Type: application/json" \
  -d '{
    "firmware_version": "1.5.2",
    "battery_voltage": 3.7,
    "wifi_ssid": "TestWiFi",
    "rssi": -45,
    "free_heap": 45000,
    "min_free_heap": 40000,
    "max_alloc_heap": 35000
  }' | jq '.'

echo -e "\n=== Flow Complete ==="
```

### Debug Response Headers

Add `-i` flag to see response headers:

```bash
# See all response headers and timing
curl -X GET "http://localhost:8000/api/display" \
  -H "id: TEST_DEVICE" \
  -H "Battery-Voltage: 3.7" \
  -i -v
```

### Verify Generated Images

```bash
# List generated images
curl -s "http://localhost:8000/static/images/" | grep -o 'href="[^"]*\.png"' | sed 's/href="//g' | sed 's/"//g'

# Download a specific image
curl -o test-image.png "http://localhost:8000/static/images/your-filename.png"
```

## Image Requirements

- **Resolution**: 800x480 pixels
- **Format**: PNG (1-bit monochrome) for FW >= 1.5.2, BMP3 for older firmware
- **Colors**: Black and white only
- **Size**: ~1.6KB for PNG, ~48KB for BMP3

Images are automatically converted to the proper format when using `create_image()`.

## Example Usage Scripts

Run the included examples:

```bash
# Basic examples
python example_usage.py

# This will create several demo images showing different use cases
```

## Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v
```

## Development

### Project Structure

```
byos-fastapi/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── database.py          # SQLite database layer
│   ├── image_utils.py       # Image generation utilities
│   └── trmnl_control.py     # Programmatic control interface
├── tests/                   # Test suite
├── static/images/           # Generated images (created at runtime)
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── example_usage.py        # Usage examples
```

### Adding Custom Features

1. **Custom image generators**: Extend `ImageGenerator` class in `image_utils.py`
2. **Additional endpoints**: Add routes to `main.py`
3. **Database models**: Extend models in `database.py`
4. **Scheduled tasks**: Use the `schedule_updates()` function

## Configuration

### Environment Variables

- `PYTHONPATH`: Set to `/app` in Docker
- `PYTHONUNBUFFERED`: Set to `1` for better logging

### Database

- Uses SQLite by default (`trmnl.db`)
- Stores device credentials and telemetry
- Automatically created on first run

### Image Storage

- Images stored in `static/images/`
- Served via FastAPI static file serving
- Automatic cleanup can be implemented as needed

## Security Considerations

- API keys are auto-generated (32 characters)
- Device authentication via MAC address + API key
- Consider adding rate limiting for production use
- Use HTTPS in production

## Troubleshooting

### Common Issues

1. **ImageMagick not found**: Install ImageMagick system package
2. **Permission errors**: Ensure write access to `static/images/` directory
3. **Device connection issues**: Check firewall settings and ensure port 8000 is accessible

### Logs

View server logs:
```bash
# Docker
docker-compose logs -f

# Manual
# Logs printed to console when running with --reload
```

## Production Deployment

### Docker Deployment

1. **Build and run**:
   ```bash
   docker-compose up -d
   ```

2. **Behind reverse proxy** (nginx/traefik):
   ```nginx
   location / {
       proxy_pass http://localhost:8000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

### Scaling

- Stateless design allows horizontal scaling
- Database can be moved to PostgreSQL/MySQL for multi-instance deployments
- Consider Redis for shared session/cache if needed

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## License

This implementation is provided as-is for educational and personal use. Ensure compliance with TRMNL's terms of service when using with their hardware.

---

## Quick Reference

**Start server**: `docker-compose up`  
**Create image**: `create_image("Your content here")`  
**Schedule updates**: `schedule_updates(your_function, 30)`  
**Run tests**: `pytest tests/ -v`  
**View API docs**: `http://localhost:8000/docs`