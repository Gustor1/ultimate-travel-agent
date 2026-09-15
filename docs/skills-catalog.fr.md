# Catalogue des Skills de Voyage

Liste exhaustive des 13 skills spécialisées incluses dans `ultimate-travel-agent`.
Toutes les skills sont locales, open source (licence MIT) et compatibles avec Antigravity.

---

| Nom de la Skill | Rôle principal | Outils requis | Résultat produit |
|---|---|---|---|
| `travel-orchestrator` | Pilote les 5 vagues de planification et synthétise le dossier | `filesystem_read`, `local_calculation` | Dossier de voyage final sourcé |
| `travel-web-research` | Étudie le climat, les coutumes et les créneaux anti-foule | `web_search`, `browser`, `filesystem_read` | Profil de destination & matrice saisonnière |
| `transport-research` | Compare les transports porte-à-porte (train, vol, route, ferry) | `web_search`, `browser`, `local_calculation` | Matrice comparative multi-modale |
| `accommodation-research` | Évalue les quartiers sûrs et sélectionne 3-5 hébergements | `web_search`, `browser`, `filesystem_read` | Short-list d'hébergements vérifiés |
| `activity-curator` | Conçoit le programme d'activités avec plans B mauvais temps | `web_search`, `browser`, `local_calculation` | Catalogue d'activités & alternatives pluie |
| `local-discovery` | Repère les adresses de quartier et restos authentiques | `web_search`, `browser`, `filesystem_read` | Pépites locales (Tier 4-6) |
| `itinerary-builder` | Construit le planning jour par jour avec regroupements géographiques | `filesystem_read`, `local_calculation` | Itinéraire chronologique détaillé |
| `budget-and-booking-checker` | Consolide les coûts, ajoute 10-15 % de réserve et liste les réservations | `filesystem_read`, `local_calculation` | Budget ventilé & calendrier des réservations |
| `travel-safety` | Contrôle visas, passeports, vaccins et consignes d'urgence | `web_search`, `browser`, `filesystem_read` | Checklist formalités, santé et sécurité |
| `source-verification` | Recoupe chaque affirmation selon la hiérarchie en 6 tiers | `web_search`, `browser`, `filesystem_read` | Journal d'audit et de vérification |
| `travel-quality-control` | Audite la cohérence temporelle, les trajets et le budget | `filesystem_read`, `local_calculation` | Rapport de validation & corrections |
| `multi-agent-orchestration` | Modélise les topologies de communication multi-agents | `filesystem_read`, `local_calculation` | Plan d'orchestration en 5 vagues |
| `mcp-skill-auditing` | Audite la sécurité des outils et serveurs MCP externes | `filesystem_read`, `web_search` | Rapport d'audit de sécurité des outils |
