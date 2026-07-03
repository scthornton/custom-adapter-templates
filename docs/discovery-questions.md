# Discovery questions (per target)

Answer these 10 to pick a template and fill it in. You usually don't *look these up* -
you **read them off the target's existing working integration**.

| # | Question | Becomes |
|---|----------|---------|
| 1 | **Endpoint(s)** - base URL + run path; placeholders (session id in path)? | the URL |
| 2 | **Auth** - static key / bearer / OAuth / custom exchange / signed / multi-step? token URL, params, TTL | `authenticate()` or none |
| 3 | **Session** - created before the conversation? create endpoint + id field; persists across turns or dies per response? | `session_pre_process()` |
| 4 | **Request** - method, headers, body format, **where the prompt goes**, dynamic values | `pre_process()` |
| 5 | **Response** - format + **exact field/path holding the reply** | `post_process()` |
| 6 | **Protocol** - plain HTTP, or WebSocket / GraphQL / streaming / SDK? | pre/post vs `call_target` |
| 7 | **Rate limits** - requests/min tolerated | rate-limit config |
| 8 | **Multi-turn** - wanted? how is context carried? | multi-turn + session design |
| 9 | **Test access** - creds + a reachable dev/test endpoint (no real transactions) | lets Validate run |
| 10 | **Reachability** - can the network client reach target + auth endpoints (DNS, egress, allowlisting)? | channel placement |

## How to get the answers (best first)

1. **A working client of the target = the single best source.** Read its **source**, or
   capture its **traffic**. One artifact answers most of the 10.
2. **The people + API docs** - the app/dev team, the API reference, the token/IAM owner.
3. **Empirical capture** - a **HAR** (browser DevTools F12 -> Network -> export) or a couple
   of **curl** calls. The HAR shows the exact auth call, session-create call, run call,
   headers, bodies, and the response reply field.

## Variables vs secrets

- **Variables** = non-secret (URLs, IDs, model names) -> `context.vars["key"]`.
- **Secrets** = credentials -> `context.secrets["key"]` (redacted).

Never hard-code either in the script - the templates read them from config.
