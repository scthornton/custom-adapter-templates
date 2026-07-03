# Template: signed-request  (scaffold)
# Target that requires an HMAC signature header over the request body. Signs the exact
# bytes it sends (so `data` carries the raw body, not json_body). EDIT the string-to-sign
# and header names to match your target's scheme.
import hashlib
import hmac
import time


def pre_process(context, inference_input):
    field = context.vars.get("prompt_field", "message")
    body = "{" + _q(field) + ":" + _q(inference_input.prompt) + "}"
    ts = str(int(time.time()))
    secret = context.secrets["signing_key"].encode()
    # EDIT: the exact string your target signs (often method + path + timestamp + body)
    to_sign = (ts + "." + body).encode()
    sig = hmac.new(secret, to_sign, hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        context.vars.get("ts_header", "X-Timestamp"): ts,
        context.vars.get("sig_header", "X-Signature"): sig,
    }
    key_id = context.secrets.get("key_id")
    if key_id:
        headers[context.vars.get("key_id_header", "X-Key-Id")] = key_id
    return PreProcessResult(url=context.vars["endpoint"], headers=headers, data=body)


def post_process(context, raw_response):
    if raw_response.status_code == 429:
        raise_rate_limited(retry_after=30)
    if raw_response.status_code != 200:
        raise_target_error("target returned " + str(raw_response.status_code))
    return PostProcessResult(output=_extract(raw_response.json_body, context.vars["reply_path"]))


def _q(s):
    # minimal JSON string with escaping
    out = str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return '"' + out + '"'


def _extract(body, path):
    cur = body
    for part in path.split("."):
        cur = cur[int(part)] if part.isdigit() else cur[part]
    return cur
