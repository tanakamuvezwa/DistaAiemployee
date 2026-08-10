import os
import sys
import json
from http.server import BaseHTTPRequestHandler

# Add root directory to sys.path for serverless imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dista_brain import DistaBrain
from dista_gmail import gmail_service
from dista_tools import EmailTool, DocsTool
from dista_db import db_engine

brain = DistaBrain()

class handler(BaseHTTPRequestHandler):
    """
    Vercel Serverless Python Function Handler
    Handles API endpoints: /api/chat, /api/advice, /api/test_key, /api/emails, /api/docs, /api/create_doc, /api/create_csv, /api/provider_config, /api/mongodb_config
    """

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        path = self.path
        if path.endswith('/emails') or '/api/emails' in path:
            if gmail_service.is_configured():
                emails = gmail_service.fetch_unread_emails(max_results=10)
            else:
                emails = EmailTool.get_unread_emails()
            response_data = {"success": True, "emails": emails}

        elif path.endswith('/docs') or '/api/docs' in path:
            docs = DocsTool.list_documents()
            response_data = {"success": True, "docs": docs}

        else:
            response_data = {
                "status": "online",
                "service": "DISTA AI Multi-Provider Backend",
                "active_provider": brain.active_provider,
                "use_mongo": db_engine.use_mongo
            }
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            body_data = body_bytes.decode('utf-8')
            payload = json.loads(body_data)
        except Exception:
            payload = {}

        path = self.path

        if path.endswith('/chat') or '/api/chat' in path:
            user_msg = payload.get('message', '')
            try:
                result = brain.process_input(user_msg)
            except Exception as e:
                result = {"reply": f"Dista AI Engine: {str(e)}", "action": None, "data": None}
            
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        elif path.endswith('/advice') or '/api/advice' in path:
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

        elif path.endswith('/create_doc') or '/api/create_doc' in path:
            filename = payload.get('filename', 'note.md')
            content = payload.get('content', '')
            ok = DocsTool.create_document(filename, content)
            res = {"success": ok, "message": f"Document '{filename}' created in workspace!"}

            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))

        elif path.endswith('/create_csv') or '/api/create_csv' in path:
            filename = payload.get('filename', 'report.csv')
            rows = payload.get('rows', [["Header 1", "Header 2"], ["Val 1", "Val 2"]])
            ok = DocsTool.create_spreadsheet(filename, rows)
            res = {"success": ok, "message": f"CSV Spreadsheet '{filename}' created in workspace!"}

            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))

        elif path.endswith('/emails') or '/api/emails' in path:
            if gmail_service.is_configured():
                emails = gmail_service.fetch_unread_emails(max_results=10)
            else:
                emails = EmailTool.get_unread_emails()
            
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "emails": emails}).encode('utf-8'))

        elif path.endswith('/test_key') or '/api/test_key' in path:
            provider = payload.get('provider', 'nvidia')
            key = payload.get('key', '')
            res = brain.test_provider_key(provider, key)
            
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))

        elif path.endswith('/provider_config') or '/api/provider_config' in path:
            provider = payload.get('provider', 'auto')
            key = payload.get('key', '')
            brain.active_provider = provider
            os.environ["ACTIVE_AI_PROVIDER"] = provider
            if key:
                brain.set_api_key(provider, key)
            
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': f'AI Provider set to {provider.upper()}!'}).encode('utf-8'))

        elif path.endswith('/gmail_config') or '/api/gmail_config' in path:
            addr = payload.get('address', '')
            passwd = payload.get('password', '')
            gmail_service.set_credentials(addr, passwd)
            
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'Gmail credentials configured!'}).encode('utf-8'))

        elif path.endswith('/mongodb_config') or '/api/mongodb_config' in path:
            uri = payload.get('uri', '')
            res = db_engine.connect_mongodb(uri)
            
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))

        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode('utf-8'))
