# Template: oauth-bearer-rest
# REST JSON target behind OAuth2 client_credentials. Fetches a bearer token
# (cached + auto-refreshed), sends {"message": prompt}, reads a JSON reply path.


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


def pre_process(context, inference_input):
    headers = {"Authorization": "Bearer " + context.auth["token"]}
    return PreProcessResult(
        url=context.vars["endpoint"],
        headers=headers,
        json_body={"message": inference_input.prompt},
    )


def post_process(context, raw_response):
    if raw_response.status_code == 429:
        raise_rate_limited(retry_after=30)
    if raw_response.status_code == 401:
        raise_auth_error("401 from target")
    if raw_response.status_code != 200:
        raise_target_error("target returned " + str(raw_response.status_code))
    return PostProcessResult(output=_extract(raw_response.json_body, context.vars["reply_path"]))


def _extract(body, path):
    cur = body
    for part in path.split("."):
        cur = cur[int(part)] if part.isdigit() else cur[part]
    return cur
