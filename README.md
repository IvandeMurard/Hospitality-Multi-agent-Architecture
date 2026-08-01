<h1 align="center">Hospitality Agentic Mesh</h1>
<p align="center">
  <em>Operational memory for hotel operations: A network of specialized AI agents that anticipate guest needs, evaluate autonomously, and learn from every service to optimize operations and cut costs.</em>
</p>

<p align="center">
  <a href="https://ivandemurard.com/aetherix">Case study</a> ·
  <a href="https://github.com/IvandeMurard/tacet-app">Tacet (public repo)</a> ·
  <a href="https://www.linkedin.com/in/ivandemurard/">Contact</a>
</p>

---

## The Vision: AI as a Living Operational Memory

This Hospitality Agentic Architecture turns AI into a **living operational memory**. Rather than just generating a static F&B forecast or a daily report, the Mesh acts as a living cognitive system for the property:
- **Understands, like a human:** Contextual reasoning grounded in each property's history, powered by a unified signal ontology that translates chaotic real-world events into structured, cross-domain context.
- **Measures, like a machine:** Every recommendation is stored next to its real outcome, so the system explicitly knows what it said versus what actually happened.
- **Learns, like a network:** Per-property memory today, federated priors next, leveraging shared intelligence to give independent hotels the power of a hive.

The individual forecasts and risk scores are just sensory organs. The true product and value lies in the **per-property memory** as it builds a compounding asset that continually optimizes operations, cuts waste, and elevates the guest experience.

## What this is

This is the public meta-repo of an multi-agent system I've been building solo since late 2025. It serves as the architectural blueprint for an event-driven network of AI agents designed for hotel operations.

