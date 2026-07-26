"""
═══════════════════════════════════════════════════════════
  FaaS Function #2  —  POST /api/orders
═══════════════════════════════════════════════════════════

  This function's only job:
  1. Save the customer's order to the 'Orders' Google Sheet.
  2. Send a Telegram notification to the shop owner.

  It is 100% independent from products.py.
  → That's the FaaS principle: one function = one job.
═══════════════════════════════════════════════════════════
"""

import json
import os
import gspread
from google.oauth2.service_account import Credentials
from http.server import BaseHTTPRequestHandler
import requests as http


class handler(BaseHTTPRequestHandler):
    """Vercel calls this class automatically on every POST request."""

    def do_POST(self):
        # Read body
        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length) or b"{}")

        user_name    = body.get("user_name", "Unknown")
        user_id      = body.get("user_id",   "N/A")
        phone        = body.get("phone",      "")
        address      = body.get("address",    "")
        items        = body.get("items",      [])
        total_amount = body.get("total_amount", 0)

        if not phone or not address or not items:
            self._send_json(400, {"status": "error", "message": "Missing required fields"})
            return

        save_to_sheet(user_id, user_name, phone, address, items, total_amount)
        notify_telegram(user_name, user_id, phone, address, items, total_amount)

        self._send_json(200, {"status": "success", "message": "Order placed!"})

    def do_OPTIONS(self):   # CORS preflight
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    # ── helpers ──────────────────────────────────────────
    def _send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


# ── business logic ────────────────────────────────────────
def _get_sheet(worksheet_name):
    """Helper: return a gspread Worksheet or None."""
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    sheet_id   = os.environ.get("GOOGLE_SHEET_ID")
    if not creds_json or not sheet_id:
        return None
    try:
        creds = Credentials.from_service_account_info(
            json.loads(creds_json),
            scopes=["https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        return client.open_by_key(sheet_id).worksheet(worksheet_name)
    except Exception as e:
        print(f"[orders] Sheet error: {e}")
        return None


def save_to_sheet(user_id, user_name, phone, address, items, total_amount):
    """Append one row to the 'Orders' sheet."""
    ws = _get_sheet("Orders")
    if not ws:
        return
    items_text = ", ".join([f"{i['name']} x{i['quantity']}" for i in items])
    ws.append_row([user_id, user_name, phone, address, items_text, total_amount])


def notify_telegram(user_name, user_id, phone, address, items, total_amount):
    """Send a formatted order summary to the shop owner via Telegram Bot."""
    token   = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return

    lines = "\n".join([
        f"  • {i['name']} x{i['quantity']} — ${float(i['price'])*int(i['quantity']):.2f}"
        for i in items
    ])
    msg = (
        f"🛒 *ការកម្ម៉ង់ទំនិញថ្មី!*\n\n"
        f"👤 *អតិថិជន:* {user_name} (ID: {user_id})\n"
        f"📞 *ទូរស័ព្ទ:* {phone}\n"
        f"📍 *អាសយដ្ឋាន:* {address}\n\n"
        f"📦 *ទំនិញ:*\n{lines}\n\n"
        f"💰 *សរុប:* ${float(total_amount):.2f}"
    )
    try:
        http.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"},
            timeout=5,
        )
    except Exception as e:
        print(f"[orders] Telegram error: {e}")
