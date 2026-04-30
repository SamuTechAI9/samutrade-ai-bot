# SamuTrade AI Bot 🤖

> AI Telegram bot for international trade. Qualifies B2B leads in their own language so I only handle the serious ones.

**🔗 Live demo:** [@SamuTradeAI_bot on Telegram](https://t.me/SamuTradeAI_bot)

---

## 🎯 What it does

SamuTrade is an AI sales assistant for an international trade business. It engages with potential B2B clients on Telegram, detects their language, qualifies the lead through natural conversation, and prepares a structured handoff for the human agent (Samuel) to close the deal.

Unlike a typical chatbot, this assistant **does not invent prices, stock or commitments**. It is a qualification layer — it gathers what the human needs to know, in the client's own language.

---

## 💡 Why this exists

Running an import-export brokerage means handling first-contact conversations across multiple languages, time zones and product categories — from Shacman trucks for Senegal to watermelons from Morocco. Most leads are not serious. Filtering them manually is exhausting.

This bot handles the first conversation 24/7, gathers the structured data needed (product, volume, destination, urgency, budget) and lets me focus only on real opportunities.

---

## 🛠️ Tech stack

- **Python 3.12** + **Flask** — webhook server
- **Azure OpenAI** (`gpt-4o-mini` deployment) — conversation engine
- **Telegram Bot API** — public messaging channel
- **Azure App Service** (Linux, B1) — production hosting
- **gunicorn** — WSGI server

---

## 🏗️ Architecture

```text
Client (Telegram user)
        ↓
Telegram Bot API
        ↓
Azure App Service (Flask + gunicorn)
        ↓
Azure OpenAI (gpt-4o-mini)
        ↓
Response back to user
```

The Flask app exposes `/telegram-webhook`. Telegram pushes every incoming message to this endpoint. The handler:

1. Extracts `chat_id` and `text` from the update
2. Maintains per-chat conversation history in memory
3. Calls Azure OpenAI twice: one for lead-data extraction (JSON), one for the natural reply
4. Sends the reply back via `sendMessage` to the same `chat_id`

---

## ✨ Features

- 🌍 **Multilingual** — auto-detects and responds in Spanish, English, French, Portuguese, Arabic, etc.
- 🎯 **Lead qualification** — gathers name, country, product, volume, destination, urgency
- 💬 **One question at a time** — WhatsApp-style short messages, never form-like
- 🛡️ **Honest by design** — never invents prices or commitments; redirects to human quote
- 🔒 **Per-session memory** — keeps context within a conversation by `chat_id`
- 📊 **Structured handoff** — when enough data is gathered, generates a lead summary

---

## 📸 Screenshots

**Live conversation: language switch mid-chat**
The bot detects the language change from Spanish to English and adapts naturally.

![Live conversation showing multilingual switch](docs/screenshots/conversation-multilang.png)

**Production logs: Azure App Service**
Real-time logs from the deployed bot processing the conversation above.

![Azure App Service production logs](docs/screenshots/azure-logs.png)

---

## 🚀 Setup (local)

```bash
# Clone the repo
git clone https://github.com/SamuTechAI9/samutrade-ai-bot.git
cd samutrade-ai-bot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
.venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create your own .env)
# AZURE_OPENAI_ENDPOINT=...
# AZURE_OPENAI_API_KEY=...
# AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
# TELEGRAM_BOT_TOKEN=...

# Run the server
python server_telegram.py
```

To receive Telegram messages, expose your local server (e.g. with ngrok) and register the webhook:

```
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<YOUR_PUBLIC_URL>/telegram-webhook
```

---

## 📍 Status & roadmap

**Current**
- ✅ Bot live in production on Azure
- ✅ Multilingual conversation working
- ✅ Lead extraction and qualification logic
- ✅ Public access via [t.me/SamuTradeAI_bot](https://t.me/SamuTradeAI_bot)

**Next**
- ⏳ Refactor to `src/` and `docs/` folder structure
- ⏳ Persistent lead storage (Azure Cosmos DB or SQLite)
- ⏳ Notification system to forward qualified leads to human agent
- ⏳ Dashboard to review and manage incoming leads
- ⏳ Migration to WhatsApp Business API once company is registered

---

## 📂 Project structure note

You'll find two server files in this repo:

- `server_telegram.py` — **the active one**, running in production with Telegram Bot API.
- `server.py` — the original WhatsApp/Twilio version. Kept as historical reference: the project started on WhatsApp via Twilio, then pivoted to Telegram once Meta business verification became a blocker without a registered company.

The Telegram version is what's currently deployed and what the live demo points to.

---

## 👤 About

Built by **Samuel Torres Nebro**
International trader moving into AI and cloud development.
I like building real things, breaking them, fixing them, and making them work in production.

📍 Trondheim, Norway
🔗 [LinkedIn](https://www.linkedin.com/in/samuel-torres-0a882b292)
📧 samueltorresSORSER@gmail.com

---

## 📄 License

MIT — feel free to fork and adapt.
