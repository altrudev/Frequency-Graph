# Counterfactual 001: Identity unavailable

This is a **synthetic, deterministic, graph-native** evidence walkthrough, not an operational outage forecast or authorized remediation system.

## Primary live query contract

- `GET /api/scenario?id=identity-outage-001` queries FalkorDB for the scenario target, dependency reachability, a disputed decision and two evidence records, and a linked investigation memory record.
- `seed_scenario()` (operator action) merges the scenario, decision, evidence and fixed investigation record into FalkorDB. The public API cannot execute writes.
- The graph traversal returns potential dependency impact, not observed production failures. `SUPPORTED_BY` and `QUALIFIED_BY` edges distinguish evidence roles; these are fictional ADR records.
- There is **no inference model**, runtime change, autonomous agent, or user-created persistent investigations yet. The only persisted memory currently demonstrated is a fixed seeded investigation record.

## EDRG evidence

- Full VPS suite: 23 tests pass with the live database enabled.
- Idempotency check: running the seed twice yields an unchanged scenario result.
- Fail-closed check: `FALKORDB_PORT=9` produces `GraphError` and no scenario result, proving the native query needs the database.
- Public Altru.dev route: `/frequency-graph/counterfactual` serves a **static exported** result derived from live FalkorDB queries. This exported report can display without the DB, and must **not** be described as a live agent or interactive graph-native decision engine.

## Remaining for competition readiness

- Host the actual graph-native query flow behind a stable, authenticated first-party HTTPS API and wire the browser to it.
- Add an append-only authenticated investigation event model, provenance integrity and invalidation on graph change, then independently test memory and contradiction updates.
- Adversarial tests, GUI interactions, end-to-end wiring and release evidence with full pinned hashes. Record independent observation distinctly from query execution.
- Recheck current hackathon rules, deadline, eligible work window, and submission deliverables before claiming the entry is complete.

## Memory revision implementation (2026-10-15)

- `app/memory.py`: fixed, operator-seeded `EvidenceRevision` graph vertices and typed links from `Investigation` (`REVIEWED_REVISION`) and `Decision` (`REVISED_BY`). The read-only `GET /api/memory` endpoint queries those records and marks the conclusion qualified when a qualifying revision is present.
- Two persisted graph revisions: `REV-IDENTITY-BASELINE` and `REV-IDENTITY-QUALIFIED`. Seeding is idempotent; no public mutation interface is exposed.
- `FG_LIVE_TEST=1 FALKORDB_PORT=16379 python3 -m unittest discover -s tests -q` passed 28 tests, including graph-backed revision read, repeat-seed idempotence, and disconnected-database failure.
- Altru.dev `/frequency-graph/counterfactual` publishes the new evidence-revision results, but remains an **exported report**, not a live graph querying client.
- **Unresolved hosting prerequisite:** `graph.altru.dev` has no DNS record. Do not expose the private database port, reuse unrelated product APIs, or claim a live first-party browser integration until a stable domain/secure proxy is configured and end-to-end browser actions are independently accepted.
- No claims of autonomous agent memory, continuous evidence ingestion, runtime outage prediction, or production remediation are supported by the current implementation.
