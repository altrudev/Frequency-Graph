"""Deterministic graph-native discovery and bounded counterfactual planner."""
import hashlib
import json
from math import ceil
from .factory import read
from .factory_economics import estimate
from .graph import _rows, query

def investigate(quantity=5000,stock_kg=10.0):
    if not isinstance(quantity,int) or not 100<=quantity<=5000: raise ValueError('Invalid quantity')
    if not isinstance(stock_kg,(int,float)) or not 1<=stock_kg<=10: raise ValueError('Invalid stock')
    graph=read()
    ids={n['id'] for n in graph['nodes']}
    edges={(e['from'],e['to']) for e in graph['edges']}
    chain=['mixer','cooker','molder','coater','pack','out']
    linked=all((a,b) in edges for a,b in zip(chain,chain[1:]))
    formula=('sugar','mixer') in edges and sum((v,'mixer') in edges for v in ('lemon','strawberry'))==1 and sum((v,'mixer') in edges for v in ('pink','yellow'))==1
    if not linked or not formula or len(ids)!=11: raise ValueError('Graph configuration is not a complete reproducible factory')
    # Capacities are attached to the corresponding graph stages, independently read from FalkorDB.
    rows=_rows(query("MATCH (n:FactoryNode) WHERE n.id IN ['cooker','molder','pack'] RETURN n.id,n.stage ORDER BY n.id"))
    stages={a:int(b) for a,b in rows}
    if stages!={'cooker':2,'molder':3,'pack':5}: raise ValueError('Graph stages differ from verified model')
    base=estimate(quantity,valid=True)
    feasible=quantity*1.5<=stock_kg*1000
    alternatives=[]
    for ident,title,oven,extra_units,verification in [
       ('BASE','Current production line',1200,0,'STRUCTURALLY_SUPPORTED'),
       ('SPLIT','Split batches; existing equipment',1200,0,'STRUCTURALLY_SUPPORTED'),
       ('UPGRADE','Hypothetical larger cooker',2000,500,'UNVERIFIED_EQUIPMENT')]:
        cycles=ceil(quantity/oven)
        minutes=cycles*18
        # Upgrade is a scenario branch, not a device in the live factory graph.
        valid=feasible and verification!='UNVERIFIED_EQUIPMENT'
        alternatives.append({'id':ident,'title':title,'cycles':cycles,'minutes':minutes,
          'material_cost_units':base['material_cost_units'],'one_time_cost_units':extra_units,
          'eligible':valid,'classification':verification,
          'reason':('Inventory short by '+str(round(quantity*1.5-stock_kg*1000))+' g' if not feasible else
             'New equipment capacity and safety are not verified' if not valid else 'Graph stage and inventory constraints satisfied')})
    eligible=[a for a in alternatives if a['eligible']]
    best=min(eligible,key=lambda a:(a['minutes'],a['one_time_cost_units'])) if eligible else None
    result={'request':{'quantity':quantity,'stock_kg':stock_kg},'graph':{'nodes':len(ids),'edges':len(edges),'stage_ids':sorted(stages)},
        'finding':{'bottleneck':'Cooking','capacity':1200,'cycles':base['cycles'],'inventory_feasible':feasible},
        'alternatives':alternatives,'recommendation':best['id'] if best else None,
        'dispatched':False,'approval':'NONE','basis':'SYNTHETIC_GRAPH_AND_DECLARED_ASSUMPTIONS'}
    result['sha256']=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()
    return result
