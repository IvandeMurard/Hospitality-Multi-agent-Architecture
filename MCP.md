# Aetherix MCP Server

The F&B node exposes its capabilities as MCP tools, so an orchestrator or any
MCP client can ask it for a forecast, recall what a property learned, or record
what actually happened. This page is the contract: what the tools are, what they
take, and what governs access.

**Status: Built, running on staging, zero real users.** The server works; nobody
depends on it yet. Access is by request rather than self-serve, and the
implementation lives in a private repository. Both facts are stated here rather
than discovered later.

## Endpoint

```
POST /mcp/v1/
Content-Type: application/json
Authorization: Bearer atx_<env>_<secret>
```

JSON-RPC 2.0, the subset MCP needs: `initialize`, `tools/list`, `tools/call`.
Every response carries `x-aetherix-mcp-version: 1`.

`/mcp/v0/` was retired on 2026-08-01 at the end of the Sunset window its own
response headers had announced. If you built against v0: the framing is
identical, `get_recommendations_with_memory_context` becomes `recall_memory`
(scope `memory:read`), and the other two tools are unchanged.

## Tools

| Tool | Scope | Rate limit | What it does |
|---|---|---|---|
| `get_operational_predictions` | `predict` | 60/min | Covers forecast and staffing for a target date |
| `recall_memory` | `memory:read` | 60/min | Semantic recall over the property's operational memory |
| `submit_feedback_to_memory` | `feedback` | 20/min | Records the manager's outcome for a past recommendation |

### get_operational_predictions

```json
{
  "target_date": "2026-08-14",
  "service_type": "dinner",
  "context": { "weather": {}, "events": [], "occupancy": 0.87 }
}
```

`target_date` is required. `service_type` is one of `breakfast`, `lunch`,
`dinner` and defaults to `dinner`. Everything in `context` is optional: supply
what you know, and the forecast uses what it is given.

### recall_memory

```json
{ "query": "rainy Friday during a trade fair", "k": 5 }
```

Free-text `query` (500 characters max), `k` between 1 and 20, default 5. It
returns the most relevant past observations for that property: what happened,
what was recommended, and how the manager responded.

### submit_feedback_to_memory

```json
{
  "recommendation_id": "4f1e…",
  "outcome": "modified",
  "actual_value": 92,
  "notes": "banquet booked late"
}
```

`outcome` is one of `accepted`, `rejected`, `modified`, `ignored`. This is the
call that closes the loop: without it the system predicts into the void.

## Multi-tenancy is not a parameter

`hotel_id` is resolved **server-side from the bearer token**. No tool schema
accepts it, and passing it anyway is ignored rather than honoured. A token can
only ever read and write its own property's data. This is deliberate: an
isolation boundary that a caller can set is not a boundary.

## What the server will refuse to do

- **It never acts.** Tools return recommendations and context. Booking, pricing
  and staffing decisions belong to a human, or to an orchestrator a human
  supervises.
- **It says when it does not know.** Low-confidence outputs are downgraded or
  flagged rather than dressed up, and every guardrail trip is logged with a
  machine-readable reason.
- **It refuses implausible input.** A POS export reporting 900 covers for a
  120-seat room is rejected before it can reach training data.

## Access

Tokens are issued per property, on request. There is no self-serve signup while
the node has no production users. Open an issue on this repo or use the contact
link in the [README](README.md), and say which tools you need and why.

## Related

- [README](README.md): the mesh, and what is built versus what is not
- [COGNITION.md](COGNITION.md): why the memory matters more than the forecast
- [benchmark/](benchmark/): how the forecast actually performs on real data,
  including where it does not beat a naive baseline
