# Étape 5 — prise de recul initiale (Zoom Out)

*   **Document :** `docs/designs/niveau-2-m1-noyau.md` (636 lignes ; spécification : lignes 1 à 347 ; plan détaillé : lignes 348 à 636).
*   **Date :** 2026-11-06.
*   **Relecteur :** `egm-zoom-out`, sans contexte, standard `zoom-out-standard`. Contexte lu : niveau 1, glossaire, feuille de route, `CLAUDE.md`, niveau 2 de M0, termes interdits, et les fichiers que le plan touche (`.github/workflows/ci.yml`, `pytest.ini`, `pyproject.toml`, `.github/chemins-proteges.txt`, `.github/protection-main.json`, `tests/outillage/test_workflows.py`, `tests/scenarios/conftest.py`).
*   **Verdict :** le problème traité est le bon, et la portée suit la ligne M1 du §11 du niveau 1. Aucun constat bloquant. Les constats portent sur le coût de portée des décisions du 2026-11-06, des exigences ajoutées sans le dire, et des couplages qui engagent les jalons suivants.

## Constats

### Major 1 : la régénération des gisements ne borne rien aux valeurs choisies
- **Lignes :** 114 (ligne « Gisements » du tableau du point 1), 121, 149, 154, 323 à 327 (alternative G), 489.
- **Description :** la raison écrite dit que « la régénération borne l'émission de la station sur la durée », et l'alternative G est rejetée parce que, sans elle, « rien ne borne l'émission ». Or le plan dit lui-même (ligne 489) qu'avec `field_stock` = 20 000 et au plus 10 200 unités extraites par tranche, le stock ne limite pas les ventes de la partie de référence : aucun champ ne se vide, et le départage par tirage à clé n'a jamais lieu. Le mécanisme a pourtant un coût : stock par champ, refus « champ vide », événement de régénération, seule égalité à départager à M1, deux scénarios.
- **Raison :** la décision du propriétaire n'est pas contestée, mais la raison écrite contredit les valeurs du plan ; un lecteur croira que la régénération protège les fourchettes, alors qu'elle n'y joue aucun rôle à M1.
- **Correction :** écrire la vraie raison (choix de contenu du propriétaire, testé par scénarios, sans effet sur les fourchettes de M1) et corriger l'inconvénient de l'alternative G ; ou, si le propriétaire veut que la régénération borne vraiment l'émission, choisir des valeurs où elle agit et refaire le calcul des bornes (ligne 581).

