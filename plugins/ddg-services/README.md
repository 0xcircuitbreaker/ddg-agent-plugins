# ddg-services

Remote MCP server for [DDG Agent Services](https://agents.daedalusdevelopmentgroup.com):
54 tools over one streamable-HTTP endpoint, backed by 376 live pay-per-call
x402 routes on USDC. No account, no API key, no human checkout.

```text
Endpoint: https://mcp.daedalusdevelopmentgroup.com/mcp
Server:   ddg-agent-services
Tools:    54
```

## Free tier — what costs nothing

| Free | How |
| --- | --- |
| Discovery | `ddg_search_services`, `ddg_list_services`, `ddg_security_service_catalog` |
| Status & conformance | `ddg_agent_status`, `ddg_checkout_conformance`, `ddg_x402scan_status` |
| Payment quotes | `ddg_quote_payment` — every 402 challenge is free to fetch and inspect |
| Rails & addresses | `ddg_x402_supported_chains`, `ddg_direct_crypto_addresses` |
| Public docs | `ddg_public_resource_index`, `ddg_fetch_public_resource`, `ddg_mcp_security_profile` |
| Trial call | A fresh agent id gets one free call per day on `web-search` and `price-feed` (the response carries a `payment-receipt: ft-…` header) |

So an agent can price, plan, and validate an integration without spending
anything. Nothing is charged until the agent itself supplies payment headers.

## Paid calls

Protected routes return a structured HTTP 402 with a `PAYMENT-REQUIRED` header
containing `accepts[]` (scheme, network, asset, amount, `payTo`). The agent pays
on-chain and replays the request with the payment header.

* Settlement: x402 over USDC — Base mainnet is the default (`eip155:8453`,
  USDC `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`); Polygon, Arbitrum, and
  World Chain are also accepted. `ddg_x402_supported_chains` returns the current list.
* Identity: protected routes require an agent identity header
  (`X-Agent-Id`, `X-DDG-Agent-Id`, or `X-DDG-User`). Missing identity returns
  403 before any payment is requested — no silent charges.
* Direct-crypto rails exist for manual/beta use; `ddg_direct_crypto_addresses`
  returns the public receiving addresses.
* `ddg_call` invokes any service by `service_id` or `/v1/` path; `ddg_receipt_*`
  and `ddg_order_*` tools track what was bought.

Route prices run from $0.001 (domain age, token metadata) to $0.01
(model compare, site audit). Full catalog and current prices:
`ddg_list_services` or `https://agents.daedalusdevelopmentgroup.com/openapi.json`.

## Example prompts once installed

```text
Find DDG services for checking whether a domain is old enough to trust.
Quote the payment for /v1/site-audit and show me the 402 challenge.
Which x402 chains does DDG accept, and what's the USDC contract on Base?
Run a free web search for "x402 facilitator health check" through DDG.
```

## Install

```text
/plugin install ddg-services@ddg-agent-plugins
```

Or without the marketplace, point any MCP client at the URL directly:

```json
{
  "mcpServers": {
    "ddg-agent-services": {
      "type": "streamable-http",
      "url": "https://mcp.daedalusdevelopmentgroup.com/mcp"
    }
  }
}
```

## Verify

```bash
curl -s -X POST https://mcp.daedalusdevelopmentgroup.com/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["result"]["tools"]), "tools")'
```

## Notes

* The server is stateless — no session id, no sticky state, safe behind retries.
* Paid calls are idempotency-key aware.
* Public resources exposed over MCP are allowlisted and redacted; no secrets are
  shipped in this package (see `mcp.json` — the only configured data is a URL).
