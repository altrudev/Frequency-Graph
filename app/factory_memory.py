"""Operator-only immutable factory experiment records; never exposed as public write API."""
import base64
import hashlib
import json
from datetime import datetime, timezone
from .graph import GraphError, _rows, query, validate_id

def canonical_snapshot(nodes,edges,options):
    ids={n['id'] for n in nodes}
    if not ids or len(ids)!=len(nodes):
        raise ValueError('Duplicate or empty factory node set')
    if any(e['from'] not in ids or e['to'] not in ids for e in edges):
        raise ValueError('Unknown node in a factory relationship')
    if len(edges)>120 or len(nodes)>60:
        raise ValueError('Graph exceeds bounded experiment limits')
    payload={'nodes':sorted(nodes,key=lambda n:n['id']),
             'edges':sorted(edges,key=lambda e:(e['from'],e['to'])),
             'options':options}
    return json.dumps(payload,sort_keys=True,separators=(',',':'))

def record_experiment(identifier,nodes,edges,options):
    validate_id(identifier)
    payload=canonical_snapshot(nodes,edges,options)
    digest=hashlib.sha256(payload.encode()).hexdigest()
    encoded=base64.b64encode(payload.encode()).decode('ascii')
    from .factory import read
    live=read()
    if {n['id'] for n in nodes}!={n['id'] for n in live['nodes']}:
        raise ValueError('Unexpected factory node identity')
    # An identifier is immutable: refuses recording a different digest under the same ID.
    existing=_rows(query(f"MATCH (e:FactoryExperiment {{id:'{identifier}'}}) RETURN e.digest LIMIT 1"))
    if existing:
        if existing[0][0]!=digest:raise GraphError('Experiment ID already used for different contents')
        return {'id':identifier,'digest':digest,'recorded':False}
    # Store only validated hex digest + allowlisted identity. Snapshot remains exported in the
    # operator's immutable source file; graph retains reference and revision lineage.
    query(f"CREATE (e:FactoryExperiment {{id:'{identifier}',digest:'{digest}',snapshot_b64:'{encoded}',scope:'SYNTHETIC',authorized:false}})",readonly=False)
    query(f"MATCH (e:FactoryExperiment {{id:'{identifier}'}}),(n:FactoryNode {{id:'mixer'}}) MERGE (e)-[:INVESTIGATES]->(n)",readonly=False)
    return {'id':identifier,'digest':digest,'recorded':True}

def list_experiments():
    rows=_rows(query("MATCH (e:FactoryExperiment) RETURN e.id,e.digest,e.scope ORDER BY e.id LIMIT 30"))
    return [{'id':a,'sha256':b,'scope':c} for a,b,c in rows]

def replay(identifier):
    validate_id(identifier)
    rows=_rows(query(f"MATCH (e:FactoryExperiment {{id:'{identifier}'}}) RETURN e.snapshot_b64,e.digest LIMIT 1"))
    if not rows:return None
    encoded,digest=rows[0]
    try: decoded=base64.b64decode(encoded,validate=True).decode('utf-8')
    except (ValueError,UnicodeDecodeError) as exc: raise GraphError('Corrupt graph experiment payload') from exc
    if hashlib.sha256(decoded.encode()).hexdigest()!=digest:raise GraphError('Graph experiment digest mismatch')
    return json.loads(decoded)
