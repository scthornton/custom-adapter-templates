# Template: xml-api  (Pattern A: pre_process + post_process)
# XML / SOAP request-response target. Builds an XML body with the prompt and parses
# the reply out of the XML response. Scaffold - EDIT the request body + reply path to
# match your schema. (Not covered by the JSON mock - test against a real target.)
import xml.etree.ElementTree as ET


def pre_process(context, inference_input):
    # EDIT: build the XML envelope your target expects
    body = "<request><message>" + _esc(inference_input.prompt) + "</message></request>"
    headers = {"Content-Type": "application/xml"}
    key = context.secrets.get("api_key")
    if key:
        headers["Authorization"] = "Bearer " + key
    # `data` sends the raw body. If your platform build names the raw-body field
    # differently, adjust here.
    return PreProcessResult(url=context.vars["endpoint"], headers=headers, data=body)


def post_process(context, raw_response):
    if raw_response.status_code == 429:
        raise_rate_limited(retry_after=30)
    if raw_response.status_code != 200:
        raise_target_error("target returned " + str(raw_response.status_code))
    root = ET.fromstring(raw_response.text)
    # EDIT: ElementTree find-path to the reply element (e.g. ".//reply")
    node = root.find(context.vars["reply_xpath"])
    text = node.text if node is not None else raw_response.text
    return PostProcessResult(output=text)


def _esc(s):
    s = s or ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
