# websocket-chat  (scaffold)

**Use when:** the target speaks **WebSocket** (streaming chat) rather than plain
request/response HTTP. Uses `call_target` (Pattern B) so you control the socket.

This is a **starter** - WebSocket framing is target-specific. Edit the three marked
lines in `adapter.py`:

1. the **outbound message** shape (`ws.send(...)`)
2. how to detect the **final chunk** (end marker)
3. where the **text chunk** lives in each message

## Fill in

| Type | Key | What |
|------|-----|------|
| variable | `ws_url` | the WebSocket URL |
| secret | `token` | only if you add `authenticate()` for a bearer |

## Auth

If the socket needs a token, paste the `authenticate()` function from
`oauth-bearer-rest` and it will be available as `context.auth["token"]`.

## Notes

- `websockets` is provided by the adapter runtime. Some versions use
  `additional_headers=` instead of `extra_headers=` on `connect()`.
- Not covered by the HTTP mock - validate against a real WS target (or in SCM Validate).
