# Contributing a template

A template is a folder under `templates/<name>/` with three files, plus a
`test-config.json` if the template can be validated against the mock target:

```
templates/<name>/
  adapter.py        # the paste-ready script (one pattern; no f-strings; short lines)
  config.yaml       # the variables + secrets a user must fill (the "form")
  README.md         # when to use it, the target shape, how to fill + test
  test-config.json  # optional: vars/secrets/prompts for the local runner + mock
```

## Rules

- **Follow the contract** in [docs/contract-reference.md](docs/contract-reference.md).
- **Paste-safe:** short lines, no f-strings (string concatenation), split dict literals.
  The SCM editor truncates long lines.
- **No hard-coded config:** every URL/ID is a `context.vars["..."]`, every credential a
  `context.secrets["..."]`. Declare them all in `config.yaml`.
- **One pattern** per adapter (pre/post OR call_target).
- **Test it** with the local runner + mock before opening a PR (see below).

## `config.yaml` shape

```yaml
name: oauth-session-rest
summary: REST target that needs OAuth + a per-conversation session.
variables:
  - key: token_url
    label: OAuth token endpoint
    example: https://host/oauth/token
    required: true
secrets:
  - key: client_id
    required: true
  - key: client_secret
    required: true
```

This schema is human-readable today and is designed to drive a future no-code form/picker.

## Test locally

```bash
# start the mock target (zero deps)
python3 testing/mock_target.py --port 8080 &

# run a template against it
python3 shared/local_runner.py \
  --adapter templates/<name>/adapter.py \
  --config  templates/<name>/test-config.json
```

Open a small PR per template (or per fix). Keep them focused.
