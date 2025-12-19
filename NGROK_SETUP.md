# Ngrok Setup Guide

Ngrok requires authentication to create public tunnels. Follow these steps:

## Step 1: Get Ngrok Authtoken

1. **Sign up for a free ngrok account**: https://dashboard.ngrok.com/signup
2. **Get your authtoken**: https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy your authtoken (it looks like: `2abc123def456ghi789jkl012mno345pq_6rStUvWxYz7AbCdEfGhIjKl`)

## Step 2: Configure Ngrok

Run this command with your authtoken:

```bash
/tmp/ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

Or if ngrok is in `/usr/local/bin/`:

```bash
/usr/local/bin/ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

## Step 3: Start Ngrok

Once configured, start ngrok:

```bash
/tmp/ngrok http 8000
```

Or in the background:

```bash
/tmp/ngrok http 8000 > /tmp/ngrok.log 2>&1 &
```

## Step 4: Get Your Public URL

After starting ngrok, you can get your public URL by:

1. **Via API** (after a few seconds):
   ```bash
   curl http://127.0.0.1:4040/api/tunnels | python3 -m json.tool
   ```
   Look for the `public_url` field.

2. **Via Web Interface**:
   Open http://127.0.0.1:4040 in your browser to see the ngrok dashboard with your public URL.

## Quick Start Script

After configuring your authtoken, you can use the provided script:

```bash
./start_ngrok.sh
```

This will start ngrok and display your public URL.

## Share with Frontend Team

Once ngrok is running, share the public URL (e.g., `https://abc123.ngrok-free.app`) with your frontend team.

**Base API URL for frontend**: `https://YOUR_NGROK_URL/api/`

Example endpoints:
- Get available slots: `https://YOUR_NGROK_URL/api/slots/?date=2024-01-15`
- Create booking: `https://YOUR_NGROK_URL/api/bookings/`


