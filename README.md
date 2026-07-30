# DistaMate — AI Workspace Assistant

> An intelligent, personal AI assistant for Gmail, Google Drive, Docs & Sheets — powered by OpenRouter AI.

## Features

- 📧 **Email Review & Drafting** — AI-powered priority classification, thread summaries, and context-aware reply drafts
- 📄 **Document Analysis** — Extract summaries, key points, action items, people, and deadlines from Google Docs
- 📊 **Spreadsheet Intelligence** — View, analyze, and update Google Sheets with AI insights and formula suggestions
- 🗂️ **Drive Browser** — Navigate folders, search with AI-reformulated queries, and create new Docs/Sheets
- 💬 **AI Chat** — Streaming chat assistant with full workspace context awareness

---

## Quick Start

### Option 1: Demo Mode (No setup needed)
1. Open a terminal in this folder
2. Run: `npx serve .` (or `python -m http.server 8080`)
3. Open `http://localhost:3000` in your browser
4. Click "Sign in with Google" → you'll be prompted to configure your Client ID
5. Skip and use **Demo Mode** to explore the UI with sample data

### Option 2: Live Google Workspace (Full integration)

#### Step 1: Get a Google Cloud OAuth2 Client ID
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable these APIs:
   - Gmail API
   - Google Drive API
   - Google Docs API
   - Google Sheets API
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Choose **Web Application**
6. Add your serving URL to **Authorized JavaScript Origins** (e.g. `http://localhost:3000`)
7. Copy the **Client ID**

#### Step 2: Serve the app
```bash
# Using npx (no install needed)
npx serve .

# Or Python
python -m http.server 8080

# Or Node.js http-server
npx http-server . -p 8080
```

> ⚠️ **Important**: Google OAuth requires an HTTP(S) origin. `file://` URLs won't work. Use a local server.

#### Step 3: Configure in DistaMate
1. Open the app in your browser
2. Click **Sign in with Google** → the Settings panel will prompt you if no Client ID is set
3. Go to **Settings** → paste your Google Client ID → click **Save & Re-authenticate**
4. Sign in with your Google account
5. Done! Your live Gmail, Drive, Docs, and Sheets are now connected.

---

## AI Configuration

DistaMate uses **OpenRouter** to access AI models. Your API key is pre-configured, but you can change it:

1. Go to **Settings → AI Engine**
2. Update the API key or select a different model
3. Click **Test AI** to verify it works

### Supported Models
| Model | Speed | Quality | Cost |
|-------|-------|---------|------|
| GPT-4o Mini | ⚡ Fast | ⭐⭐⭐⭐ | Low |
| GPT-4o | Moderate | ⭐⭐⭐⭐⭐ | Medium |
| Claude 3.5 Sonnet | Moderate | ⭐⭐⭐⭐⭐ | Medium |
| Claude 3 Haiku | ⚡ Fastest | ⭐⭐⭐ | Very Low |
| Llama 3.1 8B | Fast | ⭐⭐⭐ | Free |

---

## File Structure

```
DistaMate/
├── index.html              # App shell
├── styles/
│   ├── main.css            # Design system
│   └── components.css      # Component styles
├── js/
│   ├── app.js              # Router & main init
│   ├── config.js           # API keys & settings
│   ├── auth.js             # Google OAuth2
│   ├── ai.js               # OpenRouter AI wrapper
│   ├── gmail.js            # Gmail API wrapper
│   ├── drive.js            # Drive API wrapper
│   ├── docs.js             # Docs API wrapper
│   ├── sheets.js           # Sheets API wrapper
│   ├── ui.js               # Toast, modal, helpers
│   ├── demo-data.js        # Demo mode sample data
│   └── components/
│       ├── dashboard.js    # Dashboard panel
│       ├── email-panel.js  # Email panel
│       ├── drive-panel.js  # Drive panel
│       ├── doc-panel.js    # Documents panel
│       ├── sheets-panel.js # Sheets panel
│       ├── settings-panel.js # Settings panel
│       └── chat.js         # AI Chat (streaming)
└── README.md
```

---

## Privacy & Security

- **No backend** — 100% client-side application
- **No data storage** — API keys stored in browser `localStorage` only
- **No telemetry** — No analytics or tracking
- All requests go directly from your browser to Google APIs and OpenRouter

---

## Behavioral Guidelines

- DistaMate **never sends emails automatically** — always requires explicit user confirmation
- **Destructive actions** (cell updates, sends) require a confirmation modal
- **Demo mode** uses realistic sample data to demonstrate all features without real account access
