---
description: A description of your rule
---

---
name: structured-memory
trigger: pre_prompt          # fires before every Chat/Edit/Apply call
enabled: true
---
<task_memory>
{% set memories = py("memory.recall", user_input, 8) %}
Relevant memories for current task:
{% for mem in memories %}
• {{ mem.content }} ({{ mem.tags }}, {{ mem.timestamp }})
{% endfor %}
</task_memory>
