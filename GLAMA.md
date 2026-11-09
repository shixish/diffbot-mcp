# Glama release

`glama.json` is already on `main`. Glama lists this server after a maintainer claims it and a release build answers `initialize` and `tools/list`. Description text is not part of that check.

Glama clones `github.com/diffbot/diffbot-mcp` into `/app`. `uv sync` installs dependencies into `/app/.venv`. The auto-detected `python3` is the base interpreter and fails with `No module named 'fastmcp'`.

Admin page: https://glama.ai/mcp/servers/diffbot/diffbot-mcp/admin/dockerfile

```json
{
  "baseImage": "debian:trixie-slim",
  "nodeVersion": "24",
  "pythonVersion": "3.12",
  "buildSteps": ["uv sync"],
  "cmdArguments": ["mcp-proxy", "--", "/app/.venv/bin/python", "diffbot_mcp_server.py"],
  "placeholderArguments": {},
  "pinnedCommit": null
}
```

Sync the server before Deploy so the checkout is current `main`, not an older commit. Leave `DIFFBOT_OAUTH_ISSUER` unset. Do not put a token in the placeholders. When Deploy succeeds, Make Release.

Claim from https://glama.ai/mcp/servers/diffbot/diffbot-mcp/score while signed in as `jeromechoo` or `shixish`.
