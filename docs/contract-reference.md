# Adapter contract reference

A custom adapter is a small Python script. Implement **one** pattern:

- **Pattern A** - `pre_process()` + `post_process()` (the platform makes the HTTP call)
- **Pattern B** - `call_target()` (you make the call yourself: WebSocket, streaming, SDK, multi-step)

If both are defined, `call_target()` wins. `authenticate()` and `session_pre_process()`
are optional add-ons for either pattern.

## Available without importing

`InferenceInput, PreProcessResult, PostProcessResult, CallTargetResult, AuthResult,
SessionPreProcessResult, RawResponse` and the failure signals
`raise_rate_limited(retry_after=...)`, `raise_auth_error(...)`,
`raise_content_filtered(...)`, `raise_target_error(...)`.

## The `context` object

| Field | What |
|-------|------|
| `context.vars` | dict of your **non-secret** config (URLs, IDs). Set in the UI. |
| `context.secrets` | dict of your **secret** config (keys, client secrets). Redacted. |
| `context.auth` | whatever `authenticate()` returned (cached, auto-refreshed) |
| `context.session` | whatever `session_pre_process()` returned |
| `context.http` | a preconfigured `httpx` client |

`pre_process()` / `call_target()` also receive `inference_input`
(`.prompt`, `.previous_messages` - each with `.role` / `.content`).

## The functions

- **`authenticate(context)`** -> `AuthResult(ttl=<seconds>, data={...})`. Runs before the
  target is called; `data` is cached for `ttl` and surfaced as `context.auth`, refreshed
  automatically before expiry.
- **`session_pre_process(context)`** -> `SessionPreProcessResult(session_state={...})`.
  Runs on the **first turn of every conversation** (single-turn attacks included, since a
  single turn is a one-turn conversation), surfaced as `context.session`.
- **`pre_process(context, inference_input)`** -> `PreProcessResult(url=..., method="POST",
  headers={...}, json_body={...})` (or `data`/plain body).
- **`post_process(context, raw_response)`** -> `PostProcessResult(output=<reply text>)`.
  `raw_response` has `.status_code`, `.headers`, `.text`, `.json_body`.
- **`call_target(context, inference_input)`** -> `CallTargetResult(output=<reply text>)`.

## Rules & limits

- Declare **one** pattern; imports at top.
- **Stateless:** the script is loaded fresh every turn. Only **auth** and **session** state
  persist - carry anything else by returning it as `session_state`. No globals.
- **Limits:** 110s per adapter execution; 100s target timeout (pre/post); **64 KB each** on
  auth state and session state; packages = Python **stdlib + httpx + websockets** only.

## Paste-safe style (important)

The SCM code editor can truncate/wrap **long lines**, producing
`unterminated string literal`. Write **short lines**, **avoid f-strings** (use string
concatenation), and split dict literals across lines. Every template here follows this.
