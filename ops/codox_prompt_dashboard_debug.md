# Codex Prompt: Dashboard Debugging (Saxony Drought Dashboard)

## Context

**Dashboard:** Streamlit-based hydrological drought dashboard for Paper #1
**Location:** `/data/.openclaw/workspace/open_claw_vibe_coding/dashboard/app.py`
**Status:** Running internally (localhost:8502) but not accessible externally

## Problem

Dashboard startet im Container, aber ist extern nicht erreichbar:
- ✅ `http://localhost:8502` — responds HTTP 200
- ✅ Streamlit process active (PID 54544)
- ❌ `http://187.124.13.209:8502` — connection timeout/blocked
- ❌ Browser access from host fails

## Expected Behavior

Dashboard should be accessible from:
1. Host machine browser
2. External network (for Julian to access)

## Debugging Tasks

### 1. Network Diagnostics
```bash
# Check if port is listening
ss -tlnp | grep 8502
netstat -tlnp | grep 8502

# Check firewall rules
iptables -L -n | grep 8502

# Check Docker port mapping
docker port openclaw-1lxa-openclaw-1

# Test connectivity
curl -v http://localhost:8502
curl -v http://172.18.0.2:8502
```

### 2. Streamlit Configuration
Check `app.py` server binding:
- `--server.address 0.0.0.0` (should bind all interfaces)
- `--server.port 8502`
- Consider adding `--server.enableCORS=false`
- Consider adding `--server.enableXsrfProtection=false` for testing

### 3. Docker/Container Networking
```bash
# Check container network config
docker inspect openclaw-1lxa-openclaw-1 | grep -A 20 "Ports"

# Check if port is published
docker ps | grep openclaw

# Test from host
docker exec openclaw-1lxa-openclaw-1 curl -s http://localhost:8502 | head -5
```

### 4. OpenClaw Gateway Config
Check if port forwarding is configured:
- `/data/.openclaw/config.yaml` — look for port mappings
- Gateway may need to publish 8502 to host

### 5. Application Errors
Check Streamlit logs:
```bash
cat /tmp/dashboard.log
# Look for: binding errors, CORS issues, import errors
```

### 6. Data File Issues
Dashboard may crash on load if data files missing:
```bash
# Check expected files
ls -la /data/.openclaw/workspace/open_claw_vibe_coding/analysis/results/test_domain/
ls -la /data/.openclaw/workspace/open_claw_vibe_coding/analysis/results/catchment_custom/
ls -la /data/.openclaw/workspace/open_claw_vibe_coding/analysis/results/Chemnitz2_0p0625/

# Check file format
head -5 /data/.openclaw/workspace/open_claw_vibe_coding/analysis/results/Chemnitz2_0p0625/drought_indices.csv
```

## Expected Output

1. **Root cause identified** (network binding, firewall, Docker port mapping, or data error)
2. **Fix applied** (config change, port publish, or code fix)
3. **Dashboard accessible** at `http://<host-ip>:8502` or via tunnel

## Constraints

- Work within OpenClaw container environment
- Do not restart OpenClaw gateway unless necessary
- Preserve existing dashboard code (app.py already updated)
- Data files exist for: test_domain, catchment_custom, Chemnitz2_0p0625

## Priority

**High** — Julian needs dashboard access for Paper #1 validation

---

**Start debugging now. Report findings incrementally.**