### Major 2 : un seuil de mutation de 80 % est ajouté sans être une décision
- **Lignes :** 418 (point 9), 428 (point 11), 631 (Verification Plan).
- **Description :** le niveau 1, §10, exige seulement un score « jamais inférieur au score mesuré par la CI sur `main` ». Le document ajoute un seuil de 80 % pour un fichier nouveau et pour la mutation complète de nuit. Tous les fichiers de `src/fourx/` sont nouveaux à M1 : la règle du niveau 1 est vide pendant tout le jalon, et le seuil de 80 % est la seule exigence réelle.
- **Raison :** contraire à la règle de rédaction (ligne 97 : « n'en ajoute aucune ») ; absent du tableau des décisions du point 1 ; c'est le paramètre qui pèse le plus sur la charge du jalon.
- **Correction :** l'inscrire au tableau du point 1 comme décision du propriétaire, avec sa raison (sans plancher, le contrôle de mutation ne vérifie rien à M1) ; ou le retirer et dire que le contrôle ne mord qu'à partir de M2.

### Major 3 : les empreintes de référence dépendent de la politique scriptée et du serveur
- **Lignes :** 218, 219, 574 à 576 (point 27), point 26.
- **Description :** la partie de référence est jouée par `scripted_miner`, à travers `NpcHost` et `server`. Ses empreintes changent quand la politique, l'hôte des PNJ ou le moment de soumission des ordres change, même si les règles ne bougent pas ; il faut alors régénérer les références, et `test_revision.py` impose de monter `RULES_REVISION`.
- **Raison :** le niveau 1 (§3, §7) range les références par `rules_version`. Ici, `rules_version` monterait aussi pour un changement de politique ou de serveur. M4 enregistre `rules_version` pour chaque entraînement (§8) : une montée laisserait croire à un changement de règles.
- **Correction :** au minimum l'écrire (point 8, et circuit des pull requests de `CLAUDE.md`) ; ou figer le journal des ordres de la partie de référence dans `tests/references/` et le faire rejouer par `step` (l'alternative F a écarté une suite d'ordres écrite à la main, pas un journal enregistré et régénéré avec la révision). Choix du propriétaire.

### Major 4 : la configuration protégée de `mutmut` peut être masquée par un fichier non protégé
- **Lignes :** 383 à 388 (points 4 et 5), 340.
- **Description :** `mutmut` 3.8.0 lit d'abord `pyproject.toml`, puis `setup.cfg`. `setup.cfg` devient protégé, pas `pyproject.toml`. Une pull request de fonctionnalité pourrait ajouter une table `[tool.mutmut]` à `pyproject.toml` (un `do_not_mutate` très large) sans toucher de chemin protégé.
- **Raison :** le contrôle qui doit repérer les tests creux de l'agent de code pourrait être affaibli sans que le garde le signale (niveau 1, §10).
- **Correction :** `mutation.py` (protégé) échoue si `pyproject.toml` contient une table `tool.mutmut` ; un test au point 10, et si possible un canari au point 29.

### Major 5 : la tâche `tests-outillage` existante lancera toute la suite
- **Lignes :** 404 (point 8) ; `ci.yml` (`uv run pytest` sans filtre) et `pytest.ini` (`testpaths = tests`).
- **Description :** le point 8 dit que « les tests de l'outillage gardent leur tâche de M0 », sans la modifier. Or elle lance tout `tests/` : dès la phase 3, elle jouerait aussi le rejeu de 100 000 ticks, la partie `lent`, `hypothesis` et la mesure.
- **Raison :** chaque contrôle tournerait deux fois ; la mesure de 30 minutes du point 28 serait faussée.
- **Correction :** limiter `tests-outillage` à `uv run pytest tests/outillage`, au point 8.

### Major 6 : `tests/outillage/test_workflows.py` cassera à la phase 2
- **Lignes :** 425 à 428 (point 11), 400 à 409 (point 8), 609 à 612 (point 31) ; `tests/outillage/test_workflows.py`.
- **Description :** ce test exige exactement deux workflows (`ci.yml`, `garde.yml`) et une liste fermée de tâches obligatoires sans clé `name`. Créer `nuit.yml` le fait échouer ; les nouvelles tâches obligatoires échappent à la règle « pas de clé `name` », dont dépend la correspondance avec `protection-main.json`.
- **Raison :** la pull request d'outillage de la phase 2 serait rouge sur un contrôle déjà obligatoire.
- **Correction :** un point Modify `tests/outillage/test_workflows.py` en phase 2 (troisième workflow) et en phase 4 (liste des tâches obligatoires).

### Major 7 : le notebook et le test calculent la même métrique de deux façons
- **Lignes :** 225, 577, 583 à 586.
- **Description :** `test_fourchettes.py` calcule en Python ; le notebook recalcule en SQL DuckDB et affiche en plus la masse monétaire. « Aucun calcul que `test_fourchettes.py` ne fait pas » (ligne 586) est faux. La CI n'installe pas `duckdb` : le seul chiffre que voit le propriétaire n'est jamais testé.
- **Raison :** le niveau 1 (The Problem) nomme ce risque (définitions différentes, graphiques faux) ; M2 reprendra la méthode.
- **Correction :** une seule fonction de calcul qui lit le JSONL des événements v0 (par exemple dans `fourx.tools`), appelée par le test et par le notebook ; DuckDB n'affiche que. Sinon, corriger la ligne 586 et dire que le notebook n'est pas vérifié.

### Nit 1 : la masse monétaire n'est pas vérifiée explicitement
- **Lignes :** 109, 577. Le critère de sortie nomme la masse monétaire ; le test exclut la première tranche sans dire pourquoi. **Correction :** écrire et vérifier la borne déduite (croissance de 75 600 à 137 700 par tranche), justifier l'exclusion.

### Nit 2 : la preuve sur le portable est implicite
- **Lignes :** 46 à 50, 633. **Correction :** écrire que les références sont régénérées sur le portable (point 26), donc qu'un rejeu vert en CI prouve l'égalité avec le portable ; ou ajouter au compte rendu la sortie du rejeu sur le portable.

### Nit 3 : des lignes reprennent le niveau 1 sans rien décider
- **Lignes :** 107 (« Découpage du jalon »), 311 à 315 (alternative E). **Correction :** supprimer ou réduire à un renvoi.

### Nit 4 : « un bug volontaire par contrôle » ne correspond pas à la liste
- **Lignes :** 239, 595 à 600. Deux bugs pour `tests`, aucun pour `mutation`. **Correction :** reformuler, ou ajouter un canari de mutation (voir Major 4).

### Nit 5 : la partie de référence est jouée cinq fois, plus la mutation de base
- **Lignes :** 405, 416, 417, 575 à 577. **Correction :** faire lire à `test_fourchettes.py` les événements du rejeu de la même tâche ; prévoir l'option de ne pas recalculer le score de base.

### Nit 6 : `test_revision.py` a besoin de l'historique de `main`
- **Lignes :** 576, 404. **Correction :** préciser au point 8 la récupération de l'historique (`fetch-depth`) ou de la référence de base.

### Nit 7 : les noms neutres ne suivent pas ceux de `CLAUDE.md`
- **Lignes :** 104, 447. Le document emploie `system_1`, `ore_a`, `station_1` ; `CLAUDE.md` donne `station_a`, `ore_1`. **Correction :** ajouter au plan l'alignement de `CLAUDE.md` (chemin protégé).

### Nit 8 : « mutation, scénarios compris » n'atténue pas le risque visé
- **Lignes :** 61, 235, 388. Les tests unitaires tuent les mutants : des définitions d'étapes creuses passeraient. **Correction :** écrire l'interprétation retenue, ou proposer au propriétaire une passe de mutation limitée aux scénarios.

### Nit 9 : l'indicateur avancé est ambigu
- **Lignes :** 243, 579. « `step` seul », mais « 30 vaisseaux de PNJ scriptés ». **Correction :** dire si les ordres sont calculés hors de la mesure, ou si `observe` et la politique y entrent.

### Nit 10 : la raison donnée pour l'horloge est inexacte
- **Ligne :** 106. Le niveau 1 ne fixe aucun message de protocole (le glossaire renvoie leur choix au niveau 2 de M1). **Correction :** appuyer la décision sur la chronologie du tick (niveau 1, §2) et sur l'alternative C.

## Décompte

0 Blocker, 7 Major, 10 Nit.
