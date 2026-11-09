# Glama release

Keep Glama's default build step and command:

```json
{
  "baseImage": "debian:trixie-slim",
  "nodeVersion": "24",
  "pythonVersion": "3.12",
  "buildSteps": ["uv sync"],
  "cmdArguments": ["mcp-proxy", "--", "python3", "diffbot_mcp_server.py"],
  "placeholderArguments": {},
  "pinnedCommit": null
}
```

`uv sync` installs into `/app/.venv`. Glama's `python3` is the base interpreter, so that command fails with `No module named 'fastmcp'` unless the checkout contains the build hook in `build_backend.py`. The hook runs during `uv sync` and points that `python3` at the virtualenv. It does nothing outside Glama's `/app` layout.

Glama clones `github.com/diffbot/diffbot-mcp`, so this has to be on the commit that clone checks out. Sync the server before Deploy. Leave `DIFFBOT_OAUTH_ISSUER` unset, and do not put a token in the placeholders. When Deploy succeeds, Make Release.

Admin page: https://glama.ai/mcp/servers/diffbot/diffbot-mcp/admin/dockerfile

Claim from https://glama.ai/mcp/servers/diffbot/diffbot-mcp/score while signed in as `jeromechoo` or `shixish`.
