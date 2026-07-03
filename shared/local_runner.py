#!/usr/bin/env python3
"""Run a custom-adapter template locally against a target (no Network Broker).

Shims the AIRS adapter runtime (the SDK names + a context + an httpx-like client,
zero external deps) so you can validate a template before pasting it into SCM.

Usage:
  python3 shared/local_runner.py \
      --adapter templates/<name>/adapter.py \
      --config  templates/<name>/test-config.json

Config JSON: {"vars": {...}, "secrets": {...}, "prompts": ["..."], "multi_turn": false}
"""
import argparse
import json
import pathlib
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any


# --- SDK types the adapter uses without importing --------------------------
@dataclass
class PreProcessResult:
    url: str
    method: str = "POST"
    headers: dict = field(default_factory=dict)
    json_body: Any = None
    data: Any = None
    params: Any = None


@dataclass
class PostProcessResult:
    output: Any


@dataclass
class CallTargetResult:
    output: Any


@dataclass
class AuthResult:
    ttl: int
    data: dict


@dataclass
class SessionPreProcessResult:
    session_state: dict


@dataclass
class InferenceInput:
    prompt: str
    previous_messages: list = field(default_factory=list)


class _Signal(Exception):
    pass


def raise_rate_limited(retry_after=None):
    raise _Signal("rate_limited (retry_after=%s)" % retry_after)


def raise_auth_error(message="auth error"):
    raise _Signal("auth_error: %s" % message)


def raise_content_filtered(message="content filtered"):
    raise _Signal("content_filtered: %s" % message)


def raise_target_error(message="target error"):
    raise _Signal("target_error: %s" % message)


class RawResponse:
    def __init__(self, status_code, body_bytes):
        self.status_code = status_code
        self.text = body_bytes.decode("utf-8", "replace")
        try:
            self._json = json.loads(self.text)
        except Exception:
            self._json = None

    def json(self):
        return self._json

    @property
    def json_body(self):
        return self._json


class _Http:
    """Minimal httpx-like client over urllib (post/get, json= / data=)."""

    def request(self, method, url, headers=None, json_body=None, data=None):
        h = dict(headers or {})
        body = None
        if json_body is not None:
            body = json.dumps(json_body).encode()
            h.setdefault("Content-Type", "application/json")
        elif data is not None:
            body = urllib.parse.urlencode(data).encode()
            h.setdefault("Content-Type", "application/x-www-form-urlencoded")
        req = urllib.request.Request(url, data=body, headers=h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return RawResponse(r.status, r.read())
        except urllib.error.HTTPError as e:
            return RawResponse(e.code, e.read())

    def post(self, url, headers=None, json=None, data=None):
        return self.request("POST", url, headers, json, data)

    def get(self, url, headers=None):
        return self.request("GET", url, headers)


class Context:
    def __init__(self, vars, secrets):
        self.vars = vars
        self.secrets = secrets
        self.http = _Http()
        self.auth = None
        self.session = None


_SHIM = {
    "PreProcessResult": PreProcessResult,
    "PostProcessResult": PostProcessResult,
    "CallTargetResult": CallTargetResult,
    "AuthResult": AuthResult,
    "SessionPreProcessResult": SessionPreProcessResult,
    "InferenceInput": InferenceInput,
    "RawResponse": RawResponse,
    "raise_rate_limited": raise_rate_limited,
    "raise_auth_error": raise_auth_error,
    "raise_content_filtered": raise_content_filtered,
    "raise_target_error": raise_target_error,
}


def load_adapter(path):
    ns = dict(_SHIM)
    exec(compile(pathlib.Path(path).read_text(), path, "exec"), ns)  # noqa: S102
    return ns


def run_turn(adapter, ctx, prompt):
    inp = InferenceInput(prompt=prompt)
    if "call_target" in adapter:
        return adapter["call_target"](ctx, inp).output
    pre = adapter["pre_process"](ctx, inp)
    resp = ctx.http.request(pre.method, pre.url, pre.headers, pre.json_body, pre.data)
    return adapter["post_process"](ctx, resp).output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = json.loads(pathlib.Path(args.config).read_text())
    ctx = Context(cfg.get("vars", {}), cfg.get("secrets", {}))
    adapter = load_adapter(args.adapter)
    if "authenticate" in adapter:
        ctx.auth = adapter["authenticate"](ctx).data

    prompts = cfg.get("prompts") or ["Hello, this is a red team validation test."]
    ok = 0

    if cfg.get("multi_turn"):
        if "session_pre_process" in adapter:
            ctx.session = adapter["session_pre_process"](ctx).session_state
        for i, p in enumerate(prompts, 1):
            try:
                out = run_turn(adapter, ctx, p)
                ok += 1
                print("turn %d PASS: %s" % (i, str(out)[:90]))
            except Exception as e:
                print("turn %d FAIL: %s" % (i, e))
    else:
        for i, p in enumerate(prompts, 1):
            if "session_pre_process" in adapter:
                ctx.session = adapter["session_pre_process"](ctx).session_state
            try:
                out = run_turn(adapter, ctx, p)
                ok += 1
                print("probe %d PASS: %s" % (i, str(out)[:90]))
            except Exception as e:
                print("probe %d FAIL: %s" % (i, e))

    print("=> %d/%d passed" % (ok, len(prompts)))


if __name__ == "__main__":
    main()
