"""Graph-native counterfactual scenario: no public mutation or model inference."""
from .graph import query, _rows, validate_id, GraphError, snapshot
from .investigation import investigation

SCENARIO = 'identity-outage-001'

def seed_scenario():
    # Immutable, synthetic fixture lineage; seeded by operator, not web requests.
    query("MERGE (s:Scenario {id:'identity-outage-001'}) SET s.title='Identity service unavailable', s.assumption='Identity unavailable', s.classification='SYNTHETIC'", readonly=False)
    query("MERGE (d:Decision {id:'DEC-IDENTITY-001'}) SET d.title='Require identity for every service',d.state='disputed'", readonly=False)
    query("MERGE (e:Evidence {id:'EVD-IDENTITY-001'}) SET e.summary='Identity required by dependent components',e.classification='SYNTHETIC',e.source='ADR-001'",readonly=False)
    query("MERGE (f:Evidence {id:'EVD-IDENTITY-002'}) SET f.summary='Portal also reaches gateway but has a direct identity dependency',f.classification='SYNTHETIC',f.source='ADR-003'",readonly=False)
    query("MATCH (s:Scenario {id:'identity-outage-001'}),(n:Component {id:'identity'}) MERGE (s)-[:TARGETS]->(n)",readonly=False)
    query("MATCH (s:Scenario {id:'identity-outage-001'}),(d:Decision {id:'DEC-IDENTITY-001'}) MERGE (s)-[:CHALLENGES]->(d)",readonly=False)
    query("MATCH (d:Decision {id:'DEC-IDENTITY-001'}),(e:Evidence {id:'EVD-IDENTITY-001'}) MERGE (d)-[:SUPPORTED_BY]->(e)",readonly=False)
    query("MATCH (d:Decision {id:'DEC-IDENTITY-001'}),(e:Evidence {id:'EVD-IDENTITY-002'}) MERGE (d)-[:QUALIFIED_BY]->(e)",readonly=False)
    query("MERGE (m:Investigation {id:'INV-IDENTITY-001'}) SET m.scenario='identity-outage-001',m.status='recorded',m.classification='SYNTHETIC'",readonly=False)
    query("MATCH (m:Investigation {id:'INV-IDENTITY-001'}),(s:Scenario {id:'identity-outage-001'}) MERGE (m)-[:EXAMINES]->(s)",readonly=False)


def investigate_scenario(scenario_id=SCENARIO):
    validate_id(scenario_id)
    if scenario_id != SCENARIO: return None
    rows=_rows(query("MATCH (s:Scenario {id:'identity-outage-001'})-[:TARGETS]->(n:Component) RETURN s.id,s.title,n.id,n.name LIMIT 1"))
    if not rows:return None
    sid,title,target,targetname=rows[0]
    affected=_rows(query("MATCH (s:Scenario {id:'identity-outage-001'})-[:TARGETS]->(n:Component)<-[:DEPENDS_ON*1..6]-(c:Component) RETURN DISTINCT c.id,c.name ORDER BY c.id LIMIT 100"))
    linked=_rows(query("MATCH (s:Scenario {id:'identity-outage-001'})-[:CHALLENGES]->(d:Decision)-[r:SUPPORTED_BY|QUALIFIED_BY]->(e:Evidence) RETURN d.id,d.title,type(r),e.id,e.source,e.summary ORDER BY e.id LIMIT 20"))
    memory=_rows(query("MATCH (m:Investigation)-[:EXAMINES]->(s:Scenario {id:'identity-outage-001'}) RETURN m.id,m.status LIMIT 10"))
    traced=investigation(snapshot(),target)
    path_by_source={x['source']:x['ids'] for x in traced['paths']}
    # Existing dependency edges remain explicitly classified as topology, not incidents.
    return {'scenario':{'id':sid,'title':title,'target':target,'target_name':targetname},
       'affected':[{'id':a,'name':n,'path':path_by_source.get(a,[])} for a,n in affected],
       'evidence':[{'decision':d,'decision_title':t,'relation':rel,'id':eid,'source':src,'summary':summary} for d,t,rel,eid,src,summary in linked],
       'memory':[{'id':a,'status':b} for a,b in memory],
       'classification':'GRAPH_DERIVED_SYNTHETIC_COUNTERFACTUAL','dispatched':False,
       'uncertainties':['Dependency path does not prove runtime failure','Synthetic documents do not independently corroborate architecture','No authorization to change production systems']}
