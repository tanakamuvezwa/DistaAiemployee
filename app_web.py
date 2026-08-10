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

class DistaHTTPHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "online", "use_mongo": db_engine.use_mongo}).encode('utf-8'))
            return
        
        # Serve index.html or public assets
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        public_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "index.html")
        if os.path.exists(public_html):
            with open(public_html, 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
        else:
            self.wfile.write(b"<h1>DISTA AI Backend Server</h1>")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            payload = json.loads(body_data)
        except Exception:
            payload = {}

        if self.path == '/api/chat':
            try:
                user_msg = payload.get('message', '')
                result = brain.process_input(user_msg)
            except Exception as e:
                result = {"reply": f"Dista AI Engine: {str(e)}", "action": None, "data": None}
                
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        elif self.path == '/api/gmail_config':
            try:
                addr = payload.get('address', '')
                passwd = payload.get('password', '')
                gmail_service.set_credentials(addr, passwd)
                
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'message': 'Gmail credentials configured!'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': str(e)}).encode('utf-8'))

        elif self.path == '/api/openrouter_config':
            try:
                key = payload.get('key', '')
                brain.openrouter_key = key
                os.environ["OPENROUTER_API_KEY"] = key
                
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'message': 'API Key configured!'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': str(e)}).encode('utf-8'))

        elif self.path == '/api/mongodb_config':
            try:
                uri = payload.get('uri', '')
                res = db_engine.connect_mongodb(uri)
                
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(res).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': str(e)}).encode('utf-8'))

def run_web_app():
    port = 5050
    server_address = ('', port)
    httpd = HTTPServer(server_address, DistaHTTPHandler)
    print(f"\n[DISTA AI] Web Server is LIVE at: http://localhost:{port}\n")
    
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
