# Goldfish Annotated Review Report (étape 9)

Status: resolved (2026-10-31, « auto accept » : plan remplacé par plan_propose_etape9.md, 3 retouches de la spécification appliquées)

**Target:** `docs/designs/architecture-niveau-1.md`, du titre « ## Detailed Implementation Plan » à la fin, plus trois retouches de la spécification que le plan exige.

**Constats traités :** les 28 constats de [implementation_readiness_report.md](./implementation_readiness_report.md).

**Bilan des suggestions :** 27 PROPOSE FIX, 1 DECLINE, 0 CONTEST, 0 ESCALATE.

**Correction principale :** le plan d'implémentation est entièrement réécrit. Le nouveau texte est dans [plan_propose_etape9.md](./plan_propose_etape9.md), et il remplacerait la section actuelle. Il suit la recommandation de l'étape 5 (Z-M2) : **il ne crée que ce qui n'existe pas encore**, et n'écrit plus d'ADR qui recopient le document.

| Fichier | Ancien plan | Nouveau plan |
| :-- | :-- | :-- |
| ADR 0001 à 0006 | Six ADR qui recopient les décisions du document | Supprimées. Les décisions du 2026-10-31 restent dans le document, et `docs/adr/` ne reçoit que les décisions futures (modèle avec statut) |
| `docs/questions-ouvertes.md` | Registre qui recopie Open Questions | Supprimé. La section Open Questions du document reste le registre |
| `docs/feuille-de-route.md` | Recopie le tableau de §11 | Contient seulement le jalon en cours, les liens vers §11, les chemins des documents de niveau 2 et leur statut. Devient un chemin protégé |
| `docs/glossaire.md` | Catégories, identifiants à inventer | Liste fermée de termes. Identifiant repris du document, sinon « à fixer au niveau 2 de Mx » |
| `CLAUDE.md` | Règles résumées, avec des erreurs | Texte exact donné dans le plan |
| `docs/noms-valides.md`, `docs/termes-interdits.md` | Absents | Créés (chemins protégés) |
| Document cible | « (Create) », copie du brouillon | « (Modify) » : seul le statut change, et l'avertissement est retiré |
| `design_draft.md` | Copié puis supprimé | Supprimé **sans rien copier** |
| `concepts_brief.md` | Note de renvoi | Supprimé, car il est identique à la RFC (vérifié avec `cmp`) |
| Rapports de revue | Non traités | Déplacés dans `docs/revues/2026-10-31-architecture-niveau-1/`, avec une phrase qui dit qu'ils sont périmés |

**Trois retouches de la spécification** sont à appliquer en même temps :
1. **l. 22 :** « Il ne liste pas les fichiers à écrire » devient « Il ne liste pas les fichiers de code à écrire » (codebase-details-1-8).
2. **l. 8 :** l'exception de langue s'étend aux intitulés du gabarit du plan : sous-titres, Type / Scope, Proposed Changes, Create / Modify / Delete / Move (style-1-3).
3. **§10, chemins protégés :** « la liste des noms validés et celle des termes interdits » devient `docs/noms-valides.md` et `docs/termes-interdits.md`, et `docs/feuille-de-route.md` s'ajoute à la liste (implementation-readiness-1-9, codebase-details-1-3).

---

## Prioritized Findings & AI Suggestions

