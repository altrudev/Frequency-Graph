"""Read-only web API for graph investigations."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from .graph import GraphError, snapshot, impact, query, evidence
from .investigation import investigation, simulate_edge_removal
from .counterfactual import investigate_scenario
from .memory import history
from .factory_context import investigate_with_memory as investigate_factory

ROOT = Path(__file__).resolve().parent.parent
class Handler(BaseHTTPRequestHandler):
    def _headers(self, mime, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type",mime)
        self.send_header("Content-Length",str(len(data)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Content-Security-Policy","default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'")
        self.end_headers()
        if self.command != "HEAD": self.wfile.write(data)
    def _json(self, status, content):
        self._headers("application/json; charset=utf-8",json.dumps(content).encode(),status)
    def do_GET(self):
        url=urlsplit(self.path)
        try:
            if url.path=="/api/health":
                query("RETURN 1 AS ok")
                return self._json(200,{"status":"ok","database":"connected"})
            if url.path=="/api/graph": return self._json(200,snapshot())
            if url.path=="/api/memory":
                return self._json(200,history(parse_qs(url.query).get('id',['INV-IDENTITY-001'])[0]))
            if url.path=="/api/scenario":
                args=parse_qs(url.query)
                result=investigate_scenario(args.get('id',['identity-outage-001'])[0])
                if result and args.get('factory_agent',['0'])[0]=='1':
                    result['factory_agent']=investigate_factory(int(args.get('quantity',['5000'])[0]),float(args.get('stock',['10'])[0]))
                return self._json(200 if result else 404,result or {'error':'Scenario not found'})
            if url.path=="/api/evidence":
                ident=parse_qs(url.query).get("id",[""])[0]
                result=evidence(ident)
                return self._json(200 if result else 404,result or {"error":"Component not found"})
            if url.path=="/api/investigate":
                ident=parse_qs(url.query).get("id",[""])[0]
                result=investigation(snapshot(),ident)
                return self._json(200 if result else 404,result or {"error":"Component not found"})
            if url.path=="/api/simulate":
                args=parse_qs(url.query)
                result=simulate_edge_removal(snapshot(),args.get("source",[""])[0],args.get("target",[""])[0])
                return self._json(200 if result else 404,result or {"error":"Dependency not found"})
            if url.path=="/api/impact":
                ident=parse_qs(url.query).get("id",[""])[0]
                result=impact(ident)
                return self._json(200 if result else 404,result or {"error":"Component not found"})
            if url.path=="/api/about":
                return self._json(200,{"name":"Frequency Graph","creator":"Val Rukhaylo / Altru.dev","mode":"synthetic demonstration","ai_model":"none","authorization":"not implemented; no actions dispatched","license":"Apache-2.0"})
            if url.path=="/api/glossary":
                return self._json(200,json.loads((ROOT/"docs/glossary.json").read_text()))
            if url.path in ("/","/index.html","/style.css","/main.js","/brain.html","/brain.css","/brain.js"):
                name="brain.html" if url.path=="/" else url.path[1:]
                mime={"index.html":"text/html","style.css":"text/css","main.js":"text/javascript","brain.html":"text/html","brain.css":"text/css","brain.js":"text/javascript"}[name]
                return self._headers(mime+"; charset=utf-8",(ROOT/"static"/name).read_bytes())
            return self._json(404,{"error":"Not found"})
        except ValueError as exc: return self._json(400,{"error":str(exc)})
        except (GraphError,OSError): return self._json(503,{"error":"Graph service unavailable"})
        except BrokenPipeError: pass
    def do_HEAD(self): return self.do_GET()
    def do_POST(self):
        # Intentionally inaccessible through the public Caddy allowlist.
        if urlsplit(self.path).path!='/api/owner/episode':
            return self._json(405,{"error":"Public mutation and action execution are disabled"})
        from .factory_write import create_owned_episode
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=4096:return self._json(413,{"error":"Invalid request size"})
            if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':
                return self._json(415,{"error":"JSON required"})
            body=json.loads(self.rfile.read(size))
            bearer=self.headers.get('Authorization','')
            if not bearer.startswith('Bearer '):raise PermissionError('Bearer token required')
            outcome=create_owned_episode(body,bearer[7:])
            return self._json(201 if outcome['created'] else 200,outcome)
        except (PermissionError,):return self._json(403,{"error":"Unauthorized"})
        except (ValueError,TypeError,json.JSONDecodeError):return self._json(400,{"error":"Invalid episode request"})
        except (GraphError,OSError):return self._json(503,{"error":"Persistence unavailable"})

def serve():
    ThreadingHTTPServer((os.getenv("FG_BIND","127.0.0.1"),int(os.getenv("PORT","8080"))),Handler).serve_forever()
if __name__=="__main__": serve()
