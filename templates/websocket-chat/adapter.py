# Template: websocket-chat  (Pattern B: call_target)
# Streaming chat over a WebSocket. Connects, sends the prompt, reads chunks until an
# end marker, returns the assembled reply. WebSocket framing is target-specific, so
# EDIT the marked lines to match yours. (Not covered by the HTTP mock - test against
# a real WS target.)
#
# If the socket needs a token, add the `authenticate()` from oauth-bearer-rest and read
# context.auth["token"] below.
import asyncio
import json

import websockets


def call_target(context, inference_input):
    return asyncio.run(_run(context, inference_input.prompt))


async def _run(context, prompt):
    url = context.vars["ws_url"]
    headers = {}
    token = (context.auth or {}).get("token")
    if token:
        headers["Authorization"] = "Bearer " + token

    # NOTE: some websockets versions use additional_headers= instead of extra_headers=
    async with websockets.connect(url, extra_headers=headers) as ws:
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
