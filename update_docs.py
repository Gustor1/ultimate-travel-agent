import os
import re

# Update packages/travel-skills/README.md
readme_path = r'C:\Users\eliot\Desktop\ultimate-travel-agent\packages\travel-skills\README.md'
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'6-skill', '13-skill', content)
    content = re.sub(r'6 obsolete', '13', content)
    content = re.sub(r'obsolete 6', '13', content)
    content = content.replace('6 skills', '13 skills')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

# Update docs/decisions.md
decisions_path = r'C:\Users\eliot\Desktop\ultimate-travel-agent\docs\decisions.md'
adr_content = '''
## ADR 013: Phase 13 - Regional Grounding & Security Hardening
**Date:** 2026-09-16
**Status:** Accepted
**Context:** Need to ensure regional accuracy for China, Portugal, and London, and harden agent security (least privilege, untrusted web content handling).
**Decision:** Added specific rules to skills for these regions, created source-verification agent, and restricted internal agents from using web tools.
**Consequences:** Safer and more accurate AI travel research.
'''
if os.path.exists(decisions_path):
    with open(decisions_path, 'a', encoding='utf-8') as f:
        f.write('\n' + adr_content)

# Update docs/progress.md
progress_path = r'C:\Users\eliot\Desktop\ultimate-travel-agent\docs\progress.md'
if os.path.exists(progress_path):
    with open(progress_path, 'a', encoding='utf-8') as f:
        f.write('\n- [x] Phase 13: Regional Grounding & Security Hardening\n')

print("Docs updated.")
