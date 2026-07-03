# api-key-header

**Use when:** the target authenticates with an API key in a **custom header**
(e.g. `X-API-Key`, `api-key`) rather than `Authorization: Bearer`. REST JSON, no session.

- Request: `POST {endpoint}` with `{key_header}: <api_key>`, body `{prompt_field: "<prompt>"}`
- Reply: `reply_path`

## Fill in

| Type | Key | What | Default |
|------|-----|------|---------|
| variable | `endpoint` | run endpoint URL | - |
| variable | `key_header` | header name for the key | `X-API-Key` |
| variable | `reply_path` | JSON path to the reply | - |
| variable | `prompt_field` | body key holding the prompt | `message` |
| secret | `api_key` | the API key value | - |

## Test locally

```bash
python3 testing/mock_target.py --port 8080 &
python3 shared/local_runner.py \
  --adapter templates/api-key-header/adapter.py \
  --config  templates/api-key-header/test-config.json
```

Expected: both probes PASS.
