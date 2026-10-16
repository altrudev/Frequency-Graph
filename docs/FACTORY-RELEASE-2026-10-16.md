# Frequency Studio — factory release evidence (2026-10-16)

## Product / scope
Author: Val Rukhaylo / Altru.dev. Apache-2.0 project. The uploaded Frequency Agent Execution Assurance logo is user-provided branding; do not treat it as public-domain artwork or separate third-party licensing.

The factory is a SYNTHETIC demonstration workspace backed by FalkorDB for its canonical node/edge model. Public HTTPS permits GET/HEAD on a small allowlist only. End-user edits happen in browser memory, and saved user variants currently use localStorage, not a server-side account.

## Measured vs simulated
- Actual: source graph reads from FalkorDB, operator-written replay snapshots, browser graph editing, recipe propagation, independent code tests.
- Synthetic assumptions: 1.5 g sugar/bean, 0.075 g flavor/bean, up to 0.012 g pigment/bean, illustrative unit prices, 1,200-bean cooking capacity, 1,600-bean shaping capacity, 2,000-bean packaging capacity, 18-minute cooking cycle. All lack independent factory measurements. Fast/gentle multipliers are assumptions.
- No real recipe safety, nutrition, flavor perception, quality, production cost, waste rate, pricing currency, machine compatibility, inventory feeds or labor cost is established.
- Constructor offers bounded rule-based recipe transformations and capacity counterfactuals. It does not automatically build and certify real confectionery manufacturing equipment.
- Browser-only saved experiments are explicitly separate from operator-signed, graph-persisted snapshots.

## Governance and security
- No public POST actions or production dispatch.
- No public free-form Cypher interface. The operator-only recording API has fixed graph identity, bounded snapshot size, canonical digests and immutable experiment IDs.
- Deployment or execution authorization is NEVER implied by simulated improvements, Constructor suggestions, or verification of a toy model.
- A production multi-user persistence layer requires authentication, authorization, CSRF/replay protection, identity attribution, revision conflict control, quotas, and abuse prevention before being opened.

## What is release verified
- Application automated tests (consult current CI for count).
- Graph live availability at `/api/health`; public scenario includes synthetic factory graph and recorded experiment index.
- Browser opens root HTTPS and renders 11 factory nodes/8 initial relations.
- Existing browser interaction acceptance: disconnect/reconnect stage, ingredient substitution, pigment change, undo and reset.
- Tests of deterministic economics and immutable digest verification are included.

## Explicitly uncompleted release gates
- Validated confectionery manufacturing model, real inventory integration, calibrated throughput, production economics, external dataset connectors.
- Secure end-user server-side persistence and collaboration; current browser saves do not persist in FalkorDB.
- Independent adversarial multi-user penetration test, real touchscreen drag/port acceptance and accessibility audit.
- Signed execution attestations and authorized external actuators.
- Competition video production and final external submission are separate user-controlled steps.

## Terminology
- Frequency Studio = interactive graph editor and deterministic scenario runner.
- Living factory = directed graph of synthetic material/process dependencies.
- Constructor = bounded rule-driven candidate generation and what-if comparison.
- EDRG = evidence-driven release gate (automated proof checks, independent reproduction, adversarial validation).
- Experiment archive = immutable graph snapshot with content hash, not an industrial digital twin or production historian.
