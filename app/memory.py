"""FalkorDB-backed versioned evidence and investigation event history.

Operator-originated fixed-fixture revisions only. Public API is read-only.
"""
from .graph import query, _rows, validate_id

EVENTS = {
    'baseline': ('REV-IDENTITY-BASELINE', 'Identity architecture originally assumes universal dependency', 'BASELINE'),
    'qualification': ('REV-IDENTITY-QUALIFIED', 'Direct identity requirement and gateway dependency are distinct assumptions', 'QUALIFICATION'),
}

def seed_revision(key):
    if key not in EVENTS: raise ValueError('Unknown evidence revision')
    revision, message, status = EVENTS[key]
    # Fixed server-authored strings, not interpolation of arbitrary untrusted Cypher.
    query(f"MERGE (r:EvidenceRevision {{id:'{revision}'}}) SET r.message='{message}',r.status='{status}',r.classification='SYNTHETIC'",readonly=False)
    query(f"MATCH (i:Investigation {{id:'INV-IDENTITY-001'}}),(r:EvidenceRevision {{id:'{revision}'}}) MERGE (i)-[:REVIEWED_REVISION]->(r)",readonly=False)
    if key == 'qualification':
        query("MATCH (d:Decision {id:'DEC-IDENTITY-001'}),(r:EvidenceRevision {id:'REV-IDENTITY-QUALIFIED'}) MERGE (d)-[:REVISED_BY]->(r)",readonly=False)
    return revision

def history(investigation_id='INV-IDENTITY-001'):
    validate_id(investigation_id)
    rows=_rows(query(f"MATCH (i:Investigation {{id:'{investigation_id}'}})-[:REVIEWED_REVISION]->(r:EvidenceRevision) RETURN r.id,r.message,r.status ORDER BY r.id LIMIT 50"))
    return {'investigation_id':investigation_id,'revisions':[{'id':r,'statement':m,'type':s} for r,m,s in rows],
            'changed':any(s=='QUALIFICATION' for _,_,s in rows),'classification':'SYNTHETIC_EVIDENCE_REVISION', 'dispatched':False}
