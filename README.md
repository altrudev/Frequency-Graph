# Frequency Graph

**Evidence-driven organizational dependency explorer** — public reference application for FalkorDB Graph Hacks 2026.

**Creator:** Val Rukhaylo / Altru.dev · **License:** Apache-2.0

## What works

- Native FalkorDB graph queries through a small Python RESP2 client.
- Deterministic synthetic graph of six connected organizational systems.
- Bounded downstream impact traversal using Cypher.
- Interactive, keyboard-accessible graph exploration.
- Read-only investigation API, About section and standards-mapping glossary.
- Explicit distinction between **potential impact** and **authorization**.

**Not yet implemented:** authenticated governance decisions, live action dispatch, independent observation, cross-session agent memory, production deployment and a publicly verified HTTPS URL. This is a synthetic read-only reference implementation, not a production authorization system.

## Local requirements and setup

Python 3.10+ and an installed Podman or Docker engine with available memory. No external LLMs or Python pip packages are required.

```sh
podman run -d --name frequency-graph-db -p 127.0.0.1:16379:6379 \
  -v frequency-graph-data:/data docker.io/falkordb/falkordb:latest
export FALKORDB_PORT=16379
python3 -m app.seed
python3 -m unittest discover -s tests -v
FG_LIVE_TEST=1 python3 -m unittest discover -s tests -v
PORT=8080 FG_BIND=127.0.0.1 python3 -m app.server
```

Open `http://127.0.0.1:8080`. The database is intentionally loopback-only.

**Do not expose this reference server directly to the public internet.** Use a trusted reverse proxy, process supervision, network isolation and rate limiting after further security testing. Avoid using real organization data or privileged credentials.

## API

| Route | Behavior |
|---|---|
| `GET /api/health` | Verifies a live FalkorDB query |
| `GET /api/graph` | Returns bounded synthetic nodes and edges |
| `GET /api/impact?id=identity` | Finds potential downstream dependency impacts |
| `GET /api/about` | Product origin and truthful capability disclosure |
| `GET /api/glossary` | Machine-readable terminology crosswalk |
| `POST *` | Disabled (405); actions are not yet authorized or implemented |

## Transparency and licensing

Source files are Apache-2.0, including the complete license in [LICENSE](LICENSE). Third-party FalkorDB software retains its own license. Demo fixture data is synthetic; refer to [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for dependencies and attribution. Existing private DDC/Frequency runtimes are **not** included or licensed by this repository.

See [About](docs/ABOUT.md), [Glossary](docs/GLOSSARY.md), [Security](SECURITY.md) and [Contributing](CONTRIBUTING.md).


## Stable Altru.dev workspace (2026-10-14)

The first-party interactive workspace is accessible at [altru.dev/frequency-graph/workspace](https://altru.dev/frequency-graph/workspace). WHC serves a **read-only exported snapshot** of the live FalkorDB synthetic graph (24 nodes, 30 relationships), with deterministic browser-side investigation, hypothetical simulation, evidence lookup, and local browser history. It does **not** currently make live database queries from WHC; the VPS continues to serve the separate live graph API. Snapshot updates require explicit regeneration and publication through the existing authenticated site-operator transaction. The fixed first-party URL replaces reliance on the ephemeral Quick Tunnel for judge-facing navigation. The full browser-based adversarial gate and automated snapshot-sync pipeline remain pending.

## EDRG evidence

On 2026-10-14, the isolated VPS unit and live-database integration suite passed **5/5** tests, including graph seeding and dependency impact retrieval against a rootless Podman FalkorDB instance. The local HTTP health, graph, HTML and JS endpoints returned successful responses. These checks do **not** constitute public HTTPS, browser, persistence, concurrency or full adversarial acceptance.
