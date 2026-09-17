# Modèle de Sécurité et de Confidentialité — `ultimate-travel-agent`

Ce document formalise les principes directeurs, les garde-fous stricts, le cloisonnement des permissions et le modèle de menace (*threat model*) régissant l'écosystème multi-agents et les compétences du **Travel Skills Pack**.

---

## 1. Principes Fondamentaux de Sécurité

1. **Principe de Moindre Privilège (*Least Privilege*) :**
   - **Cloisonnement strict des sous-agents :**
     - Les agents internes (`budget-analyst`, `itinerary-optimizer`, `quality-controller`, `travel-orchestrator`, `mcp-skill-auditor`) opèrent exclusivement avec des outils de lecture locale (`filesystem_read`). Ils ont l'interdiction formelle de disposer d'outils web (`web_search`, `browser`).
     - Seuls les agents de recherche terrain (`destination-researcher`, `transport-planner`, `accommodation-researcher`, `activity-curator`, `local-discovery-agent`, `travel-preparation-agent`, `source-verification`) disposent des outils de recherche web et de navigation.
   - **Zéro accès au shell système :** Aucun agent ne dispose d'accès direct au terminal système (`run_command`), ni de permissions d'écriture arbitraires sur la machine hôte.

2. **Défense en Profondeur (*Defense in Depth*) & Isolation des Données Web :**
   - Tout contenu externe issu du web (pages d'opérateurs, guides, forums, résultats de moteurs de recherche) est classé comme **non fiable (*untrusted*)**.
   - Les agents web appliquent une isolation systématique via des balises de cloisonnement `<untrusted_web_content>` pour neutraliser les injections de prompt indirectes.
   - Interdiction formelle d'incorporer des données nominatives personnelles ou des PII (*Personally Identifiable Information*).
   - Contrôle qualité indépendant opéré en Vague 4 par `quality-controller` et `source-verification`.

3. **Zéro Action Matérielle Irréversible (Zéro Réservation / Zéro Achat) :**
   - **Interdiction absolue d'achat et de réservation automatique :** Le système ne déclenche aucun paiement, aucun débit bancaire, aucune signature contractuelle et aucune réservation autonome.
   - **Délivrance exclusive de liens officiels certifiés :** L'agent fournit des liens profonds vers les plateformes officielles certifiées des transporteurs et billetteries (Tier 1 et Tier 2) accompagnés d'instructions de réservation pas-à-pas, laissant la décision et le contrôle exclusif à l'utilisateur humain (*Human-in-the-loop*).
   - **Interdiction des OTA pour les vols :** Les plateformes intermédiaires (Expedia, Opodo, Kiwi) et les comparateurs (Google Flights, Skyscanner, Trip.com) sont strictement proscrits comme liens de réservation de vols.

4. **Souveraineté des Données et Repli Hors-Ligne :**
   - Aucune donnée personnelle sensible (numéro de passeport, carte d'identité, coordonnées bancaires) n'est manipulée, transmise ou stockée.
   - En l'absence d'outils de recherche web, toutes les skills basculent sur un protocole de repli déterministe avec mention explicite *« estimation, inventaire non ouvert »* ou *« données non confirmées »*, interdisant formellement l'invention de tarifs ou d'horaires en direct.

---

## 2. Modèle de Menace (*Threat Model*) et Risques Spécifiques

| Vecteur de Risque | Scénario d'Attaque / Défaillance | Mesure de Protection Active |
| :--- | :--- | :--- |
| **Injection de Prompt Indirecte (*Indirect Prompt Injection*)** | Une page web touristique ou un avis communautaire contient des instructions textuelles masquées visant à détourner le comportement de l'agent. | Encapsulation systématique dans `<untrusted_web_content>`, interdiction d'exécuter des instructions issues des pages web, audit de sécurité par `mcp-skill-auditor`. |
| **Fuite de PII ou de Secrets** | Un agent tente d'extraire des identifiants locaux, clés d'API ou chemins Windows/macOS. | Filtrage des mots-clés PII, exclusion des fichiers sensibles via `.gitignore`, tests automatisés vérifiant l'absence totale de clés d'API et de chemins personnels dans le dépôt. |
| **Hallucination Financière ou Phishing de Billetterie** | L'IA invente un tarif fictif, un domaine trompeur ou renvoie vers un revendeur non officiel. | Pyramide stricte des sources en 6 tiers (Tier 1 ministères, Tier 2 transporteurs officiels), vérification des URLs profondes, double contrôle par `source-verification`. |
| **Altération Accidentelle des Données Utilisateur** | L'installation ou la désinstallation du pack de compétences écrase ou supprime les compétences personnalisées de l'utilisateur. | Suivi d'empreintes cryptographiques SHA-256 via `.agents/.ultimate-travel-agent-install.json`, préservation absolue de tous les fichiers créés ou modifiés par l'utilisateur. |
| **Exécution de Code Non Contrôlée** | Une skill tierce intègre des scripts exécutables non audités (`npm`, `pip`, binaires shell). | Architecture purement déclarative (Markdown + YAML), interdiction des scripts exécutables externes non audités. |

---

## 3. Matrice des Niveaux de Risque des Outils et Compétences

Chaque compétence ou outil candidat fait l'objet d'une qualification rigoureuse avant intégration dans le catalogue :

| Niveau de Risque | Critères d'Attribution | Politique d'Intégration |
| :--- | :--- | :--- |
| **FAIBLE (*Low Risk*)** | Pure logique d'orchestration, modèles de prompts déclaratifs, formats structurés YAML, documentation, outils en lecture seule sur le workspace (`filesystem_read`). | **Adoption immédiate dans le pack de skills.** |
| **MOYEN (*Medium Risk*)** | Compétences utilisant `web_search` ou `browser` pour la consultation de portails officiels en lecture seule. | **Intégration sous garde-fous** (cloisonnement `<untrusted_web_content>`, conformité à la pyramide des sources Tier 1-6). |
| **ÉLEVÉ (*High Risk*)** | Outils nécessitant un accès complet en écriture sur le système de fichiers hôte, connecteurs avec droits d'envoi d'e-mails ou modification d'agendas. | **Audit préalable impératif par `mcp-skill-auditor`** ; rejet systématique sans accord explicite de l'utilisateur. |
| **CRITIQUE / INACCEPTABLE** | Composants manipulant des cartes bancaires, automatisant des achats, contournant des sécurités ou exécutant du code distant non audité. | **REJET IMMÉDIAT ET DÉFINITIF.** |

---

## 4. Règles d'Hygiène de Code et Audit Continu

1. **Vérification automatique continue :** La suite de tests automatisés vérifie en permanence que les agents internes ne disposent d'aucun outil web, que les agents de recherche embarquent les garde-fous PII et prompt injection, et qu'aucun secret n'est présent.
2. **Gestion des licences :** Les compétences du pack sont sous licence permissive MIT.
3. **Audit continu :** Le sous-agent `mcp-skill-auditor` et la skill `mcp-skill-auditing` évaluent toute compétence ou serveur MCP externe avant son intégration.

