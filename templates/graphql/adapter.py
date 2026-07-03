# Template: graphql  (scaffold)
# GraphQL target: POST {"query": ..., "variables": {...}} with the prompt as a variable.
# EDIT the query, the variable name, and the reply path to match your schema.


def pre_process(context, inference_input):
    headers = {"Content-Type": "application/json"}
    token = context.secrets.get("api_key")
    if token:
        headers["Authorization"] = "Bearer " + token
    var_name = context.vars.get("prompt_var", "input")
    body = {
        "query": context.vars["query"],
        "variables": {var_name: inference_input.prompt},
    }
    return PreProcessResult(url=context.vars["endpoint"], headers=headers, json_body=body)


def post_process(context, raw_response):
    if raw_response.status_code == 429:
        raise_rate_limited(retry_after=30)
    if raw_response.status_code != 200:
        raise_target_error("target returned " + str(raw_response.status_code))
    # EDIT: reply path under "data", e.g. data.chat.reply
    return PostProcessResult(output=_extract(raw_response.json_body, context.vars["reply_path"]))


def _extract(body, path):
    cur = body
    for part in path.split("."):
        cur = cur[int(part)] if part.isdigit() else cur[part]
    return cur
