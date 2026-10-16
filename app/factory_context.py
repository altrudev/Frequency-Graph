"""Graph-native retrieval and provenance for new synthetic investigations.

Read-only on the public path. No claim of physical equipment certification.
"""
from .factory_episode import read_episode
from .graph import query, _rows, validate_id, GraphError
from .factory_agent import investigate

def context_for(quantity, stock):
    # Graph traversal is the source of context; no fixture identifiers are hardcoded.
    rows=_rows(query(
      "MATCH (e:FactoryEpisode)-[:INVESTIGATES]->(n:FactoryNode {id:'cooker'}) "
      "RETURN e.id,e.evidence,e.decision ORDER BY e.id LIMIT 30"))
    episodes=[]
    for ident, evidence, decision in rows:
        prior=read_episode(ident)
        if prior is None: raise GraphError('Graph memory missing its recorded episode')
        if prior['request']['quantity']==quantity:
            episodes.append({'id':ident,'evidence':evidence,'decision':decision,
                 'digest':prior['sha256'],'stock':prior['request']['stock_kg']})
    return episodes

def investigate_with_memory(quantity=5000,stock=10.0):
    current=investigate(quantity,stock)
    episodes=context_for(quantity,stock)
    # An older documentary claim is provenance, not current equipment authorization.
    relevant=[e for e in episodes if e['evidence']=='EQUIPMENT_CERTIFIED']
    current['retrieved_episodes']=episodes
    current['memory_observation']=(
       'Earlier synthetic evidence claims an upgraded cooker could improve the plan; '
       'physical validation is still absent. Review the linked episode before changing equipment.'
       if relevant else
       'No previous equipment claim found for this batch size; base-plan constraints remain applicable.')
    current['memory_changed_outcome']=False
    current['provenance']=[
       {'episode':e['id'],'relationship':'INVESTIGATES','machine':'cooker','sha256':e['digest']}
       for e in episodes]
    return current
