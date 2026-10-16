# Constructor output — identity failover candidate

This is the exact fixed-recipe candidate produced by the operator-only `python -m app.constructor` workflow. It is **in-memory only**, uses no network or external identity providers, and is **not a deployable failover solution**.

Run the independent verification: `python verify.py` from this directory. Five tests cover healthy primary, verified standby, unverified standby rejected, total outage rejected, and primary preference.

The generated `candidate.py` SHA-256 should be `d0f19cf99d2425d603f896595a00a70a960fd8365349798b0bbc6105e9f275b7`. A passing test creates no production authorization. The FalkorDB candidate node stores the digest, result, applicability and explicit false deployment/authorization flags; no arbitrary public recipe selection or code execution is exposed.
