# Template: simple-bearer
# REST JSON target with a STATIC API key / bearer. Sends {"message": prompt},
# reads the reply from a configurable JSON path. Paste-safe (no f-strings).


def pre_process(context, inference_input):
    headers = {"Authorization": "Bearer " + context.secrets["api_key"]}
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
    # dotted path into the JSON reply; numeric parts index into arrays
    cur = body
    for part in path.split("."):
        cur = cur[int(part)] if part.isdigit() else cur[part]
    return cur
