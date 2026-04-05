# DDOS_F16 SCANWEBS v6.0 — Intelligence Platform

## 🔧 System Requirements
- Python 3.10+
- System tools: `dig`, `whois`, `openssl`, `curl`

## 🚀 Quick Start (Local)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system tools (Ubuntu/Debian)
sudo apt install dnsutils whois openssl curl

# Run the server
python app.py
```

Open `http://localhost:5000` in your browser.

---

## ☁️ Deploy to Render.com (FREE)

### Step 1: Create GitHub Repository
```bash
git init
git add .
git commit -m "DDOS_F16 SCANWEBS v6.0"
git remote add origin https://github.com/YOUR_USERNAME/ddos-f16-scanwebs.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) → Sign up (free)
2. Click **New** → **Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Runtime**: Docker
   - **Plan**: Free
5. Click **Create Web Service**

Your site will be live at: `https://ddos-f16-scanwebs.onrender.com`

---

## 🐳 Deploy with Docker

```bash
# Build
docker build -t ddos-f16-scanwebs .

# Run
docker run -p 5000:5000 ddos-f16-scanwebs
```

---

## 📁 Project Structure

```
ddos-f16-deploy/
├── app.py              # Flask server + Scanner engine
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container config
├── Procfile            # Render/Heroku process config
├── render.yaml         # Render.com deployment config
├── README.md           # This file
└── static/
    ├── index.html      # Main HTML page
    ├── styles.css      # Military HUD theme
    └── script.js       # Frontend scanner engine
```

## 🔒 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main interface |
| GET | `/api/health` | Health check |
| POST | `/api/scan` | Run scan module |

### POST /api/scan
```json
{
  "domain": "example.com",
  "module": "dns"
}
```

Available modules: `dns`, `subdomains`, `whois`, `headers`, `ssl`, `tech`, `ports`, `security`, `reverse_dns`, `geo`, `robots`
