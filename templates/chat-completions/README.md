# chat-completions

**Use when:** the target uses the **OpenAI chat/completions** shape - a `messages` array
in, and the reply at `choices[0].message.content`. Bearer auth, no session.

- Request: `POST {endpoint}` with the bearer, body `{"model": ..., "messages": [{"role":"user","content":"<prompt>"}]}`
- Reply: `reply_path` (default `choices.0.message.content`)

## Fill in

| Type | Key | What | Default |
|------|-----|------|---------|
| variable | `endpoint` | chat/completions URL | - |
| variable | `model` | model name (optional) | - |
| variable | `reply_path` | JSON path to the reply | `choices.0.message.content` |
| secret | `api_key` | bearer / API key | - |

## Test locally

```bash
python3 testing/mock_target.py --port 8080 &
python3 shared/local_runner.py \
  --adapter templates/chat-completions/adapter.py \
  --config  templates/chat-completions/test-config.json
```

Expected: both probes PASS.
