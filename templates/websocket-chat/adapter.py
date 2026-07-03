# Template: websocket-chat  (Pattern B: call_target)
# Streaming chat over a WebSocket. Connects, sends the prompt, reads chunks until an
# end marker, returns the assembled reply. WebSocket framing is target-specific, so
# EDIT the marked lines to match yours. (Not covered by the HTTP mock - test against
# a real WS target.)
#
# If the socket needs a token: set a static one as the `token` secret, or add the
# `authenticate()` from oauth-bearer-rest to fetch a short-lived one (context.auth).
import asyncio
import json

import websockets


def call_target(context, inference_input):
    return asyncio.run(_run(context, inference_input.prompt))


async def _run(context, prompt):
    url = context.vars["ws_url"]
    headers = {}
    # Prefer a token fetched by authenticate() (context.auth), fall back to a static
    # `token` secret so the declared secret works without adding authenticate().
    token = None
    if context.auth:
        token = context.auth.get("token")
    if not token:
        token = context.secrets.get("token")
    if token:
        headers["Authorization"] = "Bearer " + token

    # The AIRS runtime bundles websockets 15.x, which takes additional_headers=.
    # (Older websockets called this extra_headers=; that name was removed in v14.)
    async with websockets.connect(url, additional_headers=headers) as ws:
        # EDIT: shape the outbound message your target expects
        await ws.send(json.dumps({"input": prompt}))

        parts = []
        async for message in ws:
            data = _parse(message)
            # EDIT: how to detect the final chunk
            if isinstance(data, dict) and data.get("type") == "end":
                break
            # EDIT: where the text chunk lives
            chunk = data.get("text") if isinstance(data, dict) else str(data)
            if chunk:
                parts.append(chunk)
        return "".join(parts)


def _parse(message):
    try:
        return json.loads(message)
    except Exception:
        return message