At a glance:
- **A Multi-Agent System:** This repo documents the architecture and engineering practices, while the actual execution nodes (like Aetherix) live in separate repositories.
- **Perception Nodes:** Specialized agents that own strict bounded contexts. They expose their capabilities as [MCP](https://modelcontextprotocol.io) tools and focus purely on *understanding* data, never deciding.
- **Bespoke Orchestrator:** A central decision engine built entirely from scratch. It holds 100% of the reasoning loop to separate perception from action, ensuring a human manager is always the final authority.

## The Mesh Architecture

```mermaid
graph LR
    subgraph Nodes["Perception Nodes (Bounded Contexts)"]
        AN["Anima<br/>Guest Context & Cognition<br/>(4-layer temporal memory)"]
        A["Aetherix<br/>F&B Operations<br/>(Forecast, staffing, waste)"]
        T["Tacet<br/>Environmental Risk<br/>(Noise, events, transit)"]
    end
    O["Bespoke Orchestrator<br/>(Event-driven, the only<br/>decision maker)"]
    PMS["PMS / POS<br/>(Apaleo, Mews)"]
    M["Hotel Manager<br/>(WhatsApp, 1-tap validation)"]
    ML["Meta-Learner<br/>(Continuous improvement)"]

    O <-->|MCP tools| A
    O <-->|MCP tools| T
    O <-->|MCP tools| AN
    PMS --> O
    O -->|curated recommendations| M
    M -->|human feedback| ML
    PMS -->|autonomous ground-truth| ML
    ML -.->|recalibrates thresholds| O
```

### Core Design Principles

1. **Execution nodes never orchestrate.** The perception nodes (Anima, Aetherix, Tacet) strictly *interpret* signals within their domain. They never decide when to run or what action to take. The bespoke Orchestrator holds 100% of the decision logic.
2. **Glue, not replacement Delivery.** The Mesh operates via a PMS-agnostic canonical schema behind adapters. Intelligence is delivered directly inside the tools managers already use (e.g., 1-tap WhatsApp "receipts" summarizing the reasoning), requiring zero new dashboards to monitor.
3. **Preventing HITL (Human-in-the-Loop) Fatigue.** Human-in-the-loop is structural, but a manager bombarded with alerts will ignore them. The Orchestrator uses calibrated thresholds to filter out the noise, sending only high-significance, composite recommendations.
4. **Continuous Improvement (The Meta-Learner).** *(design — outcome capture is built in the F&B node, threshold calibration is not)* The intended dual learning strategy: every manager's 1-tap response (accept/reject) would train the thresholds, and an autonomous loop would compare past predictions against ground truth flowing back from the PMS/POS. Today the F&B node captures outcomes next to the forecasts that preceded them and recalibrates locally; the Orchestrator-level meta-learner is not built.
5. **Hive Memory (Federated Priors).** *(research)* To solve the cold-start problem, a federated "Hive" layer **would** share anonymized, learned priors across properties without leaking tenant data. This does not exist: what runs today is generic cross-property context patterns, not a federated prior. Calling it otherwise would overstate the system.

## The Nodes

### 🧠 Anima: The Relational Core (Guest Context)
Hospitality is fundamentally about the guest. Anima is the intelligence engine that allows the hotel to anticipate and personalize the experience as if every guest were a regular. It utilizes a **4-layer temporal memory** (Working, Episodic, Semantic, Segment) to prevent "over-fetching" context, ensuring the Orchestrator makes the *right gesture* for the *right guest* at the *right time*.

### 🍽️ Aetherix: F&B Execution
Aetherix anticipates staffing and F&B needs to cut food waste and control costs. It ingests historical data, weather, and local events to forecast operational pressure, issuing daily recommendations for kitchen prep and front-of-house staffing.

### 🌍 Tacet: Environmental Awareness
Tacet listens to the city. It monitors external risks—construction noise, transit strikes, and local events—translating chaotic real-world data into structured risk scores so the hotel can act proactively.

## What's built vs. what's vision

This is a solo project. The mesh narrative is a north star; some of it is built and some of it is not, and the difference is worth stating precisely rather than blurring.

Five labels, used consistently. **Built** = the code runs on its target environment — it does **not** mean anyone uses it. **Shadow-mode** = runs on real data, but no decision is delivered to a human from it. **Synthetic PoC** = validated on fabricated data only. **Design** = specified, not implemented. **Research** = exploration with no delivery commitment.

| Component | Status | Evidence — data, users |
|---|---|---|
| **Aetherix** (F&B Node) | **Built** (private): ~16.5k LOC, staging on Fly.io, 11 ADRs, 1.13:1 test ratio | Synthetic + sandbox data. **Zero real users to date.** |
| **Forecast engine** (inside Aetherix) | **Shadow-mode**: benchmarked on real data, no decision delivered from it | 829 real restaurants, 1,193 scored points — see [`benchmark/`](benchmark/) |
| **Tacet** (Environment Node) | **Synthetic PoC** (public): acoustic engine + ingestion pipeline, no CI | [Public Repo](https://github.com/IvandeMurard/tacet-app) |
| **Anima** (Guest Node) | **Synthetic PoC**: 4-layer temporal memory, MCP server, hackathon build (Jun 2026) | Synthetic cohort only. Never in production; production is DPIA-gated. |
| **Bespoke Orchestrator** | **Design**: proto-stub exists, the event-driven decision engine does not | Architectural ADRs |
| **Meta-Learner & federated Hive** | **Research**: no substrate built; the cohort-features foundation is frozen | Outcome capture (its prerequisite) is built in the F&B node |

## Engineering practices I'd bring to a team

I am building this Mesh solo from zero-to-one to master the full lifecycle of agentic AI systems. Beyond just stringing API calls together, this project demonstrates the structured engineering practices I'd bring to any full-time engineering role:

- **Full Ownership & Bespoke Control:** I build the critical path (like the Orchestrator) from scratch. When off-the-shelf frameworks obscure reasoning or limit control, I engineer bespoke solutions that keep the logic 100% transparent and deterministic.
- **Evals as merge gates, not dashboards.** Golden dataset plus an offline gate in CI (exit codes block the merge), separated by contract from runtime guardrails.
- **Typed failure reasons.** Every guardrail trip carries a machine-readable reason; "it degraded gracefully" is verifiable, not folklore.
- **Continuous discovery as a routine, not an event.** Every Monday morning: an automated scan of the market and competitive watchlist (PMS vendors, agentic startups, MCP ecosystem moves), followed by a proactive PM review session run with agent workflows. Findings feed a watchlist re-evaluated at each phase gate.
- **Incident response, practiced.** Handled a real leaked-secrets incident end-to-end: history rewrite, 11/11 credential rotation, GitHub Support purge, and post-mortem.
- **Tests outweigh code.** 1.13:1 test-to-app LOC ratio on the main node.

## Current focus (90-day plan, started July 2026)

1. **Proof:** real-data forecast benchmark ([`benchmark/`](benchmark/) — **done, and it did not flatter us**: on 829 real restaurants, Prophet beats a naive same-weekday baseline by 6.15 points of mean MAPE but **ties it on the median day**, and a gradient-boosted baseline wins outright on the median. Both readings published; the flattering one alone would not be true) • closed-loop demo on the Apaleo sandbox (forecast, recommendation, feedback, recalibration) • observability (Logfire traces, LLM cost per recommendation) • F&B manager interviews.
2. **Visibility:** this repo • a technical write-up on the blocking eval gate • a demo video.

## Stack

FastAPI • Python (async, Pydantic v2) • Supabase Postgres + pgvector (HNSW) • Prophet • Claude (multi-LLM provider abstraction) • Mistral embeddings • Redis (Upstash) • Twilio WhatsApp • Apaleo PMS (OAuth2) • Fly.io • GitHub Actions (CI + eval gate + schema-drift gate)

## License

MIT, see [LICENSE](LICENSE). The private node repos carry their own terms.
