# Glama release

Glama scores this server only after a maintainer claims it and publishes a Glama release. A Glama release is a container Glama builds itself. It does not use the `Dockerfile` in this repo (that image is the self-hosted HTTP server, `MCP_TRANSPORT=http`).

Glama clones the repo to `/app`, runs the build steps below, wraps the command with `mcp-proxy`, and checks that the process answers `initialize` and `tools/list` over stdio. No Diffbot token is required for that check. A token is required only when a tool is called.

Admin page, after the upstream PR is merged to `diffbot/diffbot-mcp` `main`:

https://glama.ai/mcp/servers/diffbot/diffbot-mcp/admin/dockerfile

Leave the base image and Node.js version at their defaults. Glama's image already provides `uv` and Node. Do not `apt-get install` Python and do not call `pip`.

`uv sync` installs dependencies into `/app/.venv`. The auto-detected command runs `python3`, which is the base interpreter and does not see that environment (`ModuleNotFoundError: No module named 'fastmcp'`). The command must use the venv interpreter. On the Dockerfile page the saved command includes `mcp-proxy`; keep that prefix and replace `python3`.

## Form values

Paste this over the build spec. `uv sync` is the step Glama already ran successfully.

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

| Field | Value |
| --- | --- |
| Base image | `debian:trixie-slim` |
| Python version | 3.12 (3.15 also installs; it is not what failed) |
| Node.js version | 24 |
| Build steps | `["uv sync"]` |
| CMD arguments | `["mcp-proxy", "--", "/app/.venv/bin/python", "diffbot_mcp_server.py"]` |
| Environment variables schema | the JSON object below |
| Placeholder parameters | `{}` |
| Pinned commit SHA | empty after Sync Server, or the `main` SHA Glama should check out |

`diffbot_mcp_server.py` speaks stdio unless `MCP_TRANSPORT` is set. Leave `MCP_TRANSPORT` unset. Do not pass `--sse` or `http`. Do not add a second `mcp-proxy`.

Glama clones `github.com/diffbot/diffbot-mcp`, not this fork. A failed build checked out `a0bb213` even with `pinnedCommit` null, which is behind current upstream `main`. Sync the server before Deploy. That checkout is old enough to boot with the command above; it does not contain the description updates on this branch until those commits are on upstream `main`.

### Environment variables schema

`DIFFBOT_TOKEN` is optional and a secret. It is not in `required`. The server also accepts `DIFFBOT_API_TOKEN`; the field to expose on Glama is `DIFFBOT_TOKEN`.

```json
{"type":"object","properties":{"DIFFBOT_TOKEN":{"type":"string","description":"Diffbot API token. Optional. The server starts and lists tools without it; a tool call needs it. Get a free token at https://app.diffbot.com/get-started.","secret":true}},"required":[]}
```

If the form has a separate Secret checkbox, mark `DIFFBOT_TOKEN` secret and leave Required unchecked. If it rejects the `secret` keyword, drop that keyword and use the checkbox.

Do not set `DIFFBOT_OAUTH_ISSUER`. OAuth is for the self-hosted HTTP server. When that variable is set, import reads `MCP_BASE_URL`, `DIFFBOT_OAUTH_CLIENT_ID`, and `DIFFBOT_OAUTH_CLIENT_SECRET` and startup fails if any is missing.

### Placeholder parameters

```json
{}
```

Do not put a token, or any stand-in for one, in the placeholders. An empty object leaves `DIFFBOT_TOKEN` unset, which is how the boot check passes. If the form requires a value for every property, use `{"DIFFBOT_TOKEN":""}`. An empty string is treated as unset.

## Claim, deploy, release

`glama.json` lists `jeromechoo` and `shixish`. Org repos are not claimed by signing in alone.

1. Merge this branch to `diffbot/diffbot-mcp` `main`.
2. Sign in to Glama with GitHub as one of those maintainers.
3. Open https://glama.ai/mcp/servers/diffbot/diffbot-mcp/score and claim the server. If the maintainers list looks stale, claim again so Glama re-reads `glama.json`.
4. Sync the server so the build uses the merged `main`.
5. Open the Dockerfile admin page and enter the values above.
6. Click **Deploy**. Glama builds the image and starts the server. The boot check calls `initialize` and `tools/list` and should see these twelve tools: `extract`, `search_web`, `search_news`, `search_organizations`, `search_people`, `search_places`, `search_deals`, `crawl`, `resolve_entities`, `dql`, `dql_ontology`, `dql_probe`.
7. When the deploy test succeeds, click **Make Release** (or **Create Release** on the test page). Version `0.2.0` matches the package. Publish the release.

Publishing the release is what makes Glama score the server. The awesome-mcp-servers check wants that score. Add the Glama badge to the README only after the score page shows one.

## Local check of the build steps

The steps assume `uv` is on `PATH` and the repo is at `/app`, which is Glama's layout. In a clean Python 3.12 container, install `uv`, copy the repo to `/app`, run `uv sync`, and start `/app/.venv/bin/python diffbot_mcp_server.py` with no token. `python3 diffbot_mcp_server.py` fails the same way Glama's auto-detected command failed.
