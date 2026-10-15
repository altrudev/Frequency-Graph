"""Minimal FalkorDB RESP2 client. No arbitrary Cypher is exposed to HTTP users."""
import os
import re
import socket

GRAPH_NAME = "frequency_graph"
IDENTIFIER = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

class GraphError(Exception):
    pass

def validate_id(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError("Invalid graph identifier")
    return value

def _read(stream):
    line = stream.readline()
    if not line or not line.endswith(b"\r\n"):
        raise GraphError("Malformed database response")
    tag, raw = line[:1], line[1:-2]
    if tag == b"+": return raw.decode()
    if tag == b"-": raise GraphError(raw.decode())
    if tag == b":": return int(raw)
    if tag == b"$":
        size = int(raw)
        if size < 0: return None
        value = stream.read(size)
        if len(value) != size or stream.read(2) != b"\r\n":
            raise GraphError("Malformed bulk response")
        return value.decode()
    if tag == b"*":
        size = int(raw)
        return None if size < 0 else [_read(stream) for _ in range(size)]
    raise GraphError("Unsupported RESP response")

def query(cypher, readonly=True):
    host = os.getenv("FALKORDB_HOST", "127.0.0.1")
    port = int(os.getenv("FALKORDB_PORT", "6379"))
    password = os.getenv("FALKORDB_PASSWORD")
    def command(sock, stream, args):
        encoded = [str(a).encode() for a in args]
        payload = b"*%d\r\n" % len(encoded)
        for value in encoded:
            payload += b"$%d\r\n" % len(value) + value + b"\r\n"
        sock.sendall(payload)
        return _read(stream)
    try:
        with socket.create_connection((host, port), timeout=3) as sock:
            sock.settimeout(5)
            with sock.makefile("rb") as stream:
                if password: command(sock, stream, ["AUTH", password])
                return command(sock, stream, ["GRAPH.RO_QUERY" if readonly else "GRAPH.QUERY", GRAPH_NAME, cypher, "TIMEOUT", "3000"])
    except (OSError, ValueError) as exc:
        raise GraphError("Database unavailable") from exc

def _rows(result):
    if not isinstance(result, list) or len(result) < 2:
        raise GraphError("Unexpected graph response")
    return [[v[1] if isinstance(v, list) and len(v) == 2 else v for v in row] for row in result[1]]

def snapshot():
    nodes = _rows(query("MATCH (n:Component) RETURN n.id, n.name, n.kind ORDER BY n.id LIMIT 150"))
    edges = _rows(query("MATCH (a:Component)-[:DEPENDS_ON]->(b:Component) RETURN a.id, b.id LIMIT 300"))
    return {"nodes":[{"id":str(a),"name":str(b),"kind":str(c)} for a,b,c in nodes],
            "edges":[{"from":str(a),"to":str(b)} for a,b in edges]}

def impact(component_id):
    component_id = validate_id(component_id)
    root = _rows(query(f"MATCH (n:Component {{id:'{component_id}'}}) RETURN n.id,n.name LIMIT 1"))
    if not root: return None
    affected = _rows(query(f"MATCH (n:Component {{id:'{component_id}'}})<-[:DEPENDS_ON*1..5]-(x:Component) RETURN DISTINCT x.id,x.name ORDER BY x.id LIMIT 150"))
    return {"target":{"id":str(root[0][0]),"name":str(root[0][1])},
            "affected":[{"id":str(a),"name":str(b)} for a,b in affected],
            "classification":"POTENTIAL_IMPACT","authorization":"NOT_EVALUATED","dispatched":False}

def seed():
    from .fixture import RECORDS, EDGES
    for ident,name,kind,evidence,note in RECORDS:
        safe_note=note.replace("'", "\\'")
        query(f"MERGE (n:Component {{id:'{ident}'}}) SET n.name='{name}',n.kind='{kind}',n.evidence='{evidence}',n.note='{safe_note}'",readonly=False)
    for source,target in EDGES:
        query(f"MATCH (a:Component {{id:'{source}'}}),(b:Component {{id:'{target}'}}) MERGE (a)-[:DEPENDS_ON]->(b)",readonly=False)
    return snapshot()

def evidence(component_id):
    component_id=validate_id(component_id)
    rows=_rows(query(f"MATCH (n:Component {{id:'{component_id}'}}) RETURN n.id,n.name,n.evidence,n.note LIMIT 1"))
    if not rows: return None
    row=rows[0]
    return {'component':row[0],'name':row[1],'source_id':row[2], 'excerpt':row[3],
            'source_class':'SYNTHETIC_ADR','verification':'FIXTURE_RECORD_ONLY',
            'disclaimer':'Synthetic rationale is not independent proof of production behavior.'}
