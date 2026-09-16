import os
import re

internal_agents = ['budget-analyst', 'itinerary-optimizer', 'quality-controller', 'travel-orchestrator', 'mcp-skill-auditor']
base_dir = r'C:\Users\eliot\Desktop\ultimate-travel-agent\.agents\agents'

for agent in internal_agents:
    filepath = os.path.join(base_dir, agent, 'agent.md')
    if not os.path.exists(filepath): continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parts = content.split("---", 2)
    if len(parts) >= 3:
        body = parts[2]
        body = re.sub(r'(?i)web_search', '', body)
        body = re.sub(r'(?i)web search', '', body)
        body = re.sub(r'(?i)browser', '', body)
        content = f"---{parts[1]}---{body}"
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Internal agents fixed.")
