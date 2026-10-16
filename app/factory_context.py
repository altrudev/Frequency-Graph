"""Graph-native investigation context and guarded simulation decision revision."""
from .factory_episode import read_episode
from .graph import query, _rows, GraphError
from .factory_agent import investigate

def context_for(quantity, stock):
    rows=_rows(query("MATCH (e:FactoryEpisode)-[:INVESTIGATES]->(n:FactoryNode {id:'cooker'}) "
                     "RETURN e.id,e.evidence,e.decision ORDER BY e.id LIMIT 30"))
    episodes=[]
    for ident,evidence,decision in rows:
        episode=read_episode(ident)
        if episode is None:raise GraphError('Graph memory missing episode')
        if episode['request']['quantity']==quantity:
            episodes.append({'id':ident,'evidence':evidence,'decision':decision,
                'digest':episode['sha256'],'stock':episode['request']['stock_kg']})
    return episodes

def investigate_with_memory(quantity=5000,stock=10.0):
    current=investigate(quantity,stock)
    episodes=context_for(quantity,stock)
    claimed=[e for e in episodes if e['evidence']=='EQUIPMENT_CERTIFIED']
    current['retrieved_episodes']=episodes
    current['provenance']=[{'episode':e['id'],'relationship':'INVESTIGATES',
                           'machine':'cooker','sha256':e['digest']} for e in episodes]
    current['memory_changed_outcome']=False
    current['memory_informed_candidate']=None
    if claimed and current['finding']['inventory_feasible']:
        # A past synthetic claim is enough to *introduce* a what-if candidate,
        # but not enough to verify equipment or permit a real-world upgrade.
        candidate=next(v for v in current['alternatives'] if v['id']=='UPGRADE')
        current['memory_informed_candidate']={
            'id':'UPGRADE_SIMULATION_ONLY','modeled_minutes':candidate['minutes'],
            'evidence_episode':claimed[-1]['id'],'eligible_for_execution':False}
        current['memory_changed_outcome']=True
        current['memory_observation']='Remembered synthetic equipment evidence changes the candidate investigation, not the authorized production plan.'
    else:
        current['memory_observation']='No relevant usable prior equipment evidence; retain the verified baseline candidate set.'
    return current
