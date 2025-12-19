#!/bin/bash

# Simple script to get ngrok URL after starting ngrok
# Usage: After running "ngrok http 8000", run this script in another terminal

echo "Fetching ngrok public URL..."
sleep 2

URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); tunnels=d.get('tunnels',[]); print(tunnels[0]['public_url'] if tunnels else '')" 2>/dev/null)

if [ -z "$URL" ]; then
    echo "❌ Could not get ngrok URL. Make sure ngrok is running:"
    echo "   Run: ngrok http 8000"
    echo ""
    echo "   Then open http://127.0.0.1:4040 in your browser to see the URL"
else
    echo ""
    echo "=========================================="
    echo "✅ NGROK PUBLIC URL"
    echo "=========================================="
    echo "Public URL: $URL"
    echo "API Base:   $URL/api/"
    echo ""
    echo "Share this with your frontend team:"
    echo "  $URL"
    echo ""
    echo "Example API endpoints:"
    echo "  - Get slots: $URL/api/slots/?date=2024-01-15"
    echo "  - Create booking: $URL/api/bookings/"
    echo "=========================================="
    echo ""
fi


