# custom-adapter-templates

Ready-to-use **Prisma AIRS AI Red Teaming custom target adapter** templates for the field.

A custom adapter connects a **non-standard** red-team target (custom auth, sessions,
protocols) to AIRS Red Teaming. Most AIRS users are security practitioners, not
developers - these templates make an adapter a **fill-in-the-blanks** job: pick the
closest template, set variables + secrets, validate. No writing Python from scratch.

> Always check first whether a **built-in connector** fits (static key, standard OAuth,
> plain request/response). Adapters are for the cases built-ins don't cover.

## Gallery

| Template | Target shape | Auth | Session |
|----------|--------------|------|---------|
| `simple-bearer` | REST JSON, static API key | static bearer | no |
| `oauth-bearer-rest` | REST JSON, OAuth token | OAuth client_credentials | no |
| `oauth-session-rest` | REST + per-conversation session (e.g. Google CES) | OAuth client_credentials | yes (single-use) |
| `websocket-chat` | WebSocket streaming chat | token | optional |
| `xml-api` | XML / SOAP request-response | key / bearer | no |

(Templates land via PRs - see the `templates/` directory.)

## How to use

1. Pick the template whose shape matches your target (each has its own README).
2. Copy its `adapter.py` into the SCM **Custom Adapters** editor.
3. Set the **variables** + **secrets** listed in the template's `config.yaml`.
4. Select your network channel and click **Validate**.

Not sure of the shape? Run the [discovery questions](docs/discovery-questions.md), or
capture a **HAR** of your working app and match it to a template.

## Test locally first

`shared/local_runner.py` runs any template against a target **without** the Network Broker,
and `testing/mock_target.py` is a zero-dependency mock for the REST/session shapes. See
each template README for the exact command.

## Reference

- [docs/contract-reference.md](docs/contract-reference.md) - the adapter contract (functions, context, limits)
- [docs/discovery-questions.md](docs/discovery-questions.md) - the 10 questions to answer per target
- [CONTRIBUTING.md](CONTRIBUTING.md) - add a template

## Status

Early / actively built out. Templates and tooling arrive in small PRs.
