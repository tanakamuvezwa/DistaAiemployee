# 🤖 DISTA AI — Personal Workspace Assistant

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Ftanakamuvezwa%2FDistaAiemployee)

A personal AI assistant featuring an interactive pixel-art humanoid avatar, dynamic audio waveform visualizer, out-loud speech synthesis, real Gmail integration, and local/serverless AI models.

---

## 🌟 Key Features

- **🤖 Pixel-Art Humanoid Avatar**: Custom 20x20 matrix robot avatar with glowing orange ring and state animations.
- **🌊 Dynamic Audio Waveform**: Real-time frequency bars pulsating in orange (`#FF6B00`) & white.
- **🔑 Flexible AI Providers**: Zero-config free G4F (GPT-4o, Llama 3.3, DeepSeek) + OpenRouter / Gemini API support.
- **📧 Real Gmail Service**: IMAP email monitoring & SMTP real email transmission.
- **💾 Persistence**: Automatic MongoDB cloud/local database & SQLite fallback.
- **☁️ Vercel Ready**: Out-of-the-box serverless deployment configuration (`vercel.json` & `@vercel/python`).

---

## 🚀 Deploying to Vercel

### Option 1: One-Click Deploy
Click the button below to deploy your own instance of Dista AI on Vercel:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Ftanakamuvezwa%2FDistaAiemployee)

### Option 2: Vercel CLI
```bash
npm install -g vercel
vercel
```

---

## 💻 Running Locally

### 1. Web Application (Zero Dependencies Required)
```bash
python app_web.py
```
Open **[http://localhost:5050](http://localhost:5050)** in your browser.

### 2. Desktop Window Application (PyQt6)
```bash
python dista_app.py
```

---

## 📄 License
MIT License
