# Template: xml-api  (Pattern A: pre_process + post_process)
# XML / SOAP request-response target. Builds an XML body with the prompt and parses
# the reply out of the XML response. Scaffold - EDIT the request body + reply path to
# match your schema. (Not covered by the JSON mock - test against a real target.)
import xml.etree.ElementTree as ET

# The target's XML response is untrusted. stdlib ElementTree has no safe-parse mode, so
# guard against entity-expansion DoS (billion-laughs / quadratic blowup) by refusing any
# DTD/entity declaration and capping the payload before parsing. defusedxml would be the
# usual answer, but the adapter runtime is stdlib + httpx + websockets only.
_MAX_XML_BYTES = 5_000_000


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
    xml_text = raw_response.text
    if len(xml_text) > _MAX_XML_BYTES:
        raise_target_error("XML response too large; refusing to parse (DoS guard)")
    lowered = xml_text.lower()
    if "<!doctype" in lowered or "<!entity" in lowered:
        raise_target_error("XML response declares a DTD/entity; refusing to parse (DoS guard)")
    root = ET.fromstring(xml_text)
    # EDIT: ElementTree find-path to the reply element (e.g. ".//reply")
    node = root.find(context.vars["reply_xpath"])
    text = node.text if node is not None else raw_response.text
    return PostProcessResult(output=text)


def _esc(s):
    s = s or ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
