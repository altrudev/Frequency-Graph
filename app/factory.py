"""Synthetic, operator-seeded manufacturing graph. Public reads only."""
from .graph import _rows, query
NODES=[('sugar','Sugar','ingredient',0),('strawberry','Strawberry','flavor',0),('lemon','Lemon','flavor',0),('pink','Pink pigment','color',0),('yellow','Yellow pigment','color',0),('mixer','Mixing bowl','machine',1),('cooker','Cooking','machine',2),('molder','Jelly bean shapes','machine',3),('coater','Coating','machine',4),('pack','Packaging','machine',5),('out','Finished jelly beans','output',6),('apple','Apple','flavor',0),('green','Green pigment','color',0),('quality','Quality inspection','inspection',5),('warehouse','Ingredient storage','storage',0)]
LINKS=[('warehouse','sugar'),('sugar','mixer'),('strawberry','mixer'),('pink','mixer'),('mixer','cooker'),('cooker','molder'),('molder','coater'),('coater','quality'),('quality','pack'),('pack','out')]
def seed():
 for ident,name,kind,stage in NODES:
  query(f"MERGE (n:FactoryNode {{id:'{ident}'}}) SET n.name='{name}', n.kind='{kind}',n.stage={stage}",readonly=False)
 for ident,capacity in (('cooker',1200),('molder',1600),('pack',2000)):
  query(f"MATCH (n:FactoryNode {{id:'{ident}'}}) SET n.capacity={capacity}",readonly=False)
 for source,target in LINKS:
  query(f"MATCH (a:FactoryNode {{id:'{source}'}}),(b:FactoryNode {{id:'{target}'}}) MERGE (a)-[:FEEDS_INTO]->(b)",readonly=False)
def read():
 nodes=_rows(query('MATCH (n:FactoryNode) RETURN n.id,n.name,n.kind,n.stage ORDER BY n.stage,n.id LIMIT 60'))
 edges=_rows(query('MATCH (a:FactoryNode)-[:FEEDS_INTO]->(b:FactoryNode) RETURN a.id,b.id ORDER BY a.id,b.id LIMIT 120'))
 return {'nodes':[{'id':a,'name':b,'kind':c,'stage':int(d)} for a,b,c,d in nodes], 'edges':[{'from':a,'to':b} for a,b in edges], 'dataset':'SYNTHETIC_FACTORY','persistence':'GRAPH_READ_ONLY_PUBLIC','physical_validation':False}
if __name__=='__main__':
 seed();print(read())
