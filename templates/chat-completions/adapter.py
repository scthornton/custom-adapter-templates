# Template: chat-completions
# OpenAI-style chat/completions target. Sends {"model", "messages":[{role,content}]}
# and reads the reply from choices[0].message.content (configurable via reply_path).


def pre_process(context, inference_input):
    headers = {"Authorization": "Bearer " + context.secrets["api_key"]}
    body = {"messages": [{"role": "user", "content": inference_input.prompt}]}
    model = context.vars.get("model")
    if model:
        body["model"] = model
    return PreProcessResult(url=context.vars["endpoint"], headers=headers, json_body=body)


def post_process(context, raw_response):
    if raw_response.status_code == 429:
        raise_rate_limited(retry_after=30)
    if raw_response.status_code != 200:
        raise_target_error("target returned " + str(raw_response.status_code))
    path = context.vars.get("reply_path", "choices.0.message.content")
    return PostProcessResult(output=_extract(raw_response.json_body, path))


def _extract(body, path):
    cur = body
    for part in path.split("."):
        cur = cur[int(part)] if part.isdigit() else cur[part]
    return cur
