import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import local Python backend tools
from dista_brain import DistaBrain
from dista_tools import EmailTool, DocsTool, MessagesTool
from dista_gmail import gmail_service
from dista_db import db_engine

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
      max-width: 440px;
      height: 870px;
      background-color: #0F1017;
      border: 2px solid #282B3D;
      border-radius: 36px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.85), 0 0 40px rgba(255,107,0,0.18);
      display: flex;
      flex-direction: column;
      padding: 24px 20px;
      position: relative;
      overflow: hidden;
    }

    /* Top Header Bar */
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
    .brand { font-size: 18px; font-weight: 800; letter-spacing: 1px; color: #FFF; }
    .brand span { color: #FF6B00; }
    .header-btn { width: 36px; height: 36px; border-radius: 18px; background: #1A1C28; border: 1px solid #282B3D; color: #8C94A8; display: flex; align-items: center; justify-content: center; font-size: 16px; cursor: pointer; transition: all 0.2s; }
    .header-btn:hover { border-color: #FF6B00; color: #FFF; }

    /* Badges */
    .badge-bar { display: flex; gap: 8px; margin-bottom: 10px; }
    .badge { font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 12px; background: #1A1C28; border: 1px solid #282B3D; color: #94A3B8; }
    .badge.active { border-color: #FF6B00; color: #FF6B00; }

    /* Center Avatar Box */
    .avatar-box { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 10px; margin-bottom: 10px; }
    .avatar-ring {
      width: 140px; height: 140px; border-radius: 50%;
      border: 2.5px solid #FF6B00;
      box-shadow: 0 0 25px rgba(255,107,0,0.45), inset 0 0 20px rgba(255,107,0,0.15);
      display: flex; align-items: center; justify-content: center;
      position: relative;
    }
    .avatar-ring.listening { border-color: #00E5FF; box-shadow: 0 0 30px rgba(0,229,255,0.6); }
    .avatar-ring.speaking { border-color: #FF8800; box-shadow: 0 0 35px rgba(255,136,0,0.7); }

    .pixel-avatar {
      width: 96px; height: 96px;
      background: radial-gradient(circle at 35% 35%, #D7DEEB, #A0A8B8);
      clip-path: polygon(25% 0%, 75% 0%, 100% 25%, 100% 75%, 75% 100%, 25% 100%, 0% 75%, 0% 25%);
      position: relative;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .pixel-eyes { display: flex; gap: 20px; margin-top: -8px; }
    .pixel-eye { width: 12px; height: 12px; background: #FF6B00; border-radius: 3px; box-shadow: 0 0 8px #FF6B00; }
    .pixel-eye.listening { background: #00E5FF; box-shadow: 0 0 10px #00E5FF; }
    .pixel-mouth { width: 20px; height: 4px; background: #282C3A; margin-top: 12px; border-radius: 2px; }
    .pixel-mouth.speaking { background: #FF6B00; height: 8px; animation: mouthTalk 0.2s infinite alternate; }

    @keyframes mouthTalk { from { height: 3px; } to { height: 10px; } }

    .greeting { font-size: 13px; font-weight: 600; color: #E2E8F0; max-width: 330px; line-height: 1.4; min-height: 38px; }

    /* Audio Waveform */
    .waveform { display: flex; align-items: center; justify-content: center; gap: 3.5px; height: 30px; }
    .wave-bar { width: 4px; height: 10px; background: #FF6B00; border-radius: 2px; transition: height 0.15s ease; }
    .wave-bar.white { background: #FFFFFF; }

    /* Action Shortcut Bar */
    .quick-actions { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 6px; margin-bottom: 8px; scrollbar-width: none; }
    .quick-actions::-webkit-scrollbar { display: none; }
    .action-chip {
      background: #1A1C28; border: 1px solid #282B3D; border-radius: 20px;
      padding: 6px 14px; font-size: 11px; font-weight: 600; color: #CBD5E1;
      white-space: nowrap; cursor: pointer; transition: all 0.2s;
    }
    .action-chip:hover { border-color: #FF6B00; color: #FFF; background: #222536; }

    /* Tool Grid (2x2) */
    .tool-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; flex: 1; }
    .tool-card {
      background: #1A1C28; border: 1px solid #282B3D; border-radius: 16px; padding: 12px;
      cursor: pointer; transition: all 0.2s ease; display: flex; flex-direction: column; justify-content: space-between;
    }
    .tool-card:hover { border-color: #FF6B00; background: #222536; transform: translateY(-2px); }
    .card-hdr { display: flex; align-items: center; gap: 8px; }
    .card-icon { font-size: 18px; }
    .card-title { font-size: 13px; font-weight: 700; color: #FFF; }
    .card-sub { font-size: 11px; color: #8C94A8; line-height: 1.3; margin-top: 4px; }

    /* Chat Stream View */
    .chat-stream { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding-right: 4px; }
    .msg-bubble { padding: 10px 14px; border-radius: 12px; font-size: 12.5px; max-width: 90%; line-height: 1.4; animation: fadeIn 0.2s ease; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
    .msg-user { background: #FF6B00; color: #FFF; align-self: flex-end; }
    .msg-dista { background: #1A1C28; border: 1px solid #282B3D; color: #E2E8F0; align-self: flex-start; }

    /* Modal Dialog */
    .modal {
      position: absolute; inset: 0; background: rgba(15,16,23,0.95); backdrop-filter: blur(10px);
      display: flex; flex-direction: column; justify-content: center; padding: 24px; z-index: 100;
    }
    .modal-card { background: #1A1C28; border: 1px solid #FF6B00; border-radius: 20px; padding: 20px; }
    .modal-title { font-size: 16px; font-weight: 700; color: #FF6B00; margin-bottom: 12px; }
    .modal-input { width: 100%; background: #0F1017; border: 1px solid #282B3D; border-radius: 8px; padding: 10px; color: #FFF; margin-bottom: 10px; font-size: 13px; }
    .modal-btn { width: 100%; padding: 10px; background: #FF6B00; border: none; border-radius: 8px; color: #FFF; font-weight: 700; cursor: pointer; }

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
      box-shadow: 0 0 15px rgba(255,107,0,0.5); transition: all 0.2s;
    }
    .mic-btn.active { background: #00E5FF; box-shadow: 0 0 20px rgba(0,229,255,0.7); color: #0F1017; }
    .mic-btn:hover { transform: scale(1.05); }
  </style>
</head>
<body>
  <div class="app-card">
    <!-- Header -->
    <div class="header">
      <div class="header-btn" onclick="toggleView()">≡</div>
      <div class="brand">DISTA <span>AI</span></div>
      <div class="header-btn" onclick="openGmailModal()">⚙️</div>
    </div>

    <!-- Status Badges -->
    <div class="badge-bar">
      <div class="badge active" id="badgeAi">● G4F GPT-4o AI</div>
      <div class="badge" id="badgeGmail">📧 Gmail: Disconnected</div>
      <div class="badge" id="badgeDb">💾 SQLite DB</div>
    </div>

    <!-- Centerpiece Avatar -->
    <div class="avatar-box">
      <div class="avatar-ring" id="avatarRing">
        <div class="pixel-avatar">
          <div class="pixel-eyes">
            <div class="pixel-eye" id="eyeL"></div>
            <div class="pixel-eye" id="eyeR"></div>
          </div>
          <div class="pixel-mouth" id="pixelMouth"></div>
        </div>
      </div>
      <div class="greeting" id="greetingText">Hello! I'm Dista. How can I assist you today?</div>
      
      <!-- Waveform -->
      <div class="waveform" id="waveform"></div>
    </div>

    <!-- Quick Action Chips -->
    <div class="quick-actions">
      <div class="action-chip" onclick="sendCmd('daily briefing')">⚡ Daily Briefing</div>
      <div class="action-chip" onclick="sendCmd('check inbox')">📧 Real Gmail Inbox</div>
      <div class="action-chip" onclick="sendCmd('draft email')">✍️ Draft Email</div>
      <div class="action-chip" onclick="sendCmd('create doc')">📄 Create Note</div>
      <div class="action-chip" onclick="sendCmd('schedule')">📅 View Schedule</div>
      <div class="action-chip" onclick="sendCmd('system')">💻 System Diagnostic</div>
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
      <div class="tool-card" onclick="sendCmd('schedule')">
        <div class="card-hdr"><span class="card-icon">📅</span><span class="card-title">Schedule</span></div>
        <div class="card-sub">View Schedule<br/><b style="color:#FF6B00">Events: 3</b></div>
      </div>
    </div>

    <div class="chat-stream" id="chatStream" style="display:none;"></div>

    <!-- Gmail Config Modal -->
    <div class="modal" id="gmailModal" style="display:none;">
      <div class="modal-card">
        <div class="modal-title">⚙️ Connect Real Gmail Account</div>
        <p style="font-size:11px;color:#8C94A8;margin-bottom:12px">
          Enter your Gmail address & 16-character Google App Password (generate at <b>myaccount.google.com/apppasswords</b>).
        </p>
        <input type="text" class="modal-input" id="gmailAddr" placeholder="your.name@gmail.com" />
        <input type="password" class="modal-input" id="gmailPass" placeholder="xxxx xxxx xxxx xxxx" />
        <button class="modal-btn" onclick="saveGmailConfig()">Save & Connect Inbox</button>
        <button class="modal-btn" style="background:#282B3D;margin-top:8px" onclick="closeGmailModal()">Cancel</button>
      </div>
    </div>

    <!-- Bottom Input Pill Bar -->
    <div class="input-bar">
      <input type="text" id="userInput" placeholder="Speak or type command for Dista..." onkeydown="if(event.key==='Enter') sendInput()" />
      <button class="mic-btn" id="micBtn" onclick="toggleVoice()" title="Toggle Voice Recognition">🎤</button>
    </div>
  </div>

  <script>
    let isListening = false;
    let isSpeaking = false;

    // Build 32 Waveform Bars
    const waveContainer = document.getElementById('waveform');
    for (let i = 0; i < 32; i++) {
      const bar = document.createElement('div');
      bar.className = 'wave-bar' + (i % 3 === 0 ? ' white' : '');
      waveContainer.appendChild(bar);
    }

    function animateWaveform() {
      const bars = document.querySelectorAll('.wave-bar');
      bars.forEach((bar, i) => {
        const h = isSpeaking || isListening
          ? Math.floor(Math.random() * 24 + 6)
          : Math.floor(Math.sin(Date.now() * 0.005 + i * 0.5) * 3 + 6);
        bar.style.height = h + 'px';
      });
    }
    setInterval(animateWaveform, 80);

    function updateAvatarState(state) {
      const ring = document.getElementById('avatarRing');
      const mouth = document.getElementById('pixelMouth');
      const eyeL = document.getElementById('eyeL');
      const eyeR = document.getElementById('eyeR');

      ring.className = 'avatar-ring ' + state;
      eyeL.className = 'pixel-eye ' + (state === 'listening' ? 'listening' : '');
      eyeR.className = 'pixel-eye ' + (state === 'listening' ? 'listening' : '');
      mouth.className = 'pixel-mouth ' + (state === 'speaking' ? 'speaking' : '');
    }

    function speakText(text) {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 1.05;
        utter.pitch = 1.0;
        utter.onstart = () => {
          isSpeaking = true;
          updateAvatarState('speaking');
        };
        utter.onend = () => {
          isSpeaking = false;
          updateAvatarState(isListening ? 'listening' : '');
        };
        window.speechSynthesis.speak(utter);
      }
    }

    function toggleView() {
      const grid = document.getElementById('toolGrid');
      const chat = document.getElementById('chatStream');
      if (grid.style.display === 'none') {
        grid.style.display = 'grid';
        chat.style.display = 'none';
      } else {
        grid.style.display = 'none';
        chat.style.display = 'flex';
      }
    }

    function openGmailModal() { document.getElementById('gmailModal').style.display = 'flex'; }
    function closeGmailModal() { document.getElementById('gmailModal').style.display = 'none'; }

    async function saveGmailConfig() {
      const addr = document.getElementById('gmailAddr').value.trim();
      const pass = document.getElementById('gmailPass').value.trim();
      if (!addr || !pass) { alert("Please enter both Gmail Address & App Password"); return; }

      const res = await fetch('/api/gmail_config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: addr, password: pass })
      });
      const data = await res.json();
      closeGmailModal();
      document.getElementById('badgeGmail').className = 'badge active';
      document.getElementById('badgeGmail').innerText = '📧 Gmail: Connected';
      alert(data.message);
      sendCmd('check inbox');
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

      document.getElementById('greetingText').innerText = "Processing...";
      updateAvatarState('speaking');

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        const reply = data.reply || "Command executed.";

        document.getElementById('greetingText').innerText = reply;
        chat.innerHTML += `<div class="msg-bubble msg-dista">${reply}</div>`;
        chat.scrollTop = chat.scrollHeight;

        speakText(reply);
      } catch (e) {
        document.getElementById('greetingText').innerText = "Error contacting Dista AI Python backend.";
        updateAvatarState('');
      }
    }

    function toggleVoice() {
      if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        alert("Web Speech API not supported in this browser. Please use Chrome/Edge or type below.");
        return;
      }

      const micBtn = document.getElementById('micBtn');
      if (isListening) {
        isListening = false;
        micBtn.classList.remove('active');
        updateAvatarState('');
        document.getElementById('greetingText').innerText = "Voice recognition paused.";
        return;
      }

      const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new Speech();
      rec.continuous = false;
      rec.interimResults = false;

      rec.onstart = () => {
        isListening = true;
        micBtn.classList.add('active');
        updateAvatarState('listening');
        document.getElementById('greetingText').innerText = "Listening... State your command.";
      };

      rec.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        document.getElementById('userInput').value = transcript;
        sendInput();
      };

      rec.onerror = (e) => {
        isListening = false;
        micBtn.classList.remove('active');
        updateAvatarState('');
        document.getElementById('greetingText').innerText = "Voice input stopped. Click mic to speak again.";
      };

      rec.onend = () => {
        isListening = false;
        micBtn.classList.remove('active');
        if (!isSpeaking) updateAvatarState('');
      };

      rec.start();
    }

    // Speak initial greeting on load
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
        content_length = int(self.headers.get('Content-Length', 0))
        body_data = self.rfile.read(content_length).decode('utf-8')
        
        if self.path == '/api/chat':
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

        elif self.path == '/api/gmail_config':
            try:
                payload = json.loads(body_data)
                addr = payload.get('address', '')
                passwd = payload.get('password', '')
                gmail_service.set_credentials(addr, passwd)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'message': 'Gmail credentials configured!'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': str(e)}).encode('utf-8'))

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
