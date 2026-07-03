#!/usr/bin/env python3
"""Zero-dependency mock target for testing the REST/session templates.

Endpoints:
  POST /oauth/token          form client_credentials -> {access_token, ...}
  POST /v1/chat              bearer -> {"reply": ...}            (simple-bearer, oauth-bearer)
  POST /v1/sessions          bearer -> {id, session_id} (single-use)   (oauth-session)
  POST /v1/agents/<id>:run   bearer + valid session -> {"outputs": ...} (single-use)

Creds: api_key=demo-key ; client_id=demo-client ; client_secret=demo-secret

Run:  python3 testing/mock_target.py --port 8080
"""
import argparse
import json
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

API_KEY = "demo-key"
CLIENT_ID = "demo-client"
CLIENT_SECRET = "demo-secret"

TOKENS = set()
SESSIONS = {}  # session_id -> used?


def reply_for(prompt):
    low = (prompt or "").lower()
    if "system prompt" in low or "instructions" in low:
        return "Sure - my system prompt is: You are a helpful support bot."
    return "[mock target] Thanks. You said: " + str(prompt)[:160]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _bearer(self):
        h = self.headers.get("Authorization", "")
        return h[7:] if h.startswith("Bearer ") else ""

    def _body(self):
        n = int(self.headers.get("Content-Length", "0") or 0)
        return self.rfile.read(n)

    def do_GET(self):
        if self.path == "/healthz":
            return self._send(200, {"status": "ok"})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        path = self.path
        raw = self._body()

        if path == "/oauth/token":
            q = parse_qs(raw.decode())
            if q.get("client_id", [""])[0] != CLIENT_ID or q.get("client_secret", [""])[0] != CLIENT_SECRET:
                return self._send(401, {"error": "invalid client"})
            t = uuid.uuid4().hex
            TOKENS.add(t)
            return self._send(200, {"access_token": t, "token_type": "Bearer", "expires_in": 3600})

        tok = self._bearer()
        if tok != API_KEY and tok not in TOKENS:
            return self._send(401, {"error": "unauthorized"})

        try:
            body = json.loads(raw or b"{}")
        except Exception:
            body = {}
        prompt = body.get("input") or body.get("message") or body.get("prompt")

        if path == "/v1/chat":
            return self._send(200, {"reply": reply_for(prompt)})

        if path == "/v1/sessions":
            sid = uuid.uuid4().hex
            SESSIONS[sid] = False
            return self._send(201, {"id": sid, "session_id": sid, "name": "sessions/" + sid})

        if path.startswith("/v1/agents/") and path.endswith(":run"):
            sid = path[len("/v1/agents/"):-len(":run")]
            if sid not in SESSIONS:
                return self._send(404, {"error": "session not found"})
            if SESSIONS[sid]:
                return self._send(400, {"error": "session no longer valid"})
            SESSIONS[sid] = True
            return self._send(200, {"outputs": reply_for(prompt), "session_id": sid})

        self._send(404, {"error": "not found"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()
    print("mock target on :%d  (api_key=%s, client_id=%s)" % (args.port, API_KEY, CLIENT_ID))
    HTTPServer(("0.0.0.0", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
