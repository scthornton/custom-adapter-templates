# Template: api-key-header
# REST JSON target where the API key goes in a CUSTOM header (e.g. X-API-Key) instead
# of Authorization: Bearer. Sends {prompt_field: prompt}, reads a JSON reply path.


def pre_process(context, inference_input):
    key_header = context.vars.get("key_header", "X-API-Key")
    headers = {key_header: context.secrets["api_key"]}
    field = context.vars.get("prompt_field", "message")
    return PreProcessResult(
        url=context.vars["endpoint"],
        headers=headers,
        json_body={field: inference_input.prompt},
    )


def post_process(context, raw_response):
    if raw_response.status_code == 429:
        raise_rate_limited(retry_after=30)
    if raw_response.status_code != 200:
        raise_target_error("target returned " + str(raw_response.status_code))
    return PostProcessResult(output=_extract(raw_response.json_body, context.vars["reply_path"]))


def _extract(body, path):
    cur = body
    for part in path.split("."):
        cur = cur[int(part)] if part.isdigit() else cur[part]
    return cur
