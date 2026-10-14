"""Pure, deterministic graph analysis; hypothetical operations never mutate FalkorDB."""
from collections import deque
from .graph import validate_id

def _adjacency(graph, exclude=None):
    result={n['id']:set() for n in graph['nodes']}
    for edge in graph['edges']:
        if exclude != (edge['from'],edge['to']) and edge['from'] in result and edge['to'] in result:
            result[edge['from']].add(edge['to'])
    return result

def _walk(start, adjacency, reverse=False, max_depth=8):
    links={key:set() for key in adjacency}
    for src, dests in adjacency.items():
        for dst in dests:
            (links[dst] if reverse else links[src]).add(src if reverse else dst)
    visited={start:[start]}
    queue=deque([start])
    while queue:
        cur=queue.popleft()
        if len(visited[cur])-1>=max_depth: continue
        for nxt in sorted(links.get(cur,())):
            if nxt not in visited:
                visited[nxt]=visited[cur]+[nxt]
                queue.append(nxt)
    return visited

def investigation(graph, target):
    target=validate_id(target)
    names={n['id']:n['name'] for n in graph['nodes']}
    if target not in names: return None
    graph_paths=_walk(target,_adjacency(graph),reverse=True)
    return {'target':{'id':target,'name':names[target]},
            'paths':[{'source':x,'name':names[x],'ids':list(reversed(path)),'depth':len(path)-1}
                     for x,path in sorted(graph_paths.items(),key=lambda p:(len(p[1]),p[0])) if x!=target],
            'mode':'OBSERVED_GRAPH_REACHABILITY','authorization':'NOT_EVALUATED','dispatched':False}

def simulate_edge_removal(graph, source, target):
    source=validate_id(source);target=validate_id(target)
    names={n['id']:n['name'] for n in graph['nodes']}
    before=_adjacency(graph)
    if source not in names or target not in names or target not in before[source]: return None
    after=_adjacency(graph,exclude=(source,target))
    b=_walk(source,before);a=_walk(source,after)
    lost=sorted(set(b)-set(a)); retained=sorted(set(b)&set(a)-{source})
    return {'proposal':{'operation':'REMOVE_DEPENDENCY','source':source,'target':target},
            'before_reachable':len(b)-1,'after_reachable':len(a)-1,
            'lost_reachability':[{'id':x,'name':names[x],'path':b[x]} for x in lost],
            'retained_reachability':[{'id':x,'name':names[x],'path':a[x]} for x in retained],
            'classification':'HYPOTHETICAL_GRAPH_ONLY','authorization':'NOT_EVALUATED',
            'mutated':False,'dispatched':False}
