"""
═══════════════════════════════════════════════════════════
  FaaS Function #1  —  GET /api/products
═══════════════════════════════════════════════════════════

  What is FaaS?
  → Function as a Service = cloud runs your function ONLY
    when someone calls it. No server to manage. No cost
    when idle. Perfect for small apps like this!

  This function's only job:
  → Return the product list from Google Sheets as JSON.
═══════════════════════════════════════════════════════════
"""

import json
import os
import gspread
from google.oauth2.service_account import Credentials
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Vercel calls this class automatically on every GET request."""

    def do_GET(self):
        products = get_products_from_sheet()
        self._send_json(200, {"status": "ok", "data": products})

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
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


# ── business logic ────────────────────────────────────────
def get_products_from_sheet():
    """Read all rows from the 'Products' sheet and return as list."""
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    sheet_id   = os.environ.get("GOOGLE_SHEET_ID")

    if creds_json and sheet_id:
        try:
            creds  = Credentials.from_service_account_info(
                json.loads(creds_json),
                scopes=["https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"]
            )
            client    = gspread.authorize(creds)
            worksheet = client.open_by_key(sheet_id).worksheet("Products")
            return worksheet.get_all_records()   # ← reads your Google Sheet!
        except Exception as e:
            print(f"[products] Google Sheets error: {e}")

    # ── Demo / mock data (shown when env vars are not set) ──
    return [
        {"id": "1", "name": "ស៊ីម៉ង់ត៍ Premium (50kg)",  "price": 6.50,
         "description": "ស៊ីម៉ង់ត៍គ្រឿងសំណង់គុណភាពខ្ពស់",
         "image_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600"},
        {"id": "2", "name": "ដែកគ្រឿង (12mm)",            "price": 4.20,
         "description": "ដែករឹងសំរាប់ការសំណង់",
         "image_url": "https://images.unsplash.com/photo-1532522714522-8c9df4ecf55a?w=600"},
        {"id": "3", "name": "ក្បឿងក្រាប (60x60)",          "price": 12.00,
         "description": "ក្បឿងស្អាតសម្រាប់ជាន់ក្នុងផ្ទះ",
         "image_url": "https://images.unsplash.com/photo-1523413555809-0fb1d4dfbf3f?w=600"},
        {"id": "4", "name": "ថ្នាំលាបពណ៌ស (20L)",          "price": 45.00,
         "description": "ថ្នាំលាបពណ៌ប្រើបានទាំងខាងក្នុង-ក្រៅ",
         "image_url": "https://images.unsplash.com/photo-1562259929-b4e1fd3aef09?w=600"},
    ]
