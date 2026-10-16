# Live HTTPS graph deployment

Live service: `127.0.0.1:18080`, database: `127.0.0.1:16379`. Neither backend port should be publicly bound. The browser page lives at `https://graph.altru.dev/brain.html` once deployed.

**Infrastructure action required:** Create `graph.altru.dev` DNS A/AAAA entry pointing at the VPS public IP, then append `deploy/Caddyfile.graph` to the privileged Caddy configuration, validate with `caddy validate --config /etc/caddy/Caddyfile`, and reload Caddy. This action requires DNS administrator and privileged configuration access, not available to the unprivileged `ubuntu` remote agent. Do not alter existing payment hosts or paste secrets into the repository.

The supplied Caddy host exposes only GET/HEAD health, scenario, memory, and static Company Brain assets. The server itself denies POST and has no public Cypher endpoint. Do not market this demonstration as an authorization engine or production outage prediction.

Deployment acceptance: resolve DNS; GET public `/api/health`, `/api/scenario`, `/api/memory` and check JSON content type; load `/brain.html` in desktop and mobile browsers, verify the decision and evidence, refresh, check no error; POST to API must not mutate; disconnect database in isolated test and confirm no stale live results are shown; check other hosted applications remain healthy. Pin image version and create service supervision before production use.
