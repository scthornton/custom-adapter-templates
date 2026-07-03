# signed-request  (scaffold)

**Use when:** the target requires an **HMAC signature** header computed over the request
(timestamp + body), rather than a simple key/bearer. Uses stdlib `hmac` / `hashlib`.

It signs the **exact bytes** it sends (the body is built as a raw string and passed via
`data`, so the signature matches). Edit for your scheme:
1. the **string-to-sign** (`to_sign`) - many targets sign `method + path + timestamp + body`
2. the **header names** (`ts_header`, `sig_header`, `key_id_header`)

## Fill in

| Type | Key | What | Default |
|------|-----|------|---------|
| variable | `endpoint` | run endpoint URL | - |
| variable | `reply_path` | JSON path to the reply | - |
| variable | `prompt_field` | body key holding the prompt | `message` |
| variable | `ts_header` / `sig_header` / `key_id_header` | header names | `X-Timestamp` / `X-Signature` / `X-Key-Id` |
| secret | `signing_key` | HMAC secret | - |
| secret | `key_id` | key id (optional) | - |

Not covered by the mock (no signature verification) - validate against a real target.
