# 🏗️ Material Shop — Telegram Mini App (FaaS)

ហាងលក់សម្ភារៈក្នុង Telegram ដែលបង្កើតដោយ FaaS (Function as a Service) Architecture។

## 📁 Project Structure

```
📦 project/
├── 📂 api/                    ← FaaS Functions (Python)
│   ├── products.py            ← Function #1: GET  /api/products
│   └── orders.py              ← Function #2: POST /api/orders
│
├── 📂 public/
│   └── index.html             ← Telegram Mini App UI
│
├── vercel.json                ← Deployment routing config
├── requirements.txt           ← Python libraries
└── .env.example               ← Environment variables template
```

## 🚀 How to Deploy (No command line needed!)

### Step 1 — Upload to GitHub
1. Download **GitHub Desktop** → [desktop.github.com](https://desktop.github.com)
2. Sign in → **"Add Existing Repository"** → choose this folder
3. Click **"Publish Repository"** → Done ✅

### Step 2 — Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) → Sign in with GitHub
2. Click **"Add New Project"** → import this repository
3. Go to **Settings → Environment Variables** → add your keys:
   - `GOOGLE_SERVICE_ACCOUNT_JSON`
   - `GOOGLE_SHEET_ID`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Click **Deploy** → Done ✅

### Step 3 — Connect to Telegram Bot
1. Open **BotFather** in Telegram → `/newbot`
2. After creating → `/mybots` → your bot → **Bot Settings** → **Menu Button**
3. Paste your Vercel URL → Save

## 📊 Google Sheets Setup
See `GOOGLE_SHEETS_SETUP.md` for step-by-step instructions.

## 🔑 Environment Variables
Copy `.env.example` to `.env` and fill in your values.
