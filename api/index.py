import os
import sys
import json
from http.server import BaseHTTPRequestHandler

# Add root directory to sys.path for serverless imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dista_brain import DistaBrain
from dista_gmail import gmail_service
from dista_db import db_engine

brain = DistaBrain()

class handler(BaseHTTPRequestHandler):
    """
    Vercel Serverless Python Function Handler
    Handles API endpoints: /api/chat, /api/test_key, /api/provider_config, /api/gmail_config, /api/mongodb_config
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
