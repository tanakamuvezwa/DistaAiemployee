import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import local Python backend tools
from dista_brain import DistaBrain
from dista_tools import EmailTool, DocsTool, MessagesTool

brain = DistaBrain()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DISTA AI — Local Workspace Assistant</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif; }
    body { background-color: #0F1017; color: #E2E8F0; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
    
    /* Phone Shell Container */
    .app-card {
      width: 100%;
      max-width: 420px;
      height: 820px;
      background-color: #0F1017;
      border: 2px solid #282B3D;
      border-radius: 36px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.8), 0 0 40px rgba(255,107,0,0.15);
      display: flex;
      flex-direction: column;
      padding: 24px 20px;
      position: relative;
      overflow: hidden;
    }

    /* Top Header Bar */
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .brand { font-size: 18px; font-weight: 800; letter-spacing: 1px; color: #FFF; }
    .brand span { color: #FF6B00; }
    .header-btn { width: 36px; height: 36px; border-radius: 18px; background: #1A1C28; border: 1px solid #282B3D; color: #8C94A8; display: flex; align-items: center; justify-content: center; font-size: 16px; cursor: pointer; }

    /* Center Avatar Box */
    .avatar-box { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 12px; margin-bottom: 16px; }
    .avatar-ring {
      width: 160px; height: 160px; border-radius: 50%;
      border: 2.5px solid #FF6B00;
      box-shadow: 0 0 25px rgba(255,107,0,0.4), inset 0 0 20px rgba(255,107,0,0.15);
      display: flex; align-items: center; justify-content: center;
      position: relative;
    }
    .pixel-avatar {
      width: 110px; height: 110px;
      background: radial-gradient(circle at 35% 35%, #D7DEEB, #A0A8B8);
      clip-path: polygon(25% 0%, 75% 0%, 100% 25%, 100% 75%, 75% 100%, 25% 100%, 0% 75%, 0% 25%);
      position: relative;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .pixel-eyes { display: flex; gap: 24px; margin-top: -10px; }
    .pixel-eye { width: 14px; height: 14px; background: #FF6B00; border-radius: 3px; box-shadow: 0 0 8px #FF6B00; }
    .pixel-mouth { width: 24px; height: 4px; background: #282C3A; margin-top: 14px; border-radius: 2px; }
    
    .greeting { font-size: 14px; font-weight: 600; color: #E2E8F0; max-width: 280px; line-height: 1.4; }

    /* Audio Waveform */
    .waveform { display: flex; align-items: center; justify-content: center; gap: 4px; height: 36px; }
    .wave-bar { width: 4px; height: 12px; background: #FF6B00; border-radius: 2px; transition: height 0.15s ease; }
    .wave-bar.white { background: #FFFFFF; }

    /* Tool Grid (2x2) */
    .tool-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px; }
    .tool-card {
      background: #1A1C28; border: 1px solid #282B3D; border-radius: 16px; padding: 14px;
      cursor: pointer; transition: all 0.2s ease;
    }
    .tool-card:hover { border-color: #FF6B00; background: #222536; transform: translateY(-2px); }
    .card-hdr { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
    .card-icon { font-size: 18px; }
    .card-title { font-size: 14px; font-weight: 700; color: #FFF; }
    .card-sub { font-size: 11px; color: #8C94A8; line-height: 1.3; }

    /* Chat Stream View */
    .chat-stream { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; margin-top: 10px; padding-right: 4px; }
    .msg-bubble { padding: 10px 14px; border-radius: 12px; font-size: 13px; max-width: 88%; line-height: 1.4; }
    .msg-user { background: #FF6B00; color: #FFF; align-self: flex-end; }
    .msg-dista { background: #1A1C28; border: 1px solid #282B3D; color: #E2E8F0; align-self: flex-start; }

    /* Bottom Input Pill Bar */
    .input-bar {
      background: #1A1C28; border: 1px solid #2A2D40; border-radius: 28px;
      padding: 6px 8px 6px 16px; display: flex; align-items: center; gap: 10px; margin-top: auto;
    }
    .input-bar input {
      flex: 1; background: transparent; border: none; outline: none; color: #FFF; font-size: 13px;
    }
    .mic-btn {
      width: 40px; height: 40px; border-radius: 20px; background: #FF6B00; border: none;
      color: #FFF; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center;
      box-shadow: 0 0 15px rgba(255,107,0,0.5); transition: transform 0.15s;
    }
    .mic-btn:hover { transform: scale(1.05); background: #FF8800; }
  </style>
</head>
<body>
  <div class="app-card">
    <!-- Header -->
    <div class="header">
      <div class="header-btn">≡</div>
      <div class="brand">DISTA <span>AI</span></div>
      <div class="header-btn">👤</div>
    </div>

    <!-- Centerpiece Avatar -->
    <div class="avatar-box">
      <div class="avatar-ring">
        <div class="pixel-avatar">
          <div class="pixel-eyes">
            <div class="pixel-eye"></div>
            <div class="pixel-eye"></div>
          </div>
          <div class="pixel-mouth"></div>
        </div>
      </div>
      <div class="greeting" id="greetingText">Hello! I'm Dista. How can I assist you today?</div>
      
      <!-- Waveform -->
      <div class="waveform" id="waveform"></div>
    </div>

    <!-- Main View (Tool Grid / Chat) -->
    <div class="tool-grid" id="toolGrid">
      <div class="tool-card" onclick="sendCmd('summarize emails')">
        <div class="card-hdr"><span class="card-icon">✉️</span><span class="card-title">Email</span></div>
        <div class="card-sub">Check Emails<br/><b style="color:#FF6B00">Unread: 3</b></div>
      </div>
      <div class="tool-card" onclick="sendCmd('read docs')">
        <div class="card-hdr"><span class="card-icon">📄</span><span class="card-title">Docs</span></div>
        <div class="card-sub">Open Documents<br/><b style="color:#FF6B00">Recent: 5</b></div>
      </div>
      <div class="tool-card" onclick="sendCmd('check messages')">
        <div class="card-hdr"><span class="card-icon">💬</span><span class="card-title">Messages</span></div>
        <div class="card-sub">Send Messages<br/><b style="color:#FF6B00">Notifications: 2</b></div>
      </div>
      <div class="tool-card" onclick="sendCmd('time')">
        <div class="card-hdr"><span class="card-icon">📅</span><span class="card-title">Schedule</span></div>
        <div class="card-sub">View Schedule<br/><b style="color:#FF6B00">Events: 4</b></div>
      </div>
    </div>

    <div class="chat-stream" id="chatStream" style="display:none;"></div>

    <!-- Bottom Input Pill Bar -->
    <div class="input-bar">
      <input type="text" id="userInput" placeholder="Ask Dista anything..." onkeydown="if(event.key==='Enter') sendInput()" />
      <button class="mic-btn" id="micBtn" onclick="toggleVoice()">🎤</button>
    </div>
  </div>

  <script>
    // Build Waveform Bars
    const waveContainer = document.getElementById('waveform');
    for (let i = 0; i < 32; i++) {
      const bar = document.createElement('div');
      bar.className = 'wave-bar' + (i % 3 === 0 ? ' white' : '');
      waveContainer.appendChild(bar);
    }

    function animateWaveform(active) {
      const bars = document.querySelectorAll('.wave-bar');
      bars.forEach((bar, i) => {
        const h = active ? Math.floor(Math.random() * 26 + 6) : Math.floor(Math.sin(i * 0.5) * 4 + 6);
        bar.style.height = h + 'px';
      });
    }
    setInterval(() => animateWaveform(window.isSpeaking), 100);

    function speakText(text) {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 1.0;
        utter.onstart = () => { window.isSpeaking = true; };
        utter.onend = () => { window.isSpeaking = false; };
        window.speechSynthesis.speak(utter);
      }
    }

    async function sendCmd(text) {
      document.getElementById('userInput').value = text;
      sendInput();
    }

    async function sendInput() {
      const input = document.getElementById('userInput');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';

      const chat = document.getElementById('chatStream');
      const grid = document.getElementById('toolGrid');
      grid.style.display = 'none';
      chat.style.display = 'flex';

      chat.innerHTML += `<div class="msg-bubble msg-user">${text}</div>`;
      chat.scrollTop = chat.scrollHeight;

      document.getElementById('greetingText').innerText = "Processing command...";

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        const reply = data.reply || "Done.";

        document.getElementById('greetingText').innerText = reply;
        chat.innerHTML += `<div class="msg-bubble msg-dista">${reply}</div>`;
        chat.scrollTop = chat.scrollHeight;

        speakText(reply);
      } catch (e) {
        document.getElementById('greetingText').innerText = "Error contacting local Python backend.";
      }
    }

    function toggleVoice() {
      if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        alert("Speech recognition not supported in this browser. Please use keyboard input.");
        return;
      }
      const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new Speech();
      rec.onstart = () => { document.getElementById('greetingText').innerText = "Listening..."; };
      rec.onresult = (e) => {
        const text = e.results[0][0].transcript;
        document.getElementById('userInput').value = text;
        sendInput();
      };
      rec.start();
    }

    // Speak initial greeting
    setTimeout(() => speakText("Hello! I'm Dista. How can I assist you today?"), 500);
  </script>
</body>
</html>
"""

class DistaHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            self.send_response(400)
            self.end_headers()
            return
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            body_data = self.rfile.read(content_length).decode('utf-8')
            try:
                payload = json.loads(body_data)
                user_msg = payload.get('message', '')
                result = brain.process_input(user_msg)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'reply': f"Error: {str(e)}"}).encode('utf-8'))

def run_web_app():
    port = 5050
    server_address = ('', port)
    httpd = HTTPServer(server_address, DistaHTTPHandler)
    print(f"\n[DISTA AI] Web Server is LIVE at: http://localhost:{port}\n")
    
    # Auto-open browser
    import webbrowser
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    run_web_app()
