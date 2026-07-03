# simple-bearer

**Use when:** the target is a plain REST JSON endpoint protected by a **static API key /
bearer** that doesn't expire, and there's no session step.

- Request: `POST {endpoint}` with `Authorization: Bearer <api_key>`, body `{"message": "<prompt>"}`
- Reply: read from `reply_path` (dotted JSON path, e.g. `reply` or `choices.0.message.content`)

> If your body key isn't `message`, edit the `json_body` line in `adapter.py`.

## Fill in

| Type | Key | What |
|------|-----|------|
| variable | `endpoint` | run endpoint URL |
| variable | `reply_path` | JSON path to the reply text |
| secret | `api_key` | the static key/bearer |

## Test locally

```bash
python3 testing/mock_target.py --port 8080 &
python3 shared/local_runner.py \
  --adapter templates/simple-bearer/adapter.py \
  --config  templates/simple-bearer/test-config.json
```

Expected: both probes PASS.
