# SamuTrade AI Bot 🤖
AI-powered WhatsApp sales agent built with Azure OpenAI and Twilio.  
Designed to automate lead qualification and scale customer acquisition.

## 🚀 Overview
This project is an intelligent WhatsApp bot designed to act as a commercial agent.  
It interacts with potential clients, qualifies leads, and gathers structured business information automatically.

## 📈 Business Impact
- Automates lead qualification via WhatsApp
- Reduces response time from minutes to seconds
- Converts conversations into structured sales data

## 💡 Features
- 📩 Receives WhatsApp messages via Twilio
- 🤖 Responds using Azure OpenAI (GPT models)
- 🧠 Qualifies leads (buyer / seller detection)
- 📊 Extracts and structures key commercial data
- 💬 Maintains natural, professional sales conversations
- 🗂 Stores lead data in structured format (JSON-ready)

## 🏗 Architecture
```
WhatsApp → Twilio → Flask (/webhook) → Azure OpenAI → Response
```

## 🛠 Tech Stack
- Python 3.12
- Flask + Gunicorn
- Twilio WhatsApp API
- Azure OpenAI (GPT-4.1-mini)
- Azure App Service (West Europe)
- REST webhook architecture
- Production-ready deployment (Azure App Service)

## ⚙️ Setup
1. Clone the repo
```bash
git clone https://github.com/SamuTechAI9/samutrade-ai-bot.git
cd samutrade-ai-bot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set environment variables
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

4. Run locally
```bash
gunicorn --bind=0.0.0.0:8000 server:app
```

## 📁 Project Structure
```
samutrade-ai-bot/
├── server.py          # Main Flask app + webhook logic
├── requirements.txt   # Dependencies
├── .gitignore         # Ignored files
└── README.md          # This file
```

## 🤖 How it works
1. Client sends a WhatsApp message
2. Twilio forwards it to `/webhook`
3. Flask processes the message
4. Azure OpenAI generates a professional sales response
5. Twilio delivers the response back to the client

## 📊 Lead Data Collected
- Name & contact info
- Buyer or seller profile
- Product & quantity
- Origin & destination country
- Budget & urgency
- Logistics problems

## 🚀 Deployment
Deployed on **Azure App Service** (Linux, Python 3.12)

## 🎥 Demo
![WhatsApp Demo](demo.gif)

## 👤 Author
**Samuel Torres** — AI & Cloud Developer (Azure)  
[LinkedIn](https://www.linkedin.com/in/samuel-torres-0a882b292) | [GitHub](https://github.com/SamuTechAI9)