| # | Constat | Gravité | Suggestion | Où c'est réglé dans le nouveau plan |
| :-- | :-- | :-- | :-- | :-- |
| 1 | implementation-readiness-1-1 : ADR 0001 avec 347 au lieu de 1 736 | High | PROPOSE FIX | Plus d'ADR 0001. Le grep « aucune copie de seuil » du plan de vérification le contrôle |
| 2 | codebase-details-1-1 : risque d'écraser le document par le brouillon | High | PROPOSE FIX | Points 8 et 9 : « (Modify) » statut seul ; suppression sans copie ; vérification du statut |
| 3 | implementation-readiness-1-2 : règle des tickets et du contenu de tiers absente de `CLAUDE.md` | High | PROPOSE FIX | Point 6, section « Ne jamais », reprise mot pour mot |
| 4 | implementation-readiness-1-3 : glossaire à inventer | High | PROPOSE FIX | Point 1 : liste fermée, identifiants du document ou « à fixer au niveau 2 de Mx », « carte d'évaluation » et « épisode » retirés |
| 5 | style-1-1 : « option A » ambigu | Medium | PROPOSE FIX | Plus d'ADR 0001 |
| 6 | implementation-readiness-1-4 : « la seule barrière » | Medium | PROPOSE FIX | Point 6 : phrase corrigée, conforme à §10 |
| 7 | implementation-readiness-1-5 : « pull request dédiée » | Medium | PROPOSE FIX | Point 6 : circuit des pull requests repris de §10, avec l'exception des empreintes et les scénarios en attente |
| 8 | implementation-readiness-1-6 : déterminisme incomplet et renvois flous | Medium | PROPOSE FIX | Point 6 : règle de renvoi vers §2 et §1 avec liens, et rappel marqué non exhaustif |
| 9 | codebase-details-1-2 : interdits manquants | Medium | PROPOSE FIX | Point 6 : runner auto-hébergé, adresses, graine, journal, instantanés, revue EGM des chemins protégés |
| 10 | implementation-readiness-1-7 : ordre de lecture et jalon en cours | Medium | PROPOSE FIX | Point 6 (ordre de lecture en cinq étapes, « s'arrêter et demander »), point 2 (« Jalon en cours : M0 »), convention de chemin des documents de niveau 2 |
| 11 | codebase-details-1-3 : listes de noms sans fichier | Medium | PROPOSE FIX | Points 3 et 4, et retouche 3 de la spécification |
| 12 | codebase-details-1-4 : ADR 0004 divergente | Medium | PROPOSE FIX | Plus d'ADR 0004 : §10 reste la seule explication |
| 13 | implementation-readiness-1-8 : recopies sans précédence | Medium | PROPOSE FIX | Règle de précédence en tête du plan et dans `docs/adr/README.md`. Plus aucune recopie |
| 14 | implementation-readiness-1-9 : feuille de route non protégée | Medium | PROPOSE FIX | Point 2 (aucun critère recopié) et retouche 3 (chemin protégé) |
| 15 | implementation-readiness-1-10 : registre des questions à inventer | Medium | PROPOSE FIX | Registre supprimé. Open Questions reste la seule liste |
| 16 | codebase-details-1-5 : note de la RFC fausse et incomplète | Medium | PROPOSE FIX | Point 7 : texte exact, écarts corrigés, « format des instantanés » retiré |
| 17 | implementation-readiness-1-11 : vérification incomplète | Medium | PROPOSE FIX | Plan de vérification : emplacement du compte rendu, grep des seuils, tableaux de correspondance, réponses attendues, revue EGM de tous les fichiers |
| 18 | codebase-details-1-6 : ADR 0003 et 0005 incomplètes, aucun critère d'ADR | Low | PROPOSE FIX | Plus d'ADR rétroactives. Critère écrit dans `docs/adr/README.md` |
| 19 | implementation-readiness-1-12 : pas de champ statut dans le modèle d'ADR | Low | PROPOSE FIX | Point 5 : champs statut, date et décideur |
| 20 | implementation-readiness-1-13 : pas de phases | Low | PROPOSE FIX | Trois phases, chacune avec l'état qu'elle laisse |
| 21 | codebase-details-1-7 : rapports et `concepts_brief.md` | Low | PROPOSE FIX | Points 10 et 11 |
| 22 | style-1-2 : convention de langue | Low | PROPOSE FIX | En tête du plan : révisable par le propriétaire, commits, pull requests et commentaires couverts ; recopiée dans le glossaire, que `CLAUDE.md` désigne |
| 23 | codebase-details-1-8 : « ne liste pas les fichiers » | Low | PROPOSE FIX | Retouche 1 de la spécification |
| 24 | style-1-3 : anglais au-delà de l'exception | Low | PROPOSE FIX | Retouche 2 de la spécification |
| 25 | style-1-4 : renvois de forme irrégulière | Low | PROPOSE FIX | Le nouveau plan écrit « §N » avec un lien partout |
| 26 | style-1-5 : deux régimes de preuve | Low | PROPOSE FIX | Point 6 : formulation proposée par le relecteur |
| 27 | style-1-6 : « destruction (sortie d'argent) », « explicitement séparé » | Low | PROPOSE FIX | Point 1 : une entrée par sens ; les définitions viennent du document, liens compris |
| 28 | style-1-7 : « pousser en force », « fichiers indexés » | Low | DECLINE (en partie) | « forcer un push » est repris. « Fichiers indexés » est remplacé par la commande `git diff --cached --name-only`, ce qui règle le fond. Rien d'autre à changer |

## Point d'attention pour le propriétaire

Le nouveau plan **supprime deux fichiers** (`design_draft.md` et `concepts_brief.md`) et en **déplace sept**. La suppression de `concepts_brief.md` repose sur une comparaison faite le 2026-10-31 : il est identique à la RFC. `/egm:egm-draft` cherchait ce fichier par défaut, mais la RFC le remplace.
