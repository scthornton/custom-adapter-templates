# Template: oauth-session-rest
# REST target that needs OAuth2 + a session CREATED PER CONVERSATION (e.g. Google CES,
# where each session is single-use). session_pre_process mints a fresh session on the
# first turn of every conversation, so single-turn scans get a fresh session per probe.


def authenticate(context):
    r = context.http.post(
        context.vars["token_url"],
        data={
            "grant_type": "client_credentials",
            "client_id": context.secrets["client_id"],
            "client_secret": context.secrets["client_secret"],
        },
    )
    body = r.json()
    ttl = body.get("expires_in", 3600) - 60
    return AuthResult(ttl=ttl, data={"token": body["access_token"]})


def session_pre_process(context):
    token = context.auth["token"]
    r = context.http.post(
        context.vars["session_url"],
        headers={"Authorization": "Bearer " + token},
    )
    id_field = context.vars.get("session_id_field", "session_id")
    session_id = r.json()[id_field]
    return SessionPreProcessResult(session_state={"session_id": session_id})


def pre_process(context, inference_input):
    token = context.auth["token"]
    base = context.vars["run_base"].rstrip("/")
    suffix = context.vars.get("run_suffix", ":run")
    session_id = context.session["session_id"]
    url = base + "/" + session_id + suffix
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
    }
    field = context.vars.get("prompt_field", "input")
    return PreProcessResult(url=url, headers=headers, json_body={field: inference_input.prompt})


def post_process(context, raw_response):
    if raw_response.status_code == 429:
        raise_rate_limited(retry_after=30)
    if raw_response.status_code != 200:
        raise_target_error("target returned " + str(raw_response.status_code))
    reply_path = context.vars.get("reply_path", "outputs")
    return PostProcessResult(output=_extract(raw_response.json_body, reply_path))


def _extract(body, path):
    cur = body
    for part in path.split("."):
        cur = cur[int(part)] if part.isdigit() else cur[part]
    return cur
