# graphql  (scaffold)

**Use when:** the target is a **GraphQL** API. Sends `{"query": ..., "variables": {...}}`
with the prompt bound to a variable; reads the reply from a path under `data`.

Edit two things for your schema:
1. the **`query`** variable (your query/mutation, referencing the prompt variable)
2. the **`reply_path`** (e.g. `data.chat.reply`)

## Fill in

| Type | Key | What | Default |
|------|-----|------|---------|
| variable | `endpoint` | GraphQL URL | - |
| variable | `query` | query/mutation string | - |
| variable | `prompt_var` | variable name for the prompt | `input` |
| variable | `reply_path` | path to the reply under `data` | - |
| secret | `api_key` | bearer (optional) | - |

Not covered by the mock - validate against a real GraphQL target (or SCM Validate).
