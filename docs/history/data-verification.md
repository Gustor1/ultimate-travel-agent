# Modèle de Preuve et Vérification des Données — `ultimate-travel-agent`

L'un des risques majeurs de l'utilisation de l'intelligence artificielle pour la planification touristique réside dans les **hallucinations factuelles** : inventions d'horaires d'ouverture, tarifs obsolètes, adresses erronées ou suggestions de restaurants fermés.

Pour éliminer ce risque, **Ultimate Travel Agent** applique un protocole d'étiquetage formel et transparent sur chaque élément de voyage.

---

## 1. La Hiérarchie des 6 Niveaux de Vérification

Chaque transport, hébergement, activité, étape ou démarche administrative porte obligatoirement l'attribut `verification_level` :

| Niveau | Identifiant | Description | Exemple de Source |
| :--- | :--- | :--- | :--- |
| 🟢 **Officiel Vérifié** | `official_verified` | Donnée issue directement d'un portail gouvernemental, consulaire ou de la billetterie officielle du monument/transporteur. | `sagradafamilia.org`, `sncf-connect.com`, `diplomatie.gouv.fr` |
| 🔵 **Recoupé (Cross-checked)** | `cross_checked` | Information confirmée par au moins deux sources réputées et indépendantes (guides de référence, offices de tourisme municipaux). | *Le Guide du Routard*, *Lonely Planet*, *Michelin Guide Vert* |
| 🔷 **Recommandé Communautaire** | `community_recommended` | Consensus issu de communautés de voyageurs expérimentés avec retours récents positifs. | Forums spécialisés, retours d'expériences documentés |
| 🟣 **Découverte Réseaux Sociaux** | `social_discovery_only` | Pépite ou tendance issue de plateformes sociales (TikTok, Instagram, Xiaohongshu/RedNote). **Nécessite une vigilance accrue sur les horaires et les prix réels.** | Comptes créateurs de voyage, vidéos virales |
| 🟡 **Non Vérifié** | `unverified` | Donnée estimée par un algorithme ou fournie par une source tierce sans confirmation directe. | Estimation forfaitaire de repas ou de taxi urbain |
| 🔴 **Obsolète** | `outdated` | Donnée identifiée comme antérieure à une modification récente de tarification, de calendrier ou de réglementation. | Ancien tarif pré-inflation ou horaires de basse saison |

---

## 2. Règle de Non-Masquage et Propagation du Niveau le Plus Faible

Le moteur d'orchestration (`TravelOrchestrationEngine`) applique une règle de fidélité stricte :

> **Principe de prudence :**  
> Une chaîne d'informations ou un dossier global ne peut pas prétendre à un niveau de confiance supérieur à celui de son élément le plus faible.

Si un itinéraire comprend 5 visites certifiées auprès de leurs billetteries officielles (`official_verified`) mais inclut une découverte gastronomique issue de TikTok (`social_discovery_only`), le contrôleur qualité (`quality-controller`) signale explicitement la présence d'items non vérifiés et préserve le tag original sans le maquiller.

---

## 3. Audit de Sécurité des Liens de Réservation (Anti-Phishing)

L'agent auditeur (`mcp-skill-auditor`) inspecte chaque URL générée dans le dossier de voyage :

1. **Protocoles sécurisés** : Seuls les protocoles `https://` (ou `http://` en test local) sont autorisés.
2. **Rejet des réducteurs d'URL** : Les liens raccourcis opaques (`bit.ly`, `tinyurl.com`, `t.co`) sont systématiquement refusés pour prévenir le hameçonnage.
3. **Redirection vers les opérateurs réels** : Les liens de réservation pointent vers les sites directs (compagnies aériennes, opérateurs ferroviaires, billetterie propre du musée) plutôt que vers des intermédiaires non officiels surfacturés.

---

## 4. Recommandations Pratiques pour le Voyageur

Avant de réserver ou d'engager des dépenses :
1. **Prioriser les éléments avec le tag 🟢 `official_verified`**.
2. Pour les items 🟣 `social_discovery_only` ou 🟡 `unverified`, toujours cliquer sur le lien ou vérifier les horaires réels sur une carte locale le matin même.
3. Ne jamais considérer un numéro d'urgence ou une démarche de visa comme définitivement acquise sans consultation du site ministériel officiel de son pays d'origine (*« Requires official source verification. »*).
