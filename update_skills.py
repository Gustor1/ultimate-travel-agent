import os
import shutil

skills_data = {
    'travel-safety/SKILL.md': '''
## Direct Link Requirements & Regional Grounding Rules
- China: visa exemption 15-day (en.nia.gov.cn)
- Portugal: AIMA replacing SEF (aima.gov.pt, vistos.mne.gov.pt)
''',
    'transport-research/SKILL.md': '''
## Direct Link Requirements & Regional Grounding Rules
- London: TfL Contactless vs Oyster (tfl.gov.uk/fares)
- China: China Railway 12306 (12306.cn)
- Portugal: CP Portugal Promo fares (cp.pt), Easytoll/Via Verde (portugaltolls.com)
''',
    'accommodation-research/SKILL.md': '''
## Direct Link Requirements & Regional Grounding Rules
- China: PSB/?? foreign guest registration
- Portugal: RNET/Alojamento Local license check
''',
    'activity-curator/SKILL.md': '''
## Direct Link Requirements & Regional Grounding Rules
- London: free national museums (britishmuseum.org, nationalgallery.org.uk), HRP official ticketing (hrp.org.uk)
- Beijing: Forbidden City advance booking (dpm.org.cn)
- Portugal: Sintra Parques ticketing (bilheteira.parquesdesintra.pt)
''',
    'travel-web-research/SKILL.md': '''
## Direct Link Requirements & Regional Grounding Rules
- Mandatory direct URL standard
- <untrusted_web_content> isolation rule for Tier 5-6 sources
'''
}

paths = [
    r'C:\Users\eliot\Desktop\ultimate-travel-agent\.agents\skills',
    r'C:\Users\eliot\Desktop\ultimate-travel-agent\packages\travel-skills\skills'
]

for base_path in paths:
    for rel_path, addon in skills_data.items():
        file_path = os.path.join(base_path, rel_path)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '## Direct Link Requirements & Regional Grounding Rules' not in content:
                # Add before Example section if it exists
                if '## Example' in content:
                    content = content.replace('## Example', addon + '\n## Example')
                elif '## Examples' in content:
                    content = content.replace('## Examples', addon + '\n## Examples')
                else:
                    content += '\n' + addon
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

print("Skills updated.")
