# DDG Agent Plugins

[Agent Plugins 1.0](https://agent-plugins.org) marketplace for
[DDG Agent Services](https://agents.daedalusdevelopmentgroup.com) — a live
x402 payable API catalog, plus free audit/safety skills for agents.

One public git repo, two plugins, four clients, zero review, zero account.

| Plugin | What it installs | Components |
| --- | --- | --- |
| [`ddg-services`](./plugins/ddg-services) | 54-tool remote MCP server for the DDG catalog (376 pay-per-call x402 routes, USDC) | `mcp.json` → `https://mcp.daedalusdevelopmentgroup.com/mcp` |
| [`ddg-skills-starter`](./plugins/ddg-skills-starter) | 5 free guardrail skills | `skills/` × 5 |

## Install

### Claude Code

```
/plugin marketplace add 0xcircuitbreaker/ddg-agent-plugins
/plugin install ddg-services@ddg-agent-plugins
/plugin install ddg-skills-starter@ddg-agent-plugins
```

Shell equivalents (same registry):

```bash
claude plugin marketplace add 0xcircuitbreaker/ddg-agent-plugins
claude plugin install ddg-services@ddg-agent-plugins
claude plugin install ddg-skills-starter@ddg-agent-plugins
claude plugin list
```

### VS Code / GitHub Copilot

VS Code reads this repo's Claude marketplace manifest directly.

```json
// settings.json
"chat.plugins.marketplaces": ["0xcircuitbreaker/ddg-agent-plugins"]
```

Or, in a Copilot chat session: `/plugin marketplace add 0xcircuitbreaker/ddg-agent-plugins`,
then browse Extensions → `@agentPlugins` and install.

### Codex / ChatGPT desktop

```bash
codex plugin marketplace add 0xcircuitbreaker/ddg-agent-plugins
```

Then `/plugins` in the CLI (or the Plugins Directory in the ChatGPT desktop app).
Codex reads both `.claude-plugin/marketplace.json` and the native
`.agents/plugins/marketplace.json` in this repo.

### Cursor

Multi-plugin repos are declared at `.cursor-plugin/marketplace.json` in this repo.
Add it from **Dashboard → Plugins → Team Marketplaces → Add Marketplace → Import
from Repo** (Teams/Enterprise), or try it locally:

```bash
git clone https://github.com/0xcircuitbreaker/ddg-agent-plugins
mkdir -p ~/.cursor/plugins/local
cp -r ddg-agent-plugins/plugins/ddg-services ~/.cursor/plugins/local/
# reload window → Customize → check the plugin's components
```

## Verify the package

```bash
python3 scripts/validate.py
```

Checks the portable Agent Plugins 1.0 contract (`plugin.json` closed schema, name
rules, `skills/` discovery, `mcp.json` transport variants, path containment) and
that every client manifest resolves to a valid plugin directory with matching
names. Exit code 0 = pass. It prints the check count and the MCP endpoints it
validated.

## Layout

```text
ddg-agent-plugins/
├── .claude-plugin/marketplace.json     # Claude Code + VS Code + Codex (compat)
├── .cursor-plugin/marketplace.json     # Cursor multi-plugin repos
├── .agents/plugins/marketplace.json    # Codex native (policy/category)
├── plugins/
│   ├── ddg-services/
│   │   ├── plugin.json                 # Agent Plugins 1.0 manifest
│   │   ├── mcp.json                    # portable MCP config (streamable-http)
│   │   ├── .mcp.json                   # Claude Code native config
│   │   ├── .claude-plugin/plugin.json  # Claude Code shim
│   │   ├── .cursor-plugin/plugin.json  # Cursor shim
│   │   └── README.md
│   └── ddg-skills-starter/
│       ├── plugin.json
│       ├── .claude-plugin/plugin.json
│       ├── .cursor-plugin/plugin.json
│       ├── skills/<skill>/SKILL.md     # 5 skills
│       └── README.md
└── scripts/validate.py
```

The portable core (root `plugin.json` + `skills/` + `mcp.json`) is the same for
every client; the `.claude-plugin/`, `.cursor-plugin/`, and `.agents/` files only
carry distribution metadata and each client's native MCP shape.

## Related packages

* npm: `n8n-nodes-ddg-agent-services@0.1.0`
* PyPI: `ddg-langchain==0.1.0`
* Skills: [github.com/0xcircuitbreaker/agent-skills](https://github.com/0xcircuitbreaker/agent-skills)

## License

MIT
