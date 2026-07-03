# oauth-session-rest

**Use when:** the target needs **OAuth2** *and* a **session created before the
conversation** - especially when each session is **single-use** (dies after one response),
like **Google CES** (`:streamRunSession`). This is the shape that breaks a standard
connector: reusing one session id makes probe #1 succeed and every probe after fail.

**How it fixes that:** `session_pre_process()` runs on the first turn of *every*
conversation. A single-turn attack is a one-turn conversation, so **each probe gets a
fresh session** and the scan runs clean.

- Auth: `POST {token_url}` client_credentials -> bearer
- Session: `POST {session_url}` -> read `session_id_field` for the new id
- Request: `POST {run_base}/<session_id>{run_suffix}` body `{"input": "<prompt>"}`
- Reply: read from `reply_path` (default `outputs`)

## Fill in

| Type | Key | What | Default |
|------|-----|------|---------|
| variable | `token_url` | OAuth token endpoint | - |
| variable | `session_url` | session-create endpoint | - |
| variable | `run_base` | base URL before the session id | - |
| variable | `run_suffix` | suffix after the session id | `:run` (CES: `:streamRunSession`) |
| variable | `session_id_field` | id field in the session response | `session_id` |
| variable | `prompt_field` | body key that holds the prompt | `input` |
| variable | `reply_path` | JSON path to the reply | `outputs` |
| secret | `client_id` / `client_secret` | OAuth creds | - |

## Multi-turn note

If you enable multi-turn on a target whose session dies per response, the single
up-front session won't survive turn 2. For that case, move the session-create into
`pre_process` (create a fresh session each turn). Single-turn needs no change.

## Test locally

```bash
python3 testing/mock_target.py --port 8080 &
python3 shared/local_runner.py \
  --adapter templates/oauth-session-rest/adapter.py \
  --config  templates/oauth-session-rest/test-config.json
```

Expected: all probes PASS (each gets a fresh single-use session).
