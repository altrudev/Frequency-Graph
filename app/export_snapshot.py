"""Generate a deterministic static snapshot for the first-party Altru.dev workspace.

Read-only source queries, atomic destination replacement, explicit origin metadata.
No automatic remote publication, user data, credentials, or live database access.
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from .graph import snapshot, evidence

def build_snapshot():
    graph = snapshot()
    ids = [n["id"] for n in graph["nodes"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate component identifiers")
    known = set(ids)
    if any(e["from"] not in known or e["to"] not in known for e in graph["edges"]):
        raise ValueError("Dangling graph edge")
    records = {name: evidence(name) for name in sorted(known)}
    if any(not e or e.get("verification") != "FIXTURE_RECORD_ONLY" for e in records.values()):
        raise ValueError("Unexpected evidence boundary")
    graph["nodes"] = sorted(graph["nodes"], key=lambda n: n["id"])
    graph["edges"] = sorted(graph["edges"], key=lambda e: (e["from"], e["to"]))
    return {"graph": graph, "evidence": records, "source": {
        "engine": "FalkorDB", "representation": "READ_ONLY_STATIC_EXPORT",
        "classification": "SYNTHETIC", "synchronized": False
    }}

def export(path, payload, timestamp=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    document = {**payload, "exported_at": timestamp, "sha256": digest}
    result = json.dumps(document, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("x", encoding="utf-8") as stream:
        stream.write(result)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    return digest

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("destination")
    args = parser.parse_args()
    print(export(args.destination, build_snapshot()))

if __name__ == "__main__":
    main()
