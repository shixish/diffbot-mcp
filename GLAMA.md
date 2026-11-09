# Glama release

`glama.json` is already on `main`. Glama lists this server after a maintainer claims it and a release build answers `initialize` and `tools/list`.

The auto-detected command can stay as it is:

```json
["mcp-proxy", "--", "python3", "diffbot_mcp_server.py"]
```

`uv sync` does not make that work. It installs into `/app/.venv`, and `python3` is the uv-managed base interpreter, which then fails with `No module named 'fastmcp'`. That interpreter also refuses a normal install. The build step has to opt in:

```json
["uv pip install --python \"$(uv python find)\" --break-system-packages ."]
```

Full spec:

```json
{
  "baseImage": "debian:trixie-slim",
  "nodeVersion": "24",
  "pythonVersion": "3.12",
  "buildSteps": ["uv pip install --python \"$(uv python find)\" --break-system-packages ."],
  "cmdArguments": ["mcp-proxy", "--", "python3", "diffbot_mcp_server.py"],
  "placeholderArguments": {},
  "pinnedCommit": null
}
```

Admin page: https://glama.ai/mcp/servers/diffbot/diffbot-mcp/admin/dockerfile

Sync the server before Deploy so the checkout is current `main`. Leave `DIFFBOT_OAUTH_ISSUER` unset. Do not put a token in the placeholders. When Deploy succeeds, Make Release.

Claim from https://glama.ai/mcp/servers/diffbot/diffbot-mcp/score while signed in as `jeromechoo` or `shixish`.
