#!/usr/bin/env python3
"""HAR -> custom adapter: turn a captured browser session into a filled template.

Capture a HAR of your working app talking to the target (browser DevTools -> Network
-> Save all as HAR). Tell the tool the prompt you typed (and ideally the reply). It
finds the auth / session / run calls, picks the matching template, and writes a filled
config. Observed credentials are emitted as PLACEHOLDERS, never as literals.

Usage:
  python3 tools/har_to_adapter.py --har capture.har --prompt "what I typed" \
      [--reply "the reply text"] --out out/

Covers HTTP request/response + session flows (what a HAR captures). WebSocket /
streaming targets aren't in a HAR - use the websocket-chat template.
"""
import argparse
import json
import pathlib
import shutil
import sys
from urllib.parse import urlsplit

TEMPLATES = pathlib.Path(__file__).resolve().parent.parent / "templates"


def load_entries(path):
    return json.loads(pathlib.Path(path).read_text())["log"]["entries"]


def body_text(msg):
    if "postData" in msg:
        return msg["postData"].get("text", "") or ""
    return (msg.get("content") or {}).get("text", "") or ""


def as_json(text):
    try:
        return json.loads(text)
    except Exception:
        return None


def header(headers, name):
    name = name.lower()
    for h in headers or []:
        if h.get("name", "").lower() == name:
            return h.get("value", "")
    return ""


def find_path(obj, needle, prefix=""):
    """Dotted path to the first string value containing `needle`."""
    if isinstance(obj, str):
        return prefix if (needle and needle in obj) else None
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = find_path(v, needle, (prefix + "." + k) if prefix else k)
            if p is not None:
                return p
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            p = find_path(v, needle, (prefix + "." + str(i)) if prefix else str(i))
            if p is not None:
                return p
    return None


def leaf_strings(obj, prefix=""):
    if isinstance(obj, str):
        yield obj, prefix
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaf_strings(v, (prefix + "." + k) if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaf_strings(v, (prefix + "." + str(i)) if prefix else str(i))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--har", required=True)
    ap.add_argument("--prompt", required=True, help="the exact prompt text you typed during capture")
    ap.add_argument("--reply", default=None, help="the reply text you got (improves reply detection)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    entries = load_entries(args.har)

    # 1) run call = the request whose body contains the prompt
    run = None
    prompt_path = None
    for e in entries:
        rj = as_json(body_text(e["request"]))
        if rj is not None:
            p = find_path(rj, args.prompt)
            if p:
                run, prompt_path = e, p
                break
    if not run:
        for e in entries:
            if args.prompt in body_text(e["request"]):
                run = e
                break
    if not run:
        sys.exit("Could not find a request containing your --prompt. Check the text and the HAR.")

    run_url = run["request"]["url"]
    run_path = urlsplit(run_url).path
    auth_hdr = header(run["request"]["headers"], "authorization")
    bearer = auth_hdr.split(" ", 1)[1] if auth_hdr.lower().startswith("bearer ") else ""

    # 2) reply path in the run response
    reply_path = None
    run_resp = as_json(body_text(run["response"]))
    if args.reply and run_resp is not None:
        reply_path = find_path(run_resp, args.reply)

    # 3) auth call = a response containing access_token (or carrying the bearer)
    token_url = None
    for e in entries:
        rj = as_json(body_text(e["response"]))
        if isinstance(rj, dict) and ("access_token" in rj or (bearer and bearer in json.dumps(rj))):
            token_url = e["request"]["url"]
            break

    # 4) session call = a response returning an id that appears in the run URL path
    session_url = session_id_field = run_base = run_suffix = None
    for e in entries:
        if e is run:
            continue
        rj = as_json(body_text(e["response"]))
        if not isinstance(rj, (dict, list)):
            continue
        for val, path in leaf_strings(rj):
            if val and len(val) >= 6 and val in run_path:
                session_url = e["request"]["url"]
                session_id_field = path
                idx = run_url.find(val)
                run_base = run_url[:idx].rstrip("/")
                run_suffix = run_url[idx + len(val):]
                break
        if session_url:
            break

    prompt_field = prompt_path.split(".")[-1] if prompt_path else "message"
    nested_prompt = bool(prompt_path and "." in prompt_path)

    # ---- choose template + build vars/secrets ----
    if session_url:
        template = "oauth-session-rest"
        vars_ = {
            "token_url": token_url or "<SET token_url>",
            "session_url": session_url,
            "run_base": run_base,
            "run_suffix": run_suffix,
            "session_id_field": session_id_field,
            "prompt_field": prompt_field,
            "reply_path": reply_path or "<SET reply_path>",
        }
        secrets = ["client_id", "client_secret"]
    elif token_url:
        template = "oauth-bearer-rest"
        vars_ = {"token_url": token_url, "endpoint": run_url,
                 "prompt_field": prompt_field, "reply_path": reply_path or "<SET reply_path>"}
        secrets = ["client_id", "client_secret"]
    else:
        template = "simple-bearer"
        vars_ = {"endpoint": run_url, "prompt_field": prompt_field,
                 "reply_path": reply_path or "<SET reply_path>"}
        secrets = ["api_key"]

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy(TEMPLATES / template / "adapter.py", out / "adapter.py")

    test_cfg = {"vars": vars_, "secrets": {s: "<SET %s>" % s for s in secrets},
                "multi_turn": False, "prompts": [args.prompt]}
    (out / "test-config.json").write_text(json.dumps(test_cfg, indent=2) + "\n")

    lines = []
    lines.append("# HAR import findings\n")
    lines.append("Matched template: **%s** (adapter.py copied to this folder)\n" % template)
    lines.append("## Detected")
    lines.append("- run call: `%s %s`" % (run["request"]["method"], run_url))
    lines.append("- auth: %s" % ("OAuth token call at " + token_url if token_url else
                                 ("static bearer in the run request" if bearer else "none detected")))
    lines.append("- session: %s" % ("created at " + session_url + " (id field `" + str(session_id_field) + "`)"
                                    if session_url else "none"))
    lines.append("- prompt field: `%s`%s" % (prompt_field, "  (NESTED - body is not flat; see below)" if nested_prompt else ""))
    lines.append("- reply path: `%s`" % (reply_path or "NOT FOUND - pass --reply, or set reply_path"))
    lines.append("\n## Enter in SCM")
    lines.append("Variables:")
    for k, v in vars_.items():
        lines.append("- `%s` = `%s`" % (k, v))
    lines.append("Secrets (set the real values - the HAR values were NOT copied):")
    for s in secrets:
        lines.append("- `%s`" % s)
    lines.append("\n## Verify")
    lines.append("- Any `<SET ...>` value above.")
    if nested_prompt:
        lines.append("- Prompt body is **nested** (`%s`). The flat templates send `{field: prompt}`; "
                     "for a nested body (e.g. chat-completions `messages`), use that template or edit `pre_process`." % prompt_path)
    lines.append("- Confirm the reply path against a real response.")
    lines.append("- Fill the secret placeholders in `test-config.json`, then run:")
    lines.append("  ```")
    lines.append("  python3 shared/local_runner.py --adapter %s/adapter.py --config %s/test-config.json" % (args.out, args.out))
    lines.append("  ```")
    (out / "FINDINGS.md").write_text("\n".join(lines) + "\n")

    print("template: %s" % template)
    print("wrote: %s/adapter.py, %s/test-config.json, %s/FINDINGS.md" % (args.out, args.out, args.out))


if __name__ == "__main__":
    main()
