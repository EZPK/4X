# Rapport de revue Goldfish : test de préparation à l'implémentation (étape 9, tour 2)

**Cible :** /home/ezpk/Projects/4X/docs/designs/architecture-niveau-1.md, l. 641 à 815 (« ## Detailed Implementation Plan » jusqu'à la fin). Les l. 1 à 640 servent de spécification de référence.

**Standard appliqué :** /home/ezpk/.claude/plugins/cache/egm/egm/0.1.0/resources/document_standards/implementation-readiness-standard.md (pour egm-implementation-readiness et egm-codebase-details). egm-style a travaillé avec son seul persona.

**Entrées :** rapport du tour 1, /home/ezpk/Projects/4X/implementation_readiness_report.md ; rapport de résolution, /home/ezpk/Projects/4X/goldfish_review_report_etape9.md.

C'est le tour 2, le seul ré-audit autorisé.

## État des relecteurs

| Relecteur | État | Constats bruts remontés (nouveaux) |
| --- | --- | --- |
| `egm-implementation-readiness` | completed | 0 Blocker, 2 Major, 9 Nit |
| `egm-codebase-details` | completed | 0 Blocker, 3 Major, 10 Nit |
| `egm-style` | completed | 0 Blocker, 8 Major, 8 Nit |

Les trois relecteurs ont rendu leur rapport au premier essai. Aucune relance n'a été nécessaire.

## Verdict

**Le plan n'est pas encore prêt pour l'implémentation, mais il n'a plus de Blocker.**

La réécriture règle le fond du tour 1 :
- plus d'ADR qui recopient le document ;
- plus de risque d'écraser la spécification avec le brouillon ;
- un texte exact pour `CLAUDE.md` ;
- trois phases ;
- un compte rendu de vérification avec un chemin.

Les trois retouches de la spécification sont en place (l. 8, 22 et 440). Les trois relecteurs l'ont vérifié.

Ce qui reste :
- **Tour 1 :** 22 constats réglés, 6 réglés en partie, 0 non réglé. Trois des reliquats restent de niveau Major (implementation-readiness-1-3, -1-5 et -1-11).
- **Nouveaux constats :** 0 Blocker, 8 Major, 14 Nit, après dédoublonnage.

Les Major les plus coûteux à laisser :
- **implementation-readiness-2-1 :** le plan attend le statut « Approved », alors que c'est lui qui le pose.
- **implementation-readiness-2-2 :** la règle de précédence rend toute ADR future sans effet.
- **style-2-1 et style-2-2 :** deux phrases de `CLAUDE.md` donnent à l'agent une image fausse, l'une de ses protections, l'autre de la portée des règles de déterminisme.

---

## 1. Statut des 28 constats du tour 1

Quand les relecteurs divergent, le statut retenu est expliqué dans la colonne de droite.

| Constat du tour 1 | Statut retenu | Justification |
| :-- | :-- | :-- |
| implementation-readiness-1-1 (seuil Rust 347) | resolved | Plus d'ADR 0001. Le grep de la l. 808 cherche 347 et 1 736. L'espace de la l. 237 est une espace simple, que le grep trouve. |
| codebase-details-1-1 (écrasement par le brouillon) | resolved | Le point 8 passe en « (Modify) », statut seul (l. 776-782). Le point 9 supprime le brouillon sans rien copier (l. 787). L'ordre du changement de statut pose un problème nouveau : voir implementation-readiness-2-1. |
| implementation-readiness-1-2 (règle des tickets et du contenu de tiers) | resolved | Reprise à la l. 739. |
| implementation-readiness-1-3 (glossaire à inventer) | **partially** (3 relecteurs sur 3) | Liste fermée, règle des identifiants, retrait de « carte d'évaluation » et d'« épisode » : réglé. **Reliquat, Major :** voir la section 2. |
| style-1-1 (« option A ») | resolved | L'ADR 0001 n'existe plus. |
| implementation-readiness-1-4 (« la seule barrière ») | resolved | La phrase a disparu. Celle qui la remplace (l. 742) promet trop : voir style-2-1. |
| implementation-readiness-1-5 (« pull request dédiée ») | **partially** (implementation-readiness ; egm-style signale le même manque comme nouveau constat Major) | Les deux types de pull request et l'exception des empreintes sont repris (l. 744-748). **Reliquat, Major :** voir la section 2. |
| implementation-readiness-1-6 (déterminisme) | resolved | Règle de renvoi vers §2 et §1, avec liens, et rappel marqué non exhaustif (l. 751). La portée du rappel pose un problème nouveau : voir style-2-2. |
| codebase-details-1-2 (interdits manquants) | resolved | Runner (l. 737), adresses, graine, journal et instantanés (l. 738), revue EGM (l. 748). Un lien manque : voir codebase-details-2-5. |
| implementation-readiness-1-7 (ordre de lecture) | resolved | Ordre en cinq étapes (l. 726-731), « Jalon en cours : M0 » (l. 689), convention de chemin (l. 654), réponse attendue (l. 814). Il reste des ambiguïtés : voir implementation-readiness-2-4. |
| codebase-details-1-3 (listes de noms sans fichier) | resolved | Points 3 et 4, et l. 440. |
| codebase-details-1-4 (ADR 0004) | resolved | Plus d'ADR 0004. |
| implementation-readiness-1-8 (recopies sans précédence) | resolved | Règle de précédence (l. 647, 714) et plus aucune recopie dans des ADR. Cette règle crée deux problèmes nouveaux : voir implementation-readiness-2-2 et style-2-3. |
| implementation-readiness-1-9 (feuille de route non protégée) | resolved | Aucun critère recopié, chemin protégé (l. 440), « Ce fichier fait foi » (l. 692). |
| implementation-readiness-1-10 (registre des questions) | resolved | Registre supprimé. |
| codebase-details-1-5 (note de la RFC) | **partially** (egm-style ; les deux autres : resolved) | Le texte exact est donné et vérifié contre la RFC (l. 43, 258-259, 265, 268, 297), et « format des instantanés » est retiré. **Reliquat, Nit :** la ligne de statut de la RFC reste « à valider avant `/egm-draft` » (RFC l. 5, vérifié), et le tour 1 la citait parmi les écarts. La décision 6 fait l'objet d'un nouveau constat (codebase-details-2-4), les renvois « §N » aussi (style-2-4). |
| implementation-readiness-1-11 (vérification incomplète) | **partially** (3 relecteurs sur 3) | Chemin du compte rendu (l. 804), réponses attendues (l. 813-814), revue étendue (l. 815) : réglé. **Reliquat, Major :** voir la section 2. |
| codebase-details-1-6 (critère des ADR) | resolved | Critère écrit (l. 712). |
| implementation-readiness-1-12 (champ statut) | resolved | l. 713. |
| implementation-readiness-1-13 (phases) | resolved | Trois phases, chacune avec l'état qu'elle laisse (l. 656-759). |
| codebase-details-1-7 (rapports, `concepts_brief.md`) | resolved | Points 10 et 11. Les sept rapports cités existent à la racine. Voir codebase-details-2-3 et implementation-readiness-2-5. |
| style-1-2 (convention de langue) | resolved | l. 649-652. Le fichier qui doit la porter est mal désigné : voir style-2-6. |
| codebase-details-1-8 (l. 22) | resolved | l. 22 corrigée. |
| style-1-3 (anglais) | resolved | l. 8 étendue. Détail sans conséquence : « Compilation/Build » (l. 806) n'est pas dans la liste de la l. 8. |
| style-1-4 (forme des renvois) | **partially** (egm-style : not resolved ; egm-codebase-details : partially ; egm-implementation-readiness : resolved) | `CLAUDE.md` renvoie par des liens complets. **Reliquat, Nit :** les textes destinés à d'autres fichiers écrivent « §N » sans lien : `docs/termes-interdits.md` (l. 705) et la note de la RFC (l. 767-774), y compris « (glossaire) » sans chemin. Le rapport de résolution affirmait « « §N » avec un lien partout ». C'est inexact. Ce reliquat est aggravé dans la RFC : voir style-2-4. |
| style-1-5 (deux régimes de preuve) | resolved (2 sur 3) | La l. 740 reprend la formulation proposée. L'objection d'egm-implementation-readiness porte sur la formulation elle-même : elle devient le nouveau constat implementation-readiness-2-6. |
| style-1-6 (glossaire imprécis) | resolved | « Une entrée distincte par sens » (l. 666). |
| style-1-7 (DECLINE en partie) | **partially, réouverture limitée** (egm-style ; les deux autres : resolved) | « Forcer un push » est repris (l. 735). egm-style estime que la correction a échoué sur un point : `git diff --cached --name-only` (l. 738) n'affiche que des noms de fichiers. Elle attrape donc un journal ou un instantané ajouté, mais pas une adresse du PC d'entraînement écrite dans un fichier. Or c'est l'un des buts de la règle. « Fichiers ajoutés » est en outre ambigu (nouveaux ou indexés ?). **Reliquat, Nit.** Correction : « Avant chaque commit, relire le contenu indexé (`git diff --cached`). » |

**Bilan du tour 1 :** 22 resolved, 6 partially, 0 not resolved.

---

## 2. Reliquats Major des constats du tour 1

Ce ne sont pas de nouveaux constats. Ils gardent l'identifiant du tour 1.

### implementation-readiness-1-3 (reliquat) : la liste fermée du glossaire oblige encore le rédacteur à inventer. Sévérité : Major
* **Relecteurs :** les trois (egm-codebase-details le classe Nit, egm-implementation-readiness Major).
* **Lignes :** 664-681. Spécification : 47, 56, 81, 153, 165, 248, 292, 308.
* **Problème :**
  * « fonction publique (hors périmètre) » (l. 674) n'apparaît nulle part dans la spécification, et les Non-Goals cités en lien ne la définissent pas. La colonne *lien* ne peut pas être remplie.
  * Des termes centraux de la spécification manquent : `step`, `observe` et l'observation, la politique (l. 153, vérifié), la corporation (l. 248, 292, 308, vérifié), la validation sans état, le protocole, l'environnement d'entraînement, la définition d'étapes. Comme la liste est fermée, le rédacteur ne peut pas les ajouter, et le contrôle de la l. 810 ne verra pas qu'ils manquent.
  * La règle de la l. 665 ne dit pas quoi écrire dans la colonne « identifiant » pour un terme qui n'a ni identifiant ni jalon : humain, joueur IA, PNJ, agent de code, client tiers, déclencheur Rust, indicateur avancé, toute la ligne « Projet ». Pour les valeurs de `actor_kind`, le rédacteur sera tenté d'inventer `human` ou `npc`.
  * La l. 664 ne dit pas que la « définition en une ligne » reprend la phrase du document. Le rapport de résolution l'affirme pourtant.
* **Pourquoi c'est important :** c'est le même défaut qu'au tour 1. Le rédacteur décide seul dans un chemin protégé.
* **Correction proposée :**
  * Retirer « fonction publique ».
  * Ajouter les termes oubliés.
  * Écrire « — (pas d'identifiant de code) » pour les termes qui n'ont ni identifiant ni jalon.
  * Ajouter : « la définition reprend la phrase du document qui la donne ».

### implementation-readiness-1-5 (reliquat) : `CLAUDE.md` ne dit pas où vit la marque *en attente*. Sévérité : Major
* **Relecteurs :** `egm-implementation-readiness` (reliquat Major), `egm-style` (nouveau constat N-4, Major).
* **Lignes :** 746. Spécification : 431, 437.
* **Problème :** la l. 746 demande à la pull request de fonctionnalité de retirer la marque *en attente*, et d'ajouter qu'elle « ne touche aucun chemin protégé ». Or les scénarios sont un chemin protégé (l. 437). La spécification lève la contradiction à la l. 431 : « La liste des scénarios en attente vit hors des chemins protégés, et le moyen exact est fixé au niveau 2 de M0. » `CLAUDE.md` omet cette phrase.
* **Pourquoi c'est important :** un agent qui ne lit que `CLAUDE.md` reçoit deux consignes incompatibles.
* **Correction proposée :** « …le retrait de la marque *en attente*, dans la liste des scénarios en attente, qui vit hors des chemins protégés (moyen fixé au niveau 2 de M0). » On peut ajouter que le contrôle de garde pose alors l'étiquette « références régénérées ».

### implementation-readiness-1-11 (reliquat) : l'outil de vérification des liens n'existe pas, et le contrôle des seuils ne cherche qu'un seuil. Sévérité : Major
* **Relecteurs :** les trois.
* **Lignes :** 807, 808. Spécification : 647.
* **Problème :**
  * La l. 807 renvoie au « script de vérification utilisé pendant la revue ». Il n'y a aucun script dans /home/ezpk/Projects/4X : la liste des fichiers ne contient que des `.md`, et aucun rapport ne contient ce script. L'exécutant devrait l'écrire, y compris la règle de calcul des ancres.
  * Le grep de la l. 808 ne cherche que 347 et 1 736. La règle de la l. 647 interdit de recopier tout seuil et tout critère : 10 %, 95 %, 100 000 ticks, 8 heures, 5 entraînements.
* **Correction proposée :**
  * Donner dans le plan la commande ou le script lui-même, avec la règle de calcul des ancres de GitHub.
  * Élargir le grep à une liste fermée de valeurs, ou exiger une relecture qui associe chaque nombre des fichiers créés à un lien.

---

## 3. Nouveaux constats (Major, puis Nit)

### implementation-readiness-2-1 : la condition de départ du plan tourne en rond. Sévérité : Major
* **Relecteurs :** les trois (`egm-implementation-readiness` N1, `egm-codebase-details` N1, `egm-style` N-1).
* **Lignes :** 643, 780, 811 ; l. 4.
* **Problème :** la l. 643 dit que le plan « s'exécute une fois que le statut de ce document est passé à « Approved » ». Or c'est le point 8, en phase 3, qui fait passer le statut de « Proposed » à « Approved » (l. 780), et le statut actuel est « Proposed » (l. 4, vérifié). La l. 811 (« contient **toujours** la ligne « Statut : Approved » ») suppose même que le statut était déjà « Approved ».
* **Pourquoi c'est important :** à la lettre, le plan ne peut jamais commencer. Sinon, l'exécutant choisit seul de changer le statut avant la phase 1 ou au point 8.
* **Correction proposée :** l. 643 : « Il s'exécute une fois que le propriétaire a validé ce plan corrigé. Le passage du statut à « Approved » est le point 8. » À la l. 811, remplacer « toujours » par « désormais » (voir aussi codebase-details-2-1).

### implementation-readiness-2-2 : la règle de précédence rend toute ADR future sans effet. Sévérité : Major
* **Relecteurs :** `egm-implementation-readiness` (N2), `egm-codebase-details` (N2).
* **Lignes :** 647, 712, 714.
* **Problème :**
  * La l. 647 dit « En cas d'écart, ce document l'emporte ». Une ADR « change une interface, un invariant ou un choix décrit » dans le niveau 1 (l. 712). Elle crée donc un écart par définition, et cet écart est toujours tranché en faveur du niveau 1.
  * Recopiée telle quelle dans `docs/adr/README.md` (l. 714), la phrase « ce document l'emporte » y désignerait le README, et « les fichiers créés ici » n'y aurait plus de sens.
  * Les deux critères divergent : « une interface ou un invariant » (l. 647), « une interface, un invariant **ou un choix** » (l. 712).
* **Pourquoi c'est important :** le premier agent qui rédige une ADR doit inventer le processus de mise à jour des décisions, dans un chemin protégé.
* **Correction proposée :** donner le texte exact du README, par exemple : « `docs/designs/architecture-niveau-1.md` fait foi. Une ADR acceptée modifie, dans la même pull request, la section du niveau 1 qu'elle concerne. L'ADR garde la raison du changement, le niveau 1 garde la règle. La règle « le niveau 1 l'emporte » vaut contre les copies, pas contre une ADR acceptée. » Aligner les deux critères sur une même formule.

### style-2-1 : `CLAUDE.md` prête au hook et aux règles `deny` des contrôles qu'ils ne font pas, et qui n'existent pas encore. Sévérité : Major
* **Relecteurs :** `egm-style` (N-2, Major), `egm-implementation-readiness` (N3, Nit), `egm-codebase-details` (N7, Nit).
* **Lignes :** 742. Spécification : 413-420, 645.
* **Problème :**
  * « Ces interdictions sont aussi filtrées par le hook Claude Code et par les règles `deny` de `.claude/settings.json`. » Selon les l. 413-420, ces mécanismes couvrent seulement la fusion, le push vers `main`, le push forcé, `--no-verify` et la modification des réglages. Ils ne filtrent pas les cas suivants :
    * le runner auto-hébergé ;
    * les secrets (c'est le rôle de `gitleaks`) ;
    * les adresses, la graine et le journal ;
    * les instructions de tiers ;
    * les affirmations sans preuve.
  * `.claude/settings.json` n'est créé qu'au niveau 2 de M0 (l. 645). Jusque-là, la phrase est fausse.
  * « La règle ci-dessus » ne désigne aucune des sept puces en particulier.
* **Pourquoi c'est important :** dans le premier fichier qu'il lit, l'agent apprendrait que des interdictions sont protégées alors qu'elles ne le sont pas.
* **Note de synthèse :** Major retenu (deux relecteurs sur trois disent Nit), parce que la phrase est fausse sur un dispositif de sécurité.
* **Correction proposée :** « À partir de M0, la fusion, le push vers `main`, le push forcé, `--no-verify` et la modification des réglages sont aussi filtrés par le hook Claude Code et les règles `deny` de `.claude/settings.json`, qui n'attrapent que les commandes directes. Les secrets sont aussi bloqués par `gitleaks`. Aucun mécanisme technique n'empêche un script de fusionner une pull request aux contrôles verts : seule la règle « Seul le propriétaire fusionne » l'interdit (§10). »

### style-2-2 : le rappel de déterminisme perd sa portée « dans le noyau ». Sévérité : Major
* **Relecteur :** `egm-style` (N-3).
* **Lignes :** 751. Spécification : 253-254 (vérifié : « Aucun nombre flottant, aucune division ni modulo natifs (`/`, `//`, `%`) dans le noyau »).
* **Problème :** le rappel de `CLAUDE.md` interdit flottants, `/`, `//` et `%` sans dire que ces interdits ne valent que pour le noyau.
* **Pourquoi c'est important :** l'agent les appliquerait à `training` et `policies`, où les réseaux de neurones utilisent forcément des flottants.
* **Correction proposée :** « Dans le paquet `core` : appliquer tous les invariants de déterminisme de §2… Rappel non exhaustif : … »

### style-2-3 : `CLAUDE.md` enfreint la règle de précédence que le plan pose. Sévérité : Major
* **Relecteurs :** `egm-style` (N-5, Major), `egm-codebase-details` (N11, Nit).
* **Lignes :** 647, 744-751. Spécification : 409.
* **Problème :** la l. 647 interdit aux fichiers créés de recopier « seuil » ou « procédure ». `CLAUDE.md` recopie pourtant la procédure des pull requests (l. 744-748) et un seuil, « entiers sur 64 bits signés » (l. 751). La spécification l'impose en partie : les règles de travail sont « inscrites dans `CLAUDE.md` » (l. 409). Mais la règle de précédence ne prévoit aucune exception.
* **Pourquoi c'est important :** deux fichiers protégés et permanents se contrediraient, `docs/adr/README.md` (qui reprend la règle) et `CLAUDE.md`. Un agent pourrait plus tard « corriger » `CLAUDE.md` en supprimant ces recopies.
* **Note de synthèse :** à corriger dans la même réécriture de la l. 647 qu'implementation-readiness-2-2.
* **Correction proposée :** « Les fichiers créés ici ne recopient ni seuil ni critère de sortie. Seul `CLAUDE.md` résume des règles et des procédures, chacune suivie d'un lien vers la section qui fait foi. En cas d'écart, ce document l'emporte. »

### style-2-4 : dans la note de la RFC, « §N » renvoie aux sections de la RFC elle-même. Sévérité : Major
* **Relecteur :** `egm-style` (N-6). Cela aggrave le reliquat de style-1-4.
* **Lignes :** 767-774, 705.
* **Problème :** la RFC numérote ses propres sections de 1 à 13 (vérifié : « ### 10. « L'agent s'améliore » n'a pas de définition », « ### 3. Le déterminisme se conçoit… »). Lu dans la RFC, « (§10) » renvoie à la section 10 de la RFC, et non à §10 du niveau 1. « (§3) » renvoie au déterminisme de la RFC.
* **Pourquoi c'est important :** le texte de la note est imposé mot pour mot (l. 764). Le rédacteur ne peut donc pas lever l'ambiguïté lui-même, et un lecteur de la RFC suivrait le mauvais renvoi.
* **Correction proposée :** écrire chaque renvoi sous forme de lien, par exemple `[§10 du niveau 1](./architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia)`, et `[glossaire](../glossaire.md)`. Faire de même à la l. 705 pour `docs/termes-interdits.md`.

### style-2-5 : le contrôle de `CLAUDE.md` ne peut pas réussir tel qu'il est écrit. Sévérité : Major
* **Relecteur :** `egm-style` (N-8).
* **Lignes :** 809.
* **Problème :**
  * La l. 809 demande d'associer « à chaque règle de §10 (règles de travail, interdictions, circuit des pull requests) et de §9bis sa ligne dans `CLAUDE.md` », sans « aucune règle sans ligne ». Or §10 contient des règles qui n'ont rien à faire dans `CLAUDE.md` : la configuration de la protection de branche, la liste des chemins protégés, les tableaux de contrôles par jalon, la suite canari. Lu à la lettre, le contrôle échoue. Lu au sens large, l'exécutant choisit ce qui compte.
  * En sens inverse, des règles de `CLAUDE.md` viennent de §3, de §8 et des Non-Functional Requirements, que le contrôle ne couvre pas.
* **Correction proposée :** « …à chaque règle des l. 409-411, 415-420 et 429-431 (§10), de la l. 399 (§9bis), de la l. 364 (§8) et de la l. 592 (Non-Functional Requirements)… ».

### codebase-details-2-1 : le plan de vérification ne détecte pas un nettoyage fait à moitié. Sévérité : Major
* **Relecteurs :** `egm-codebase-details` (N3, Major), `egm-style` (N-10, Nit), `egm-implementation-readiness` (N9, Nit).
* **Lignes :** 811 ; l. 4 ; points 8 et 11.
* **Problème :**
  * `ls design_draft.md concepts_brief.md plan_propose_etape9.md` échoue dès qu'**un seul** des trois fichiers manque. Le contrôle passe donc même si deux fichiers restent.
  * La vraie ligne est `*   **Statut :** Proposed` (l. 4, vérifié). Le texte « Statut : Approved » n'y figure pas tel quel, à cause des `**`. Un grep littéral échoue même après une modification correcte.
  * Rien ne vérifie le retrait de l'encadré de la l. 643, le déplacement des sept rapports, ni le `README.md` de `docs/revues/…`.
* **Note de synthèse :** Major retenu, parce que deux des trois vérifications de la l. 811 donnent un résultat faux, l'un trop indulgent, l'autre trop sévère.
* **Correction proposée :**
  * `for f in design_draft.md concepts_brief.md plan_propose_etape9.md; do test ! -e "$f" || echo "reste : $f"; done` : aucune ligne attendue.
  * `grep -n '^\*   \*\*Statut :\*\* Approved$' docs/designs/architecture-niveau-1.md` : une ligne attendue.
  * `grep -c 'Plan corrigé après' docs/designs/architecture-niveau-1.md` : 0 attendu.
  * Aucun `*_report*.md` à la racine, et la liste attendue des fichiers de `docs/revues/2026-10-31-architecture-niveau-1/`.

### style-2-6 : la convention de langue doit aller dans le glossaire, mais le point 1 ne le prévoit pas. Sévérité : Nit
* **Relecteurs :** `egm-style` (N-7, Major), `egm-implementation-readiness` (N5, Nit), `egm-codebase-details` (N13, Nit).
* **Lignes :** 658, 663-666, 753, 755.
* **Problème :**
  * La consigne « recopiée en tête du glossaire » se trouve au point 6, en phase 2, alors que le glossaire est créé au point 1, en phase 1, dont la règle est « aucun fichier existant n'est encore modifié ».
  * Aucune vérification ne contrôle sa présence, alors que `CLAUDE.md` renvoie au glossaire pour la convention (l. 753).
  * « La convention de langue ci-dessus » (l. 755) peut désigner la puce de `CLAUDE.md` qui précède, au lieu des l. 649-652.
* **Note de synthèse :** ramené à Nit, parce que la consigne existe dans le plan et qu'il suffit de la déplacer.
* **Correction proposée :**
  * Dans le point 1, ajouter : « En tête : la convention de langue des l. 649-652, recopiée telle quelle. »
  * Retirer la l. 755.
  * Ajouter cette présence au contrôle de la l. 810.

### style-2-7 : défauts de détail dans la liste fermée du glossaire. Sévérité : Nit
* **Relecteurs :** `egm-style` (N-9), `egm-implementation-readiness` (N4), `egm-codebase-details` (reliquat de 1-3).
* **Lignes :** 651, 672-681. Spécification : 81, 173, 258.
* **Problème :**
  * « joueur IA » et « référence scriptée » apparaissent dans deux groupes (l. 672, 673), ce qui contredit « une entrée distincte par sens ».
  * « client tiers » est rattaché à l'Overview. Il n'apparaît qu'aux Non-Goals (l. 81, vérifié), où il désigne un client logiciel.
  * « fréquence des empreintes (`N_empreinte`) » : c'est un intervalle (« tous les `N_empreinte` ticks », l. 258, vérifié).
  * `orders`, `events` et `state` sont des paramètres de `step`, au pluriel. Les donner comme identifiants d'« ordre », d'« événement » et d'« état » pousse à nommer des types au pluriel.
  * `K_ordres`, `T_inactif` et `N_empreinte` sont en français, alors que la l. 651 veut des identifiants en anglais.
  * « mode rejeu » est défini en §1 (l. 173, vérifié), absent des sections citées à la l. 675. Jalon et documents de niveau 1 et 2 sont dans l'Overview, absente de la l. 681.
* **Correction proposée :**
  * Une seule entrée par terme.
  * « client tiers » → Non-Goals.
  * « intervalle des empreintes en production ».
  * « (paramètre de `step`) » pour `orders`, `events` et `state`.
  * Les trois réglages marqués « nom provisoire du document, nom définitif au niveau 2 de Mx ».
  * Colonnes Section corrigées.

### implementation-readiness-2-3 : la feuille de route demande un lien vers une ligne de tableau, ce qui est impossible. Sévérité : Nit
* **Relecteurs :** les trois.
* **Lignes :** 690.
* **Problème :** une ligne de tableau Markdown n'a pas d'ancre. Le seul lien possible est `../designs/architecture-niveau-1.md#11-le-découpage-en-documents-de-niveau-2`.
* **Correction proposée :** « lien vers §11 (même ancre pour tous les jalons), ligne Mx ».

### implementation-readiness-2-4 : ambiguïtés dans l'ordre de lecture de `CLAUDE.md`. Sévérité : Nit
* **Relecteurs :** les trois (`egm-style` N-11, `egm-implementation-readiness` N11, `egm-codebase-details` N13).
* **Lignes :** 690, 730. Spécification : 8.
* **Problème :**
  * « Ce document de niveau 2 » suit « 1. Ce fichier. » et peut se lire « ce fichier-ci ».
  * « n'est pas « approuvé » » peut viser le statut de la feuille de route (en français, l. 690) ou le champ Statut du document de niveau 2 (en anglais, « Approved », l. 8).
  * Si la tâche de l'agent est justement d'écrire le document de niveau 2 de M0, la règle l'arrête aussitôt.
* **Correction proposée :** « 4. Le document de niveau 2 désigné à l'étape 3. S'il n'existe pas, ou s'il n'a pas le statut « approuvé » dans `docs/feuille-de-route.md`, s'arrêter et demander au propriétaire, sauf si la tâche est de rédiger ce document. »

### implementation-readiness-2-5 : la justification de la suppression de `concepts_brief.md` ne tient plus après le point 7. Sévérité : Nit
* **Relecteur :** `egm-implementation-readiness` (N7).
* **Lignes :** 764, 791.
* **Problème :** le point 7 modifie la RFC avant que le point 10 supprime `concepts_brief.md`, « identique à la RFC ». Un `cmp` relancé au point 10 montrera une différence.
* **Correction proposée :** « vérifier avec `cmp concepts_brief.md docs/designs/mmo-gestion-spatiale-ia.md` avant le point 7 », ou placer la suppression avant le point 7.

### implementation-readiness-2-6 : la règle sur « ça marche » admet encore une preuve fournie par l'agent. Sévérité : Nit
* **Relecteur :** `egm-implementation-readiness` (sous style-1-5).
* **Lignes :** 740. Spécification : 467 (vérifié : « Les preuves sont produites par la CI ou par les scripts de §9bis, jamais déclarées par l'agent de code »), 562.
* **Problème :** « citer la sortie de la commande exécutée » fait de la sortie produite par l'agent une preuve, ce que la l. 467 exclut. La formulation vient de la correction proposée au tour 1 : le défaut est dans la proposition, pas dans son application.
* **Correction proposée :** « Ne jamais affirmer qu'une chose fonctionne sans citer le lien vers le contrôle CI correspondant. Hors pull request, citer la sortie de la commande exécutée, qui ne vaut pas preuve. »

### codebase-details-2-2 : le format de `docs/termes-interdits.md` est à la fois fixé et renvoyé à M0. Sévérité : Nit
* **Relecteurs :** les trois.
* **Lignes :** 706. Spécification : 455. RFC : 200.
* **Problème :**
  * « Le format exact lu par le contrôle (une ligne par terme, insensible à la casse) est fixé au niveau 2 de M0 » : on ne sait pas si la parenthèse est une décision ou un exemple.
  * Une recherche insensible à la casse et sans limite de mot trouvera « isk » dans `disk` et `risk`.
  * Le contrôle de M0 trouvera aussi ces termes dans la liste elle-même, dans la RFC (l. 200, vérifié) et dans les rapports déplacés, et rien n'annonce ces exclusions.
* **Correction proposée :** « Format provisoire : une ligne par terme, sans puce. Format définitif, recherche par mots entiers et fichiers exclus (cette liste, la RFC, `docs/revues/`) fixés au niveau 2 de M0. »

### codebase-details-2-3 : la liste des rapports à déplacer est fermée, et leurs liens casseront. Sévérité : Nit
* **Relecteurs :** `egm-codebase-details` (N4, N8), `egm-implementation-readiness` (N8).
* **Lignes :** 796-800, 807.
* **Problème :**
  * Les sept noms sont figés. Le présent rapport, /home/ezpk/Projects/4X/implementation_readiness_report_tour2.md, n'en fait déjà pas partie.
  * Les liens relatifs des rapports déplacés casseront : `./docs/designs/architecture-niveau-1.md` dans plusieurs rapports, `./plan_propose_etape9.md` dans /home/ezpk/Projects/4X/goldfish_review_report_etape9.md (l. 11), fichier supprimé à la l. 800.
  * La l. 807 ne dit pas si un fichier déplacé compte comme « modifié ».
* **Correction proposée :** « tous les fichiers `*_report*.md` de la racine au moment de l'exécution ». Ajouter « les rapports déplacés ne sont pas modifiés ; leurs liens internes sont exclus du contrôle de la l. 807 ».

### codebase-details-2-4 : la note de la RFC n'annule pas « À consigner dans un ADR ». Sévérité : Nit
* **Relecteurs :** `egm-codebase-details` (N9), `egm-style` (sous codebase-details-1-5).
* **Lignes :** 766-774, 647. RFC : 281 (vérifié : la décision 6 se termine par « À consigner dans un ADR. »).
* **Problème :** le plan décide que les décisions du 2026-10-31 restent dans le document (l. 647). La note ne le signale pas, si bien qu'un agent qui lit la RFC créerait une ADR rétroactive.
* **Correction proposée :** ajouter à la note : « Décisions du 2026-10-31 (dont n° 6, retour arrière) : pas d'ADR, elles restent dans le document de niveau 1 (§7). »

### codebase-details-2-5 : il manque le lien vers §8 pour l'adresse du serveur MLflow. Sévérité : Nit
* **Relecteur :** `egm-codebase-details` (N10).
* **Lignes :** 738. Spécification : 364 (vérifié), 592.
* **Problème :** l'interdiction renvoie à §3 et aux Non-Functional Requirements. La règle sur l'adresse de MLflow (« n'est jamais écrite dans le dépôt ni dans une pull request ») est en §8.
* **Correction proposée :** ajouter `[§8](docs/designs/architecture-niveau-1.md#8-lentraînement)`.

### codebase-details-2-6 : fichiers créés ou supprimés sans marque, et revue mal justifiée. Sévérité : Nit
* **Relecteurs :** `egm-codebase-details` (N12), `egm-style` (N-12, N-16), `egm-implementation-readiness` (sous 1-11).
* **Lignes :** 799, 800, 804, 815.
* **Problème :**
  * `docs/revues/2026-10-31-architecture-niveau-1/README.md` et `compte-rendu-implementation.md` sont créés sans marque (Create).
  * La suppression de `plan_propose_etape9.md` est rangée dans un point (Move).
  * La l. 815 justifie la revue « puisqu'ils sont tous des chemins protégés ». C'est faux pour `docs/revues/`, qui n'est pas dans la liste des l. 434-440.
* **Correction proposée :**
  * Des sous-points marqués (Create) et (Delete).
  * À la l. 815 : « la plupart sont des chemins protégés », en disant si `docs/revues/` est relu.

### codebase-details-2-7 : « exactement » le texte suivant, alors qu'il est présenté en citation. Sévérité : Nit
* **Relecteur :** `egm-codebase-details` (N13).
* **Lignes :** 724, 764.
* **Problème :** rien ne dit s'il faut garder les marques `>` ni si les intitulés en gras (« **Ordre de lecture** ») deviennent des titres.
* **Correction proposée :** « sans les marques de citation ; les intitulés en gras restent en gras ».

### style-2-8 : affirmations inexactes dans le texte du plan. Sévérité : Nit
* **Relecteur :** `egm-style` (N-12).
* **Lignes :** 643, 645, 759, 799.
* **Problème :**
  * l. 645 : « les quelques fichiers qu'une session d'agent de code lit en premier ». Le plan modifie aussi la RFC, supprime trois fichiers et en déplace sept.
  * l. 643 : « l'étape 9 de la revue » n'est pas défini pour un lecteur neuf. L'impact est faible, puisque l'encadré est retiré.
  * l. 759 : « Les anciens fichiers renvoient au document qui fait foi. » Seule la RFC reçoit un renvoi, les deux autres fichiers sont supprimés.
  * l. 799 : le README dit que les rapports du dossier « décrivent des versions antérieures », mais le compte rendu (l. 804), rangé au même endroit, n'en est pas un.
* **Correction proposée :** corriger chaque phrase dans ce sens.

### style-2-9 : formulations de la note de la RFC. Sévérité : Nit
* **Relecteur :** `egm-style` (N-13).
* **Lignes :** 768, 772, 774.
* **Problème :**
  * l. 768 : « désormais « étiquetée et signalée » » n'a pas de nom auquel s'accorder.
  * l. 772 : « Seuil Rust : voir §2 » ne décrit pas l'écart.
  * l. 774 : `textual-serve` est « repoussé », donc pas « tranché ».
* **Correction proposée :**
  * « critère de M0 : une pull request qui touche un chemin protégé est « étiquetée et signalée » au lieu de « bloquée » ».
  * Décrire l'écart Rust, ou retirer la ligne.
  * « tranchés ou repoussés ».

---

## Notes de synthèse

* **Dédoublonnage.** Les 13 nouveaux constats d'egm-codebase-details, les 11 d'egm-implementation-readiness et les 16 d'egm-style se ramènent à 22 nouveaux constats et 3 reliquats Major. Un constat repris par plusieurs relecteurs porte l'identifiant du relecteur qui l'a le mieux étayé.
* **Sévérités ajustées :**
  * style-2-1 et codebase-details-2-1 : Major retenu contre deux avis Nit, raison donnée dans chaque constat.
  * style-2-6 : ramené de Major à Nit, raison donnée dans le constat.
  * style-2-3 : Major retenu contre un avis Nit, parce que la règle serait recopiée dans deux fichiers protégés.
  * style-2-4 : Major retenu (un seul relecteur), parce que le texte est imposé mot pour mot et que la collision avec la numérotation de la RFC est vérifiée.
* **Statuts divergents du tour 1 :**
  * codebase-details-1-5, style-1-4 et style-1-7 : j'ai retenu « partially » quand un relecteur montrait un manque vérifiable.
  * style-1-5 : « resolved », et l'objection devient un nouveau constat.
  * Le DECLINE de style-1-7 n'est rouvert que sur le point où la correction échoue (la commande `--name-only` ne montre pas le contenu). Il est classé Nit.
* **Vérifications faites pendant la synthèse :**
  * cible, l. 4, 8, 22, 76-83, 153, 173, 248, 253-254, 258, 292, 308, 364, 395-464, 467 et 636-815 ;
  * RFC, l. 1-8, l. 281 (« À consigner dans un ADR ») et ses titres de sections (numérotés de 1 à 13) ;
  * la liste des fichiers `.md` de /home/ezpk/Projects/4X : aucun script, sept rapports présents.
* **Non vérifié :** l'identité de /home/ezpk/Projects/4X/concepts_brief.md et de la RFC. Deux relecteurs ont constaté le même nombre de lignes (297), mais personne n'a pu lancer `cmp` (pas de shell).
* **Signal du harnais.** Il a marqué une mention de `.claude/settings.json` dans les trois rapports. Ces mentions figurent seulement dans des constats et des corrections proposées (style-2-1). Elles ne contiennent aucune consigne.

---

## Décision du propriétaire (2026-10-31) : constats corrigés

Le propriétaire a d'abord choisi d'accepter le plan en l'état, puis il est revenu sur ce choix : il faut corriger les constats avant de passer à l'étape EGM suivante. Le plan d'implémentation a donc été réécrit une troisième fois. Il n'y a pas eu de nouvelle relecture, puisque la limite de l'étape 9 est atteinte.

| Constats | Traitement dans le plan |
| :-- | :-- |
| implementation-readiness-2-1 | L'encadré dit que le plan s'exécute après validation par le propriétaire. Le statut passe à « Approved » au dernier point (11) |
| implementation-readiness-2-2, style-2-3 | Règle de précédence réécrite : seul `CLAUDE.md` résume des procédures ; une ADR acceptée modifie le niveau 1 dans la même pull request ; un seul critère d'ADR ; texte exact de `docs/adr/README.md` |
| style-2-1 | `CLAUDE.md` : section « Ce qui est vérifié techniquement, et ce qui ne l'est pas », qui dit quels mécanismes filtrent quoi, et à partir de M0 seulement |
| style-2-2 | Les invariants de déterminisme s'appliquent « dans le paquet `core` », et le texte précise qu'ils ne valent pas pour les autres paquets |
| style-2-4, style-1-4, style-2-9, codebase-details-2-4, codebase-details-1-5 | Note de la RFC réécrite : liens explicites « §N du niveau 1 », ligne de statut remplacée, ADR rétroactive annulée, formulations corrigées |
| style-2-5 | Contrôle de `CLAUDE.md` fondé sur une liste fermée de règles |
| codebase-details-2-1 | Commandes de nettoyage corrigées, statut, encadré et rapports vérifiés |
| implementation-readiness-1-3, style-2-7, style-2-6 | Glossaire : convention de langue en tête, définitions reprises du document, règle à trois cas pour les identifiants, termes manquants ajoutés, « fonction publique » retirée, une seule entrée par terme |
| implementation-readiness-1-5 | La liste des scénarios en attente vit hors des chemins protégés, et l'étiquette « références régénérées » est posée |
| implementation-readiness-1-11 | Règle de calcul des ancres donnée, et grep élargi à une liste fermée de valeurs |
| implementation-readiness-2-3 à 2-6, codebase-details-2-2, 2-3, 2-5 à 2-7, style-1-7, style-2-8 | Corrigés : lien §11 unique, ordre de lecture, `cmp` avant la modification de la RFC, règle de preuve, format provisoire des termes interdits, rapports désignés par motif, lien §8, marques Create/Delete, textes imposés sans `>`, `git diff --cached`, phrases inexactes |
