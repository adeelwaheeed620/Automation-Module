# 🧠 Automation Task Executor

This module connects to a backend via WebSocket, listens for task instructions, executes browser-based automation using a GoLogin profile, and returns structured results.

---

## 📁 Files Included

| File | Description |
|------|-------------|
| `websocket_listener.py` | Main automation engine. Connects via WebSocket, executes tasks, and sends back results. |
| `config.json` | Configuration for backend WebSocket URL and GoLogin API token. |

---

## ⚙️ Configuration

Edit `config.json` before running:

```json
{
  "websocket_url": "ws://your-backend-server.com/ws/tasks",
  "api_token": "your-gologin-api-token"
}


🚀 Running the Automation:
python websocket_listener.py


🧩 Features
Maintains a persistent WebSocket connection with your backend.

Listens for incoming tasks (as JSON).

Launches GoLogin browser profiles with proper fingerprinting and proxy.

Executes:

fill: types into input fields.

click: clicks buttons or links.

select: selects dropdown values.

extract: fetches result data (e.g. QR code, text, image).

Detects and returns results with proper status codes:

PAYMENT_SUCCESS

LOGIN_FAILED

PROXY_EXPIRED

ACCOUNT_EXPIRED

PAYMENT_FAILED

Posts results to callback_url if provided in the task JSON.

🔐 GoLogin Setup
Make sure the GoLogin app is installed and running.

You must have existing profiles created (e.g. via Module 1).

Insert your api_token in config.json.

📤 Task JSON Format (Example)
json
Copy
Edit
{
  "orderId": "xyz123",
  "profile_id": "685a244d9749c83b5f2c53a3",
  "url": "https://example.com/payment",
  "actions": [
    { "action": "fill", "selector": "#amount", "value": "10" },
    { "action": "click", "selector": "#submit" }
  ],
  "result_selector": "#qrCode img",
  "paymentMethod": "Alipay",
  "amount": 10,
  "callback_url": "https://your-backend.com/api/result"
}
📌 Notes
If callback_url is missing, results are printed to console.

Handles task failures gracefully and returns specific error statuses.

Designed for long-term, unattended operation.

