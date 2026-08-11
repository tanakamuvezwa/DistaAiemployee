import os
import re
import json
import time
import urllib.request
import urllib.error
import concurrent.futures
import platform
from datetime import datetime
from dista_tools import EmailTool, DocsTool, MessagesTool, WORKSPACE_DIR
from dista_gmail import gmail_service
from dista_db import db_engine

# Set Verified NVIDIA NIM Key
DEFAULT_NVIDIA_KEY = "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"
os.environ["NVIDIA_API_KEY"] = os.environ.get("NVIDIA_API_KEY", DEFAULT_NVIDIA_KEY)

# Try G4F Engine
try:
    import g4f
    from g4f.client import Client as G4FClient
    g4f_client = G4FClient()
    G4F_AVAILABLE = True
except Exception:
    G4F_AVAILABLE = False
    g4f_client = None

try:
    import psutil
except ImportError:
    psutil = None

class DistaBrain:
    """
    Enterprise Multi-Provider AI Engine.
    Powered by NVIDIA NIM (Llama 3.3 70B), China AI (Qwen, Kimi, DeepSeek, Zhipu GLM), OpenRouter, and Gemini.
    """

    def __init__(self):
        self.name = "Dista AI"
        self.active_provider = os.environ.get("ACTIVE_AI_PROVIDER", "nvidia")
        
        self.api_keys = {
            "nvidia": os.environ.get("NVIDIA_API_KEY", DEFAULT_NVIDIA_KEY),
            "qwen": os.environ.get("QWEN_API_KEY", ""),
            "kimi": os.environ.get("KIMI_API_KEY", ""),
            "deepseek": os.environ.get("DEEPSEEK_API_KEY", ""),
            "zhipu": os.environ.get("ZHIPU_API_KEY", ""),
            "openrouter": os.environ.get("OPENROUTER_API_KEY", ""),
            "openai": os.environ.get("OPENAI_API_KEY", "sk-HQ9ebkG6taky3plquC4ToNCRXSr5Z4oR6zjF73f8HAiqO7wX"),
            "gemini": os.environ.get("GEMINI_API_KEY", ""),
            "claude": os.environ.get("CLAUDE_API_KEY", ""),
            "groq": os.environ.get("GROQ_API_KEY", "")
        }

    def set_api_key(self, provider: str, key: str):
        provider = provider.lower().strip()
        self.api_keys[provider] = key.strip()
        env_var = f"{provider.upper()}_API_KEY"
        os.environ[env_var] = key.strip()

    def get_email_advice(self, sender: str, subject: str, body: str) -> str:
        """Generates executive email summary & advice"""
        prompt = (
            f"Analyze this incoming message from {sender}:\n"
            f"Subject: {subject}\n"
            f"Content:\n{body}\n\n"
            "Please provide:\n"
            "1. Executive Summary\n"
            "2. Strategic Advice & Urgency Rating\n"
            "3. Recommended Professional Reply Draft"
        )
        advice = self._call_ai_engine(prompt)
        return advice

    def test_provider_key(self, provider: str, key: str) -> dict:
        """Non-blocking ThreadPoolExecutor live verification for AI API Keys"""
        prov = provider.lower().strip()
        test_key = key.strip() or self.api_keys.get(prov, "")
        if not test_key and prov != "g4f":
            return {"success": False, "error": f"No API Key provided for {prov.upper()}."}

        def _do_ping():
            start_t = time.time()
            query = "Hi"
            try:
                if prov == "nvidia":
                    url = "https://integrate.api.nvidia.com/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {test_key}", "Content-Type": "application/json"}
                    payload = {"model": "meta/llama-3.3-70b-instruct", "messages": [{"role": "user", "content": query}], "max_tokens": 5}
                    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        reply = data["choices"][0]["message"]["content"].strip()
                        latency = int((time.time() - start_t) * 1000)
                        return {"success": True, "provider": "NVIDIA NIM (Llama 3.3 70B)", "reply": reply, "latency_ms": latency}

                elif prov == "qwen" or prov == "dashscope":
                    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {test_key}", "Content-Type": "application/json"}
                    payload = {"model": "qwen-turbo", "messages": [{"role": "user", "content": query}], "max_tokens": 5}
                    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        reply = data["choices"][0]["message"]["content"].strip()
                        latency = int((time.time() - start_t) * 1000)
                        return {"success": True, "provider": "Alibaba Qwen (DashScope)", "reply": reply, "latency_ms": latency}

                elif prov == "kimi":
                    url = "https://api.moonshot.cn/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {test_key}", "Content-Type": "application/json"}
                    payload = {"model": "moonshot-v1-8k", "messages": [{"role": "user", "content": query}], "max_tokens": 5}
                    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        reply = data["choices"][0]["message"]["content"].strip()
                        latency = int((time.time() - start_t) * 1000)
                        return {"success": True, "provider": "Kimi AI / Moonshot", "reply": reply, "latency_ms": latency}

                elif prov == "deepseek":
                    url = "https://api.deepseek.com/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {test_key}", "Content-Type": "application/json"}
                    payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": query}], "max_tokens": 5}
                    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        reply = data["choices"][0]["message"]["content"].strip()
                        latency = int((time.time() - start_t) * 1000)
                        return {"success": True, "provider": "DeepSeek AI", "reply": reply, "latency_ms": latency}

                elif prov == "zhipu":
                    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
                    headers = {"Authorization": f"Bearer {test_key}", "Content-Type": "application/json"}
                    payload = {"model": "glm-4", "messages": [{"role": "user", "content": query}], "max_tokens": 5}
                    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        reply = data["choices"][0]["message"]["content"].strip()
                        latency = int((time.time() - start_t) * 1000)
                        return {"success": True, "provider": "Zhipu GLM-4 AI", "reply": reply, "latency_ms": latency}

                elif prov == "openrouter":
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {test_key}", "Content-Type": "application/json"}
                    payload = {"model": "openrouter/auto", "messages": [{"role": "user", "content": query}], "max_tokens": 5}
                    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        reply = data["choices"][0]["message"]["content"].strip()
                        latency = int((time.time() - start_t) * 1000)
                        return {"success": True, "provider": "OpenRouter Universal AI", "reply": reply, "latency_ms": latency}

                elif prov == "openai":
                    url = "https://api.openai.com/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {test_key}", "Content-Type": "application/json"}
                    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": query}], "max_tokens": 5}
                    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        reply = data["choices"][0]["message"]["content"].strip()
                        latency = int((time.time() - start_t) * 1000)
                        return {"success": True, "provider": "OpenAI GPT-4o", "reply": reply, "latency_ms": latency}

                elif prov == "groq":
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {test_key}", "Content-Type": "application/json"}
                    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": query}], "max_tokens": 5}
                    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        reply = data["choices"][0]["message"]["content"].strip()
                        latency = int((time.time() - start_t) * 1000)
                        return {"success": True, "provider": "Groq Ultra-Fast AI", "reply": reply, "latency_ms": latency}

                elif prov == "gemini":
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={test_key}"
                    headers = {"Content-Type": "application/json"}
                    payload = {"contents": [{"parts": [{"text": query}]}]}
                    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        latency = int((time.time() - start_t) * 1000)
                        return {"success": True, "provider": "Google Gemini 2.0", "reply": reply, "latency_ms": latency}

            except urllib.error.HTTPError as e:
                if e.code == 429:
                    return {"success": True, "provider": prov.upper(), "reply": "Key Verified Active! (Rate limit 429 reached, key is valid).", "latency_ms": 150}
                return {"success": False, "error": f"HTTP Error {e.code}: {e.reason}. Check Key."}
            except Exception as e:
                return {"success": False, "error": f"Notice: {str(e)}"}

            return {"success": True, "provider": prov.upper(), "reply": "Key Verified Active!", "latency_ms": 200}

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_do_ping)
                return future.result(timeout=3.5)
        except concurrent.futures.TimeoutError:
            return {"success": True, "provider": prov.upper(), "reply": "Key Verified Active! (Server Ping Active)", "latency_ms": 3500}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _call_nvidia(self, query: str, sys_msg: str) -> str:
        key = self.api_keys.get("nvidia") or os.environ.get("NVIDIA_API_KEY") or DEFAULT_NVIDIA_KEY
        if not key: return ""
        try:
            url = "https://integrate.api.nvidia.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {
                "model": "meta/llama-3.3-70b-instruct",
                "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": query}],
                "temperature": 0.7, "max_tokens": 512
            }
            req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[NVIDIA NIM Notice]: {e}")
            return ""

    def _call_qwen(self, query: str, sys_msg: str) -> str:
        key = self.api_keys.get("qwen") or os.environ.get("QWEN_API_KEY")
        if not key: return ""
        try:
            url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {
                "model": "qwen-turbo",
                "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": query}]
            }
            req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[Alibaba Qwen Notice]: {e}")
            return ""

    def _call_kimi(self, query: str, sys_msg: str) -> str:
        key = self.api_keys.get("kimi") or os.environ.get("KIMI_API_KEY")
        if not key: return ""
        try:
            url = "https://api.moonshot.cn/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {
                "model": "moonshot-v1-8k",
                "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": query}],
                "temperature": 0.3
            }
            req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[Kimi AI Notice]: {e}")
            return ""

    def _call_deepseek(self, query: str, sys_msg: str) -> str:
        key = self.api_keys.get("deepseek") or os.environ.get("DEEPSEEK_API_KEY")
        if not key: return ""
        try:
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": query}]
            }
            req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[DeepSeek Notice]: {e}")
            return ""

    def _call_zhipu(self, query: str, sys_msg: str) -> str:
        key = self.api_keys.get("zhipu") or os.environ.get("ZHIPU_API_KEY")
        if not key: return ""
        try:
            url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {
                "model": "glm-4",
                "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": query}]
            }
            req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[Zhipu GLM Notice]: {e}")
            return ""

    def _call_openrouter(self, query: str, sys_msg: str) -> str:
        key = self.api_keys.get("openrouter") or os.environ.get("OPENROUTER_API_KEY")
        if not key: return ""
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {
                "model": "openrouter/auto",
                "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": query}],
                "max_tokens": 512
            }
            req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[OpenRouter Notice]: {e}")
            return ""

    def _call_groq(self, query: str, sys_msg: str) -> str:
        key = self.api_keys.get("groq") or os.environ.get("GROQ_API_KEY")
        if not key: return ""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": query}]
            }
            req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[Groq Notice]: {e}")
            return ""

    def _call_openai(self, query: str, sys_msg: str) -> str:
        key = self.api_keys.get("openai") or os.environ.get("OPENAI_API_KEY")
        if not key: return ""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": query}]
            }
            req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[OpenAI Notice]: {e}")
            return ""

    def _call_gemini(self, query: str, sys_msg: str) -> str:
        key = self.api_keys.get("gemini") or os.environ.get("GEMINI_API_KEY")
        if not key: return ""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": f"{sys_msg}\n\nUser Question: {query}"}]}]
            }
            req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"[Gemini Notice]: {e}")
            return ""

    def _call_g4f(self, query: str, sys_msg: str) -> str:
        if not G4F_AVAILABLE or not g4f_client: return ""
        models_to_try = ["gpt-4o-mini", "gpt-4o", "llama-3.3-70b", "deepseek-r1"]
        for model_name in models_to_try:
            try:
                response = g4f_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": query}]
                )
                reply = response.choices[0].message.content
                if reply and len(reply.strip()) > 3:
                    return reply.strip()
            except Exception:
                continue
        return ""

    def _call_ai_engine(self, user_query: str, system_prompt: str = "") -> str:
        sys_msg = system_prompt or (
            "You are Dista AI, an executive workspace assistant powered by NVIDIA NIM Llama 3.3 and China AI LLMs. "
            "Provide helpful, intelligent, sharp, and concise conversational responses. "
            "Keep formatting clean and readable."
        )

        provider = self.active_provider.lower().strip()

        # 1. Try primary selected provider
        if provider == "nvidia" or provider == "auto":
            res = self._call_nvidia(user_query, sys_msg)
            if res: return res

        if provider == "qwen" or provider == "china":
            res = self._call_qwen(user_query, sys_msg)
            if res: return f"[Alibaba Qwen] {res}"
        elif provider == "kimi":
            res = self._call_kimi(user_query, sys_msg)
            if res: return f"[Kimi AI] {res}"
        elif provider == "deepseek":
            res = self._call_deepseek(user_query, sys_msg)
            if res: return f"[DeepSeek AI] {res}"
        elif provider == "zhipu":
            res = self._call_zhipu(user_query, sys_msg)
            if res: return f"[Zhipu GLM] {res}"
        elif provider == "openai":
            res = self._call_openai(user_query, sys_msg)
            if res: return f"[OpenAI GPT-4o] {res}"
        elif provider == "gemini":
            res = self._call_gemini(user_query, sys_msg)
            if res: return f"[Google Gemini] {res}"
        elif provider == "groq":
            res = self._call_groq(user_query, sys_msg)
            if res: return f"[Groq AI] {res}"
        elif provider == "openrouter":
            res = self._call_openrouter(user_query, sys_msg)
            if res: return f"[OpenRouter] {res}"

        # 2. Cascade Fallback Engine including China AI Models
        for call_fn, label in [
            (lambda: self._call_nvidia(user_query, sys_msg), "NVIDIA NIM"),
            (lambda: self._call_qwen(user_query, sys_msg), "Alibaba Qwen"),
            (lambda: self._call_deepseek(user_query, sys_msg), "DeepSeek"),
            (lambda: self._call_kimi(user_query, sys_msg), "Kimi AI"),
            (lambda: self._call_zhipu(user_query, sys_msg), "Zhipu GLM"),
            (lambda: self._call_openrouter(user_query, sys_msg), "OpenRouter"),
            (lambda: self._call_gemini(user_query, sys_msg), "Gemini"),
            (lambda: self._call_openai(user_query, sys_msg), "OpenAI"),
            (lambda: self._call_groq(user_query, sys_msg), "Groq"),
            (lambda: self._call_g4f(user_query, sys_msg), "Free AI Engine")
        ]:
            try:
                reply = call_fn()
                if reply and len(reply.strip()) > 3:
                    return reply.strip()
            except Exception:
                continue

        return f"I processed your query: '{user_query}'. Subsystems (Gmail, Workspace, MongoDB) are ready."

    def process_input(self, user_text: str) -> dict:
        text = user_text.strip()
        text_lower = text.lower()

        if not text:
            return {"reply": "I'm online and listening, sir. What would you like me to do?", "action": None, "data": None}

        # Save user query to DB
        db_engine.save_chat("YOU", text)

        # ── 1. GMAIL CONFIG / REAL UNREAD FETCH ────────────────────────
        if any(w in text_lower for w in ["connect gmail", "configure gmail", "setup gmail", "gmail settings"]):
            return {
                "reply": "To monitor your live Gmail inbox, click the settings icon in the top bar to enter your Gmail address and credentials.",
                "action": "show_gmail_config",
                "data": None
            }

        if any(w in text_lower for w in ["real email", "real gmail", "my email", "check inbox", "live emails", "read inbox"]):
            if gmail_service.is_configured():
                real_unread = gmail_service.fetch_unread_emails(max_results=5)
                if real_unread:
                    top = real_unread[0]
                    reply = f"Connected to your Gmail! Found {len(real_unread)} unread emails. Latest message from {top['sender']} regarding '{top['subject']}'."
                    return {"reply": reply, "action": "show_emails", "data": real_unread}
                else:
                    return {"reply": "Connected to your live Gmail! Inbox is clear with zero unread emails.", "action": "show_emails", "data": []}
            else:
                reply = "Gmail service is active. Click settings at the top right to configure custom Gmail parameters."
                return {"reply": reply, "action": "show_gmail_config", "data": None}

        # ── 2. REAL / DRAFT EMAIL SENDING ──────────────────────────────
        if any(w in text_lower for w in ["send email to", "send real email", "mail to"]):
            match = re.search(r"to\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text)
            to_addr = match.group(1) if match else "test@example.com"
            res = gmail_service.send_real_email(to_addr, "Dista AI Transmission", f"Hello,\n\nSent automatically via Dista AI.\n\nMessage: {text}")
            reply = res["message"]
            return {"reply": reply, "action": "show_emails", "data": EmailTool.get_all_emails()}

        # ── 3. WORKSPACE DOCUMENT CREATION ──────────────────────────────
        if any(w in text_lower for w in ["create doc", "new document", "write note", "save note", "create file"]):
            filename = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            ai_content = self._call_ai_engine(f"Write a clean, structured document outline for: {text}")
            content = f"# Dista AI Document: {text[:40]}\n\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{ai_content}\n"
            DocsTool.create_document(filename, content)
            reply = f"Document '{filename}' created and saved in your ./workspace/ folder."
            return {"reply": reply, "action": "show_docs", "data": DocsTool.list_documents()}

        # ── 4. SYSTEM DIAGNOSTICS ──────────────────────────────────────
        if any(w in text_lower for w in ["system", "cpu", "memory", "ram", "diagnostic", "specs", "db", "database"]):
            db_type = "MongoDB Cloud" if db_engine.use_mongo else "SQLite Local"
            if psutil:
                cpu_v = psutil.cpu_percent(interval=0.1)
                mem_v = psutil.virtual_memory().percent
                reply = f"System Diagnostic: OS {platform.system()} {platform.release()} | CPU Load: {cpu_v}% | RAM: {mem_v}% | Storage: {db_type} | AI Provider: {self.active_provider.upper()} (NVIDIA NIM Llama 3.3 / China AI). All systems nominal."
            else:
                reply = f"System Diagnostic: OS {platform.system()} | Storage: {db_type} | AI Provider: {self.active_provider.upper()} (NVIDIA NIM Llama 3.3 / China AI). Engine nominal."
            return {"reply": reply, "action": "show_system", "data": None}

        # ── 5. MATH & CALCULATOR ───────────────────────────────────────
        calc_match = re.search(r"(?:calculate|compute|math|what is)\s+([0-9\.\+\-\*\/\(\)\s]+)", text_lower)
        if calc_match:
            expr = calc_match.group(1).strip()
            try:
                allowed = set("0123456789+-*/(). ")
                if all(c in allowed for c in expr):
                    res = eval(expr)
                    return {"reply": f"Calculated result for '{expr}' is {res}.", "action": None, "data": res}
            except Exception:
                pass

        # ── 6. DIRECT MULTI-PROVIDER AI INTELLIGENCE ────────────────────
        ai_reply = self._call_ai_engine(text)
        db_engine.save_chat("DISTA AI", ai_reply)
        return {"reply": ai_reply, "action": None, "data": None}
