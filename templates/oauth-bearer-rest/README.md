# oauth-bearer-rest

**Use when:** the target is a REST JSON endpoint behind **OAuth2 client_credentials**
(short-lived bearer), with **no session** step. AIRS fetches + refreshes the token for you.

- Auth: `POST {token_url}` form `client_credentials` -> bearer
- Request: `POST {endpoint}` with the bearer, body `{"message": "<prompt>"}`
- Reply: read from `reply_path`

> If your body key isn't `message`, edit the `json_body` line in `adapter.py`.

## Fill in

| Type | Key | What |
|------|-----|------|
| variable | `token_url` | OAuth token endpoint |
| variable | `endpoint` | run endpoint URL |
| variable | `reply_path` | JSON path to the reply text |
| secret | `client_id` | OAuth client id |
| secret | `client_secret` | OAuth client secret |

## Test locally

```bash
python3 testing/mock_target.py --port 8080 &
python3 shared/local_runner.py \
  --adapter templates/oauth-bearer-rest/adapter.py \
  --config  templates/oauth-bearer-rest/test-config.json
```

Expected: both probes PASS.
