import sys
import os
import json
import socketserver
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import local Python backend tools
from dista_brain import DistaBrain
from dista_tools import EmailTool, DocsTool, MessagesTool
from dista_gmail import gmail_service
from dista_db import db_engine

brain = DistaBrain()

class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

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
        try:
            if '/api/emails' in self.path:
                if gmail_service.is_configured():
                    emails = gmail_service.fetch_unread_emails(max_results=10)
                    if not emails:
                        emails = EmailTool.get_all_emails()
                else:
                    emails = EmailTool.get_all_emails()
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "emails": emails}).encode('utf-8'))
                return

            elif '/api/docs' in self.path:
                docs = DocsTool.list_documents()
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "docs": docs}).encode('utf-8'))
                return

            elif self.path.startswith('/api/'):
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "online", "active_provider": brain.active_provider, "use_mongo": db_engine.use_mongo}).encode('utf-8'))
                return
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            
            public_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "index.html")
            if os.path.exists(public_html):
                with open(public_html, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b"<h1>DISTA AI Backend Server</h1>")
        except Exception as e:
            print(f"[GET Error]: {e}")

    def do_POST(self):
        try:
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

            elif self.path == '/api/advice':
                sender = payload.get('sender', '')
                subject = payload.get('subject', '')
                body = payload.get('body', '')
                try:
                    advice = brain.get_email_advice(sender, subject, body)
                    res = {"success": True, "advice": advice}
                except Exception as e:
                    res = {"success": False, "error": str(e)}

                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(res).encode('utf-8'))

            elif self.path == '/api/create_doc':
                filename = payload.get('filename', 'note.md')
                content = payload.get('content', '')
                ok = DocsTool.create_document(filename, content)
                res = {"success": ok, "message": f"Document '{filename}' created in workspace!"}

                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(res).encode('utf-8'))

            elif self.path == '/api/create_csv':
                filename = payload.get('filename', 'report.csv')
                rows = payload.get('rows', [["Header 1", "Header 2"], ["Val 1", "Val 2"]])
                ok = DocsTool.create_spreadsheet(filename, rows)
                res = {"success": ok, "message": f"CSV Spreadsheet '{filename}' created in workspace!"}

                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(res).encode('utf-8'))

            elif '/api/emails' in self.path:
                if gmail_service.is_configured():
                    emails = gmail_service.fetch_unread_emails(max_results=10)
                else:
                    emails = EmailTool.get_unread_emails()
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "emails": emails}).encode('utf-8'))

            elif self.path == '/api/test_key':
                provider = payload.get('provider', 'nvidia')
                key = payload.get('key', '')
                try:
                    res = brain.test_provider_key(provider, key)
                except Exception as e:
                    res = {'success': False, 'error': str(e)}

                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(res).encode('utf-8'))

            elif self.path == '/api/provider_config':
                try:
                    provider = payload.get('provider', 'auto')
                    key = payload.get('key', '')
                    brain.active_provider = provider
                    os.environ["ACTIVE_AI_PROVIDER"] = provider
                    if key:
                        brain.set_api_key(provider, key)
                    res = {'success': True, 'message': f'AI Provider set to {provider.upper()}!'}
                except Exception as e:
                    res = {'success': False, 'message': str(e)}

                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(res).encode('utf-8'))

            elif self.path == '/api/gmail_config':
                try:
                    addr = payload.get('address', '')
                    passwd = payload.get('password', '')
                    gmail_service.set_credentials(addr, passwd)
                    res = {'success': True, 'message': 'Gmail credentials configured!'}
                except Exception as e:
                    res = {'success': False, 'message': str(e)}

                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(res).encode('utf-8'))

            elif self.path == '/api/mongodb_config':
                try:
                    uri = payload.get('uri', '')
                    res = db_engine.connect_mongodb(uri)
                except Exception as e:
                    res = {'success': False, 'message': str(e)}

                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(res).encode('utf-8'))

        except Exception as e:
            print(f"[POST Error]: {e}")
            try:
                self.send_response(500)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            except Exception:
                pass

def run_web_app():
    port = 5050
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, DistaHTTPHandler)
    print(f"\n[DISTA AI] Multi-Threaded Web Server is LIVE at: http://localhost:{port}\n")
    
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
