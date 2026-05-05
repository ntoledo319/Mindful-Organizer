---
description: A description of your rule
---

---
name: never‑stop
# Give it a high priority so it overrides other rules if needed.
priority: 999

# 1) Remove almost all brakes on iteration count.
agent:
  maxIterations: 9999        # bump this higher if you REALLY want

# 2) Auto‑approve every tool invocation (no “Run? Y/N” prompts).
toolPolicies:
  - tool: "*"
    allow: true

# 3) Auto‑retry once when the model returns an ERROR or stops early.
trigger: post_response
script: |
  {% if "ERROR" in assistant_response or "Stopped due to max iterations" in assistant_response %}
  {{ send("continue") }}
  {% endif %}
...
