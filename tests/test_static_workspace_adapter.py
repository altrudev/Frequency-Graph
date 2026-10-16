import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent


def first_party_workspace_bundle(adapter_source, workspace_source):
    """Compose the published snapshot adapter before the shared workspace script."""
    original="async function api(path){const r=await fetch(path,{cache:'no-store'}),body=await r.json();if(!r.ok)throw Error(body.error||r.status);return body}"
    if workspace_source.count(original)!=1:
        raise ValueError('Unexpected API client: refusing to publish')
    if 'window.FG_OFFLINE=' not in adapter_source:
        raise ValueError('Missing snapshot adapter')
    patched=workspace_source.replace(original,'async function api(path){return window.FG_OFFLINE(path)}')
    result=adapter_source+'\n'+patched
    if result.index('window.FG_OFFLINE=')>=result.index('async function api(path)'):
        raise ValueError('Invalid adapter initialization order')
    return result

class FirstPartyAdapterRegression(unittest.TestCase):
    def test_snapshot_adapter_replaces_live_fetch(self):
        source=(ROOT/'static/main.js').read_text()
        adapter='(function(){window.FG_OFFLINE=async function(path){return {}}})();'
        output=first_party_workspace_bundle(adapter,source)
        self.assertIn('async function api(path){return window.FG_OFFLINE(path)}',output)
        self.assertNotIn('await fetch(path',output)

    def test_missing_adapter_fails_closed(self):
        with self.assertRaises(ValueError):
            first_party_workspace_bundle('',(ROOT/'static/main.js').read_text())
