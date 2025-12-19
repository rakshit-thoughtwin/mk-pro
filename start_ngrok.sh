#!/bin/bash

# Ngrok Startup Script for Django API
# Make sure you've configured your authtoken first!

NGROK_BIN="/tmp/ngrok"
PORT=8000

# Check if ngrok exists
if [ ! -f "$NGROK_BIN" ]; then
    echo "Error: ngrok not found at $NGROK_BIN"
    exit 1
fi

# Check if Django server is running on port 8000
if ! lsof -ti:$PORT > /dev/null 2>&1; then
    echo "Warning: Django server doesn't seem to be running on port $PORT"
    echo "Start it with: python manage.py runserver 0.0.0.0:$PORT"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Kill any existing ngrok processes
pkill -f "ngrok http" 2>/dev/null
sleep 1

echo "Starting ngrok tunnel on port $PORT..."
$NGROK_BIN http $PORT > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok to start
echo "Waiting for ngrok to initialize..."
sleep 5

# Get the public URL
PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); tunnels=d.get('tunnels',[]); print(tunnels[0]['public_url'] if tunnels else '')" 2>/dev/null)

if [ -z "$PUBLIC_URL" ]; then
    echo "Error: Could not retrieve ngrok URL. Check /tmp/ngrok.log for details."
    echo "Make sure you've configured your authtoken: $NGROK_BIN config add-authtoken YOUR_TOKEN"
    cat /tmp/ngrok.log | tail -10
    kill $NGROK_PID 2>/dev/null
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Ngrok is running!"
echo "=========================================="
echo "Public URL: $PUBLIC_URL"
echo "API Base URL: $PUBLIC_URL/api/"
echo ""
echo "Share this URL with your frontend team:"
echo "  $PUBLIC_URL"
echo ""
echo "Web Interface: http://127.0.0.1:4040"
echo "Logs: /tmp/ngrok.log"
echo "Process ID: $NGROK_PID"
echo ""
echo "To stop ngrok, run: pkill -f 'ngrok http'"
echo "=========================================="


