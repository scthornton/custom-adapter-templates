# xml-api  (scaffold)

**Use when:** the target speaks **XML / SOAP** request-response instead of JSON.
Uses `pre_process` + `post_process` with the stdlib XML parser.

This is a **starter** - XML schemas vary. Edit two things in `adapter.py`:

1. the **request envelope** built in `pre_process` (the `body = ...` line)
2. the **reply element path** (`reply_xpath`, an ElementTree find-path like `.//reply`)

## Fill in

| Type | Key | What |
|------|-----|------|
| variable | `endpoint` | run endpoint URL |
| variable | `reply_xpath` | ElementTree path to the reply element |
| secret | `api_key` | optional bearer/API key |

## Notes

- `xml.etree.ElementTree` is stdlib (always available).
- `data=` sends the raw XML body. If your platform build names the raw-body field
  differently, adjust the `pre_process` return.
- Not covered by the JSON mock - validate against a real target (or in SCM Validate).
