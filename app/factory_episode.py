"""Operator-controlled graph memory with decision/evidence provenance and replay."""
import hashlib
import json
from .graph import query, _rows, GraphError, validate_id
from .factory_agent import investigate

def create_episode(identifier, quantity=5000, stock=10, prior=None, evidence='UNVERIFIED'):
    validate_id(identifier)
    if prior: validate_id(prior)
    if evidence not in ('UNVERIFIED','EQUIPMENT_CERTIFIED'):
        raise ValueError('Unknown evidence state')
    result=investigate(quantity,stock)
    # New documentary evidence authorizes consideration in a simulation only;
    # it never authorizes real equipment operation.
    if evidence=='EQUIPMENT_CERTIFIED' and result['finding']['inventory_feasible']:
        upgrade=next(x for x in result['alternatives'] if x['id']=='UPGRADE')
        upgrade['eligible']=True
        upgrade['classification']='DOCUMENTARY_CLAIM_NOT_PHYSICAL_VERIFICATION'
        upgrade['reason']='Synthetic equipment claim permits simulated comparison only; physical operation unauthorized'
        baseline=next(x for x in result['alternatives'] if x['id']=='BASE')
        if upgrade['minutes']<baseline['minutes']:
            result['recommendation']='UPGRADE_SIMULATION_ONLY'
    result['evidence_state']=evidence
    result['prior_episode']=prior
    result['sha256']=hashlib.sha256(json.dumps({k:v for k,v in result.items() if k!='sha256'},sort_keys=True).encode()).hexdigest()
    existing=_rows(query(f"MATCH (e:FactoryEpisode {{id:'{identifier}'}}) RETURN e.digest LIMIT 1"))
    if existing:
        if existing[0][0]!=result['sha256']: raise GraphError('Episode identity conflict')
        return {'id':identifier,'digest':result['sha256'],'created':False}
    if prior:
        old=read_episode(prior)
        if old is None: raise ValueError('Prior episode not found')
    # Base64 keeps serialized memory opaque to Cypher while content digest supports independent replay.
    import base64
    payload=base64.b64encode(json.dumps(result,sort_keys=True).encode()).decode()
    query(f"CREATE (e:FactoryEpisode {{id:'{identifier}',digest:'{result['sha256']}',body:'{payload}',evidence:'{evidence}',decision:'{result['recommendation'] or 'NONE'}'}})",readonly=False)
    query(f"MATCH (e:FactoryEpisode {{id:'{identifier}'}}),(n:FactoryNode {{id:'cooker'}}) MERGE (e)-[:INVESTIGATES]->(n)",readonly=False)
    if prior:
        query(f"MATCH (e:FactoryEpisode {{id:'{identifier}'}}),(p:FactoryEpisode {{id:'{prior}'}}) MERGE (e)-[:REVISITS]->(p)",readonly=False)
    return {'id':identifier,'digest':result['sha256'],'created':True}

def read_episode(identifier):
    validate_id(identifier)
    rows=_rows(query(f"MATCH (e:FactoryEpisode {{id:'{identifier}'}}) RETURN e.body,e.digest LIMIT 1"))
    if not rows: return None
    import base64
    try: result=json.loads(base64.b64decode(rows[0][0],validate=True))
    except (ValueError,UnicodeError,TypeError) as exc:raise GraphError('Episode data corrupted') from exc
    digest=hashlib.sha256(json.dumps({k:v for k,v in result.items() if k!='sha256'},sort_keys=True).encode()).hexdigest()
    if digest!=rows[0][1] or digest!=result.get('sha256'):raise GraphError('Episode digest mismatch')
    return result

def history():
    rows=_rows(query("MATCH (e:FactoryEpisode) RETURN e.id,e.digest,e.evidence,e.decision ORDER BY e.id LIMIT 20"))
    return [{'id':a,'sha256':b,'evidence':c,'decision':d} for a,b,c,d in rows]
