import os
import re

test_path = r'C:\Users\eliot\Desktop\ultimate-travel-agent\tests\test_isolation_install.py'
if os.path.exists(test_path):
    with open(test_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # "4. Presence of all 11 agents." -> "4. Presence of all 12 agents."
    content = content.replace('11 agents', '12 agents')
    # assert res2["agents_count"] == 11 -> == 12
    content = content.replace('== 11', '== 12')
    
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("test_isolation_install.py updated.")
