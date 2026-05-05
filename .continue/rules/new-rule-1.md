---
description: A description of your rule
---

---
name: memory-writeback
trigger: post_response
enabled: true
---
{% py("memory.upsert",
       {"id": ulid(), "type": "result", "content": assistant_response,
        "tags": "auto", "timestamp": now_iso()}) %}
