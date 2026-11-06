# Étape 7 — critique (conception, structure, style)

*   **Document :** `docs/designs/niveau-2-m1-noyau.md` (636 lignes ; spécification : lignes 1 à 347 ; plan détaillé : lignes 348 à 636).
*   **Date :** 2026-11-06.
*   **Relecteurs :** trois relecteurs sans contexte, en parallèle, avec le standard `feature-spec-standard` :
    - `egm-design` (conception), qui a aussi lu le niveau 1, le glossaire, `CLAUDE.md`, `.importlinter`, `.github/workflows/ci.yml`, `.github/chemins-proteges.txt`, `pytest.ini` et `tests/scenarios/conftest.py` ;
    - `egm-structural` (structure), qui a aussi lu le niveau 2 de M0 comme modèle ;
    - `egm-style` (style), qui a aussi lu le glossaire et les termes interdits.
*   **Préfixes :** C = conception, S = structure, Y = style. Les renvois « étape 5 » et « étape 6 » visent `zoom_out_report.md` et `comprehension_report.md`.
*   **Vérification de l'agent de code :** C-B1 relu aux lignes 146 et 178 à 183. L'observation doit contenir « les événements visibles du dernier tick, et les résultats de ses ordres », mais aucun passage ne dit où `observe` les trouve. Constat confirmé.
*   **Termes interdits :** aucun (recherche sans tenir compte de la casse, par le relecteur de style).

## Synthèse

| Relecteur | Blocker | Major | Nit |
|---|---|---|---|
| Conception | 1 | 19 | 10 |
| Structure | 1 | 8 | 11 |
| Style | 0 | 17 | 13 |
| **Total brut** | **2** | **44** | **34** |

Après le retrait des doublons (avec les étapes 5 et 6, et entre relecteurs), il reste **2 Blockers et 29 Majors nouveaux** ; les autres Majors confirment des constats déjà relevés.

## Conception

### C-B1 : aucun chemin ne porte les résultats d'ordre et les événements du dernier tick jusqu'à l'observation
- **Lignes :** 146, 178 à 183, 204, 474.
- **Description :** `step` renvoie `(state, events)` et `observe(état, acteur)` ne reçoit que l'état ; le document ne range ni les événements du dernier tick ni les `OrderResult` dans `State`. Aucun événement n'existe pour un ordre accepté, donc son « budget restant » n'est connu nulle part. Les refus prononcés à la réception (format, quota, acteur usurpé) arrivent avant `step` : ils ne sont ni journalisés, ni dans l'état, ni transportés par un message.
- **Raison :** niveau 1, §5 (« Chaque ordre reçoit un résultat structuré », « Il n'y a pas d'autre canal vers le joueur », signature de `observe`) ; ligne 38 (« sans décision ouverte ») ; engage `TickUpdate` à M3 et l'observation à M4.
- **Correction :** ranger dans `State` les événements et les résultats du dernier tick, remplacés à chaque `step` et comptés dans les empreintes. Pour les refus de la réception : (a) journaliser l'ordre refusé, que `step` refuse avec le code reçu, ou (b) ajouter un champ à `TickUpdate` en justifiant l'écart avec le §5. Inscrire le choix au tableau du point 1.
- **Recoupe :** étape 6, question 12 et N19.

### C-M1 : le registre de l'état garde toutes les écritures
- **Lignes :** 132, 158 à 165, 169, 172, 181.
- **Description :** si `State` garde toutes les `LedgerEntry` depuis le tick 0, l'empreinte du registre réencode tout l'historique à chaque tick (O(ticks²) sur 100 000 ticks), chaque phase recopie ce tuple, et l'instantané du monde en ligne grossit sans limite à M5. Les écritures sont déjà émises comme événements.
- **Correction :** l'état garde les soldes, les écritures du tick courant et des compteurs cumulés par motif ; l'historique vit dans les événements. Ajouter l'alternative.

### C-M2 : plusieurs ordres d'un même tick peuvent violer la conservation
- **Lignes :** 138 à 143, 146 à 152.
- **Description :** chaque ordre est validé contre l'état T. Deux ventes du même vaisseau, chacune sous la cargaison mais dont la somme la dépasse, passent toutes les deux, et la cargaison devient négative. Non définis : une vente arrête-t-elle un trajet ou un minage ; que devient un vaisseau redirigé pendant un saut ; un ordre ultérieur du même tick remplace-t-il le précédent.
- **Raison :** niveau 1, §4, invariant 3 (aucune quantité négative).
- **Correction :** validation séquentielle sur un état provisoire qui réserve la cargaison vendue, ou « un seul ordre retenu par vaisseau et par tick » ; définir le changement de route en cours de saut ; scénario « double vente refusée ».

### C-M3 : la référence scriptée n'est pas idempotente
- **Lignes :** 212, 581.
- **Description :** rien n'empêche la politique de renvoyer « miner » à chaque tick ; chaque ordre accepté remplace l'activité et consomme une action. Le calcul des bornes suppose quatre décisions par aller-retour.
- **Correction :** la politique n'émet un ordre que si l'activité observée diffère de l'activité voulue ; test « aucun ordre sur 10 ticks de minage ».

### C-M4 : identifiants en chaînes, contre des entiers au niveau 1
- **Lignes :** 104, 121, 127 à 131, 138, 169.
- **Recoupe :** étape 6, M7 (même constat). Correction : identifiants entiers dans l'état, noms neutres à l'affichage, correspondance dans `world.py`.

### C-M5 : le générateur à clé n'est pas spécifié assez pour une seconde implémentation
- **Lignes :** 149, 154, 171, 487.
- **Description :** l'encodage en octets de la clé n'est pas fixé (largeur, boutisme, encodage du motif, taille du condensé, bits tirés), et un seul tirage par champ ne suffit pas à ordonner N vaisseaux.
- **Raison :** niveau 1, §2 (« reproductible en Rust »).
- **Correction :** fixer l'encodage canonique ; ordonner par (tirage sur graine, tick, champ, vaisseau, motif ; identifiant) ; un vecteur de test figé.
- **Recoupe :** étape 6, M11 (départage) ; la partie « encodage » est nouvelle.

### C-M6 : le contrôle statique du déterminisme laisse des trous
- **Lignes :** 170, 173, 486, 504.
- **Description :** `float()`, `x ** -1`, `divmod`, `pow`, `operator.truediv`, `decimal`, `fractions`, `statistics` restent possibles ; `hash()` et `id()` ne sont pas interdits ; l'exemption de `arith.py` n'est pas écrite.
- **Correction :** liste fermée d'imports permis dans `core` ; fonctions intégrées interdites (`float`, `hash`, `id`, `divmod`, `pow`, `round`, `open`, `input`, `vars`, `globals`) ; `**` permis avec un exposant littéral positif ou nul ; exemption nommée pour `arith.py`.

### C-M7 : enveloppe des événements ambiguë
- **Lignes :** 141, 181, 207.
- **Description :** la régénération n'a ni acteur ni cause ; les ordres de création n'ont pas d'acteur émetteur ; la règle de `seq` n'est pas fixée ; l'identité d'un ordre (dont dépend `causation_id`) n'est pas définie ; un numéro répété dans un tick n'est pas traité.
- **Correction :** `actor_id`, `actor_kind`, `causation_id` facultatifs pour un fait des règles ; `seq` dans l'ordre des phases puis des identifiants ; `causation_id` = (`actor_id`, `tick`, numéro) ; numéro répété refusé.
- **Recoupe :** étape 6, M14 (acteur des ordres d'administration).

### C-M8 : rien n'empêche un client de soumettre un ordre d'administration
- **Lignes :** 141, 183, 204.
- **Description :** `Order` porte sa catégorie ; la ligne 141 dit « émis par le serveur seulement », mais ni `validate_orders` ni `Reception` ne refusent une catégorie autre que « joueur » venant d'un point de connexion.
- **Raison :** niveau 1, §3 et §5 ; exploitable à M3 par WebSocket.
- **Correction :** refus à la réception, avec un `RefusalCode` dédié ; un scénario au point 20 et un canari.

### C-M9 : la visibilité n'a pas de mécanisme, et la plupart des événements n'ont pas de classe
- **Lignes :** 180, 181, 477, 494, 510.
- **Description :** le document ne dit pas comment un champ « porte » sa classe ; les vues de `schema` écrites à la main rendent le test de propriétés tautologique ; les classes de six types d'événements manquent.
- **Correction :** classe déclarée en métadonnée de chaque champ de `State` ; un test générique entre vues et état ; un tableau des classes par type d'événement.
- **Recoupe :** étape 6, M8 (tableau des classes) ; le mécanisme et le test générique sont nouveaux.

### C-M10 : la concurrence entre Textual et l'horloge n'est pas choisie
- **Lignes :** 106, 187 à 203, 531.
- **Description :** fil séparé ou tâche asyncio ; la frontière « reçu avant le début du tick T+1 » en dépend.
- **Correction :** une seule boucle asyncio, horloge en tâche, point de connexion en `asyncio.Queue`, mode sans horloge synchrone.

### C-M11 : le stock ne contraint jamais la partie de référence
- **Lignes :** 114, 121, 326, 489, 581, 600.
- **Recoupe :** étape 5, Major 1, et étape 6, B1 (même cause). Correction nouvelle proposée : une seconde partie de référence, petite et contrainte par le stock, ou un canari sur un tirage toujours exécuté, plus l'interdiction statique de `hash` (C-M6).

### C-M12 : la partie de référence dépend de `policies`, `clients` et `server`
- **Lignes :** 218, 321, 574, 575.
- **Recoupe :** étape 5, Major 3 (même constat). Le relecteur ajoute l'effet sur M5 (compatibilité au déploiement) et recommande le journal d'ordres figé.

### C-M13 : `test_revision.py` contredit la création de `rules-1`
- **Lignes :** 497, 565, 576.
- **Description :** la tranche A fusionne `RULES_REVISION` = 1 ; la tranche C crée `tests/references/rules-1/` ; `test_revision` exige alors une révision supérieure à 1. Le contrôle `tests` passe au rouge, ou le dossier `rules-1` est faux.
- **Correction :** exemption « `main` n'a pas encore de références », ou `RULES_REVISION` introduit dans la même pull request que la première référence.
- **Recoupe :** étape 6, question 13 et N12 ; la contradiction est nouvelle.

### C-M14 : `tests-outillage` lancera tout
- **Lignes :** 404, 409.
- **Recoupe :** étape 5, Major 5. Ajout : le niveau 2 de M0 (ligne 286) prévoyait que `tests-outillage` « devient `tests` » à M1, ce que le plan contredit sans le dire.

### C-M15 : les nouvelles tâches seront rouges dès la phase 2
- **Lignes :** 352, 357, 403 à 407.
- **Recoupe :** étape 6, M9 (même constat).

### C-M16 : la mutation repose sur des tests non déterministes
- **Lignes :** 388, 416 à 418.
- **Description :** les tests `hypothesis` ne sont pas exclus de `mutmut` ; leur tirage fait varier le nombre de mutants tués entre la base et la tête, et la règle « score jamais inférieur » échouera au hasard.
- **Correction :** profil `hypothesis` `derandomize=True`, sans base d'exemples, sous `mutmut` et en CI, ou exclure `proprietes` de la mutation.

### C-M17 : une modification des définitions d'étapes seules ne déclenche aucune mutation
- **Lignes :** 235, 415.
- **Recoupe :** étape 6, M2, et étape 5, Nit 8. Correction précisée : quand `tests/scenarios/steps/` change, muter les modules exercés (ou tout `core`) et comparer à la base.

### C-M18 : pas de canari pour la mutation
- **Lignes :** 239, 595 à 600.
- **Recoupe :** étape 5, Nit 4 ; S-M6 ; Y-M16. Correction : un bug volontaire qui ajoute dans `core` une fonction appelée mais non vérifiée.

### C-M19 : la section Risks & Mitigations manque
- **Recoupe :** S-B1 (même constat, porté au rang de Blocker par le relecteur de structure).

### Nits de conception
- **C-N1** (lignes 418, 428) : seuils de 80 % sans justification. Recoupe étape 5, Major 2 ; étape 6, M3 ; S-M4.
- **C-N2** (lignes 218, 219, 497, 527) : l'empreinte de `tunables.toml` porte sur les octets bruts (un commentaire change `rules_version`) ; références rangées par révision au lieu de `rules_version`. Correction : empreinte de l'encodage canonique de `Tunables`. Recoupe étape 6, N13.
- **C-N3** (ligne 180) : la graine est à la fois dans l'état et en paramètre de `step` ; dire laquelle fait foi au rejeu.
- **C-N4** (lignes 243, 579) : l'indicateur avancé ne mesure que `step`, alors que l'entraînement appelle aussi `observe`. Recoupe étape 5, Nit 9.
- **C-N5** (ligne 180) : la visibilité de `actor_kind` (visible en jeu, niveau 1, §5) n'est pas listée.
- **C-N6** (lignes 115, 180) : stock, position et prix publics permettent de déduire la cargaison et les recettes d'un autre acteur ; le dire et l'accepter pour M1.
- **C-N7** (ligne 110) : `fourx.__main__` pourrait recevoir un contrat d'imports qui lui interdit `fourx.core`.
- **C-N8** (ligne 529) : `git rev-parse HEAD` ignore un dossier de travail modifié ; ajouter un drapeau « modifié ».
- **C-N9** (ligne 576) : `fetch-depth` pour `test_revision.py`. Recoupe étape 5, Nit 6.
- **C-N10** (lignes 206, 207, 216) : ordres de création « au tick 0 » et instantané initial au tick 0 : dire s'ils sont appliqués au premier `step`.

## Structure

### S-B1 : la section « Risks & Mitigations » manque
- **Lignes :** entre 335 et 337.
- **Description :** les risques sont dispersés (casse de `mutmut` lignes 111 et 309, durée de la CI lignes 335 et 588, fenêtre des phases 2 à 4 ligne 357, compilation de `duckdb` ligne 443, preuve sur la seconde machine ligne 108). Trois risques que le niveau 1 date de M1 ne sont repris nulle part : définitions d'étapes creuses, fuite d'un champ caché par `observe`, empreintes changées par une montée de Python ou de `msgspec`.
- **Raison :** le standard exige cette section ; le niveau 2 de M0 l'a (sa ligne 532).
- **Correction :** ajouter « ## Risks & Mitigations » après les Non-Functional Requirements, au format de M0 (Risque | Effet | Signal | Parade), avec les risques dispersés, les trois risques M1 du niveau 1, et ceux de C-M1, C-M2, C-M11, C-M12, C-M16, C-B1.

### S-M1 : pas de section CUJ, alors que la ligne 9 annonce « Given / When / Then »
- **Lignes :** 9, 15 à 91.
- **Correction :** ajouter « ## Critical User Journeys (CUJs) » (CUJ 1 et CUJ 4 adaptés à M1), ou retirer la mention de la ligne 9 et renvoyer aux CUJ du niveau 1.

### S-M2 : renvois faux ou incomplets vers les fourchettes et les valeurs
- **Lignes :** 224 (« point 1 » au lieu de 27), 109 et 156 (sans numéro).
- **Recoupe :** étape 6, M5 (ligne 224). Ajout : ligne 109 → point 27, ligne 156 → point 17.

### S-M3 : la mesure de durée de la CI est rangée sous le notebook
- **Lignes :** 588, 335. **Recoupe :** étape 6, M5.

### S-M4 : le seuil de 80 % n'existe que dans le plan
- **Recoupe :** étape 5, Major 2 ; étape 6, M3. Correction précisée : le porter au Technical Plan, point 10 (ligne « mutation » du tableau et paragraphe des contrôles de nuit).

### S-M5 : le test des entiers sur 64 bits change de contrôle selon la section
- **Lignes :** 233 (`hypothesis`), 505 (`tests/core/test_entiers_64_bits.py`, contrôle `tests`), 510 (non repris).
- **Correction :** choisir un emplacement et aligner la ligne 233 et les points 18 et 19.

### S-M6 : « un bug par contrôle » ne correspond pas au plan
- **Recoupe :** étape 5, Nit 4 ; C-M18 ; Y-M16.

### S-M7 : la vérification du Goal 7 n'a aucun point du plan
- **Ligne :** 60.
- **Description :** « un test vérifie la présence de chaque champ » de version (journal, instantanés, événements, protocole, règles) ; aucun point ne crée ce test (le point 23 ne couvre que le journal).
- **Correction :** nommer le test (par exemple `tests/core/test_versions.py`) dans le point 18 ou un point dédié.

### S-M8 : un engagement de M0 envers M1 n'est repris nulle part
- **Lignes :** point 11 (425 à 428).
- **Description :** le niveau 2 de M0 (Approved) annonce un contrôle de nuit qui relit la protection de `main` à partir de M1 (ses lignes 541 et 564). `nuit.yml` ne contient que `canari` et `mutation-complete`.
- **Correction :** ajouter la tâche au point 11 avec son objectif, ou la placer dans les Non-Goals avec le jalon qui la prend.

### Nits de structure
- **S-N1** (lignes 449, 512, 547) : les titres « Tranche A / B / C » sont au même niveau (H4) que les points qu'ils contiennent.
- **S-N2** (ligne 361) : ajouter « (pull request protégée) » au titre de la phase 1.
- **S-N3** (lignes 113 à 117 ; 73, 103, 287 à 291) : le tableau des décisions répète le détail du Technical Plan ; la perte de vaisseau est traitée trois fois. Garder la décision et la raison, renvoyer au point qui détaille. Recoupe étape 5, Nit 3.
- **S-N4** (lignes 572, 577, 579) : ligne vide qui coupe la liste du point 27 ; Type / Scope incomplet (marques `lent` et `mesure`).
- **S-N5** (lignes 359, 388, 407, 489, 563, 567) : ajouter à la ligne 11 qu'un « point N » sans préfixe renvoie à la même partie. Recoupe étape 6, N15.
- **S-N6** (lignes 224, 232, 405, 577) : la spécification ne dit pas que la première tranche est exclue, ni que `rejeu` lance aussi le test `lent`.
- **S-N7** (lignes 612, 619, 633) : créer des points « Action — … » pour l'application de la protection, le rejeu sur la seconde machine et les pull requests d'essai rouges.
- **S-N8** (lignes 183, 473) : renvoyer de la ligne 183 à la valeur de `ORDER_QUOTA_PER_TICK` (point 16).
- **S-N9** (lignes 565 à 567) : le point 26 dépend du point 27 mais vient avant.
- **S-N10** (lignes 237, 612) : définir la notation `!` comme M0 (sa ligne 12). Recoupe étape 6, N5.
- **S-N11** (lignes 370, 623, 630) : Type / Scope du point 33 sans « chemin protégé » ; commande manquante pour le contrôle des termes interdits. Recoupe étape 6, N7.

## Style

### Majors de style
- **Y-M1 : « champ » a deux sens** (champ de données : lignes 32, 57, 59, 60, 125, 180, 488, 510 ; champ de minerai : lignes 114, 121, 128, 139, 149, 152, 154, 165, 181, 212, 459, 460, 581), et « gisement » est un synonyme (lignes 21, 114, 327). La ligne 180 mélange les deux sens. **Correction :** « gisement » pour l'entité du jeu (identifiants `field_stock` inchangés), « champ » pour les données.
- **Y-M2 : « tranche » a trois sens** (« tranche 0 » du glossaire ; groupe de pull requests, lignes 353, 445, 447, 449, 512, 547, 588 ; période de 1 000 ticks, lignes 109, 224, 489, 577, 581, 586). **Correction :** « fenêtre de 1 000 ticks », « volet A / B / C », « tranche » réservé à « tranche 0 ».
- **Y-M3 : « phase »** désigne à la fois l'étape d'un tick (glossaire) et les étapes du plan (lignes 350, 357, 361, 378, 445, 588, 590, 614). **Correction :** « palier » pour le plan, ou « phase du tick » partout où le sens du glossaire est visé.
- **Y-M4 : « écriture »** (terme du registre) au sens d'« action d'écrire » (lignes 23, 313, 545). **Correction :** « enregistrement », « la règle la plus simple à coder », « sortie JSONL ».
- **Y-M5 : « empreinte du commit »** (lignes 205, 529) : écrire « l'identifiant (SHA) du commit ».
- **Y-M6 : « réglage »** pour un paramètre du serveur (lignes 106, 203, 303) : écrire « paramètre du serveur ».
- **Y-M7 : synonymes du PNJ de M1** (« PNJ scripté », « référence scriptée », « le PNJ ») ; la ligne 212 fait de la référence scriptée « une politique », alors que le glossaire en fait un PNJ. **Correction :** une définition au point 7, puis « PNJ » partout.
- **Y-M8 : « station PNJ »** (lignes 17, 105, 129) alors que la ligne 113 dit que la station n'est pas un acteur : écrire « station ».
- **Y-M9 : « joueur » seul** (lignes 115, 211, 299, 518) : « acteur » ou « propriétaire » selon le cas.
- **Y-M10 : « le compte d'un autre »** (ligne 115) : écrire « le portefeuille d'un autre ».
- **Y-M11 : « correctif » pour un bug injecté** (lignes 595, 602, 607, 632) : écrire « bug volontaire ».
- **Y-M12 : phrase incompréhensible** (ligne 632, « liste des attrapés »). Recoupe étape 6, M13.
- **Y-M13 : « client graphique »** (lignes 45, 517) : écrire « le client Textual ».
- **Y-M14 : antécédent ambigu** (ligne 212, « champ non vide du minerai le mieux payé ») : « parmi les gisements non vides, aller à celui dont le minerai est le mieux payé ».
- **Y-M15 : « scénarios compris »** (lignes 61, 235). Recoupe étape 5, Nit 8 ; étape 6, M2.
- **Y-M16 : « un par contrôle »** (ligne 239). Recoupe S-M6, C-M18.
- **Y-M17 : phrases trop longues** (lignes 109, 114, 359, 489, 518, 575, 581). Ligne 581 : passer le calcul des bornes en liste ; ligne 489 : séparer valeurs et justification, et remplacer « ce qui garde ses bornes ».

### Nits de style
- **Y-N1** : anglicismes évitables (« game design » lignes 5, 99 ; « POC » ligne 295 ; « lore » lignes 82, 99 ; « notebook » lignes 56, 225, 383, 586 ; « Drafted with EGM » ligne 636).
- **Y-N2** : registre familier (« rouge », « vert », « tient debout », « remonté », « proprement », « tests creux »).
- **Y-N3** : jargon non défini à la première occurrence (« par `!` », « point de connexion » ligne 204, « le lanceur » ligne 540, « le portable » lignes 19, 48).
- **Y-N4** (ligne 211) : « journal » pour l'historique du client, en collision avec le journal des ordres.
- **Y-N5** (ligne 409) : « actions » pour les actions GitHub, en collision avec le budget d'actions.
- **Y-N6** : raccourcis (« le garde » ligne 433, « l'acteur usurpé » ligne 474, « horloge en mode sans horloge » ligne 545, « Une partie est un dossier » ligne 206, « Elles deviennent un chemin protégé » ligne 218).
- **Y-N7** : antécédents ambigus (lignes 357, 164, 218).
- **Y-N8** : formulations elliptiques (lignes 170, 171, 303, 443, 567, 624).
- **Y-N9** : tournures lourdes (ligne 106, « à la demande du client demanderait » ; ligne 36, « en de nombreuses copies »).
- **Y-N10** : même refus formulé deux fois (lignes 140 et 462).
- **Y-N11** (ligne 183) : « l'entraînement » pour « l'environnement d'entraînement ».
- **Y-N12** (lignes 11, 38) : « partie » au sens de « section ».
- **Y-N13** : typographie (ligne 359, parenthèses accolées ; ligne 219, « = » dans la prose ; ligne 578, ligne vide dans la liste).

## Constats nouveaux qui demandent une décision du propriétaire

1. **C-B1** : où vivent les résultats d'ordre et les refus de la réception (dans `State`, ou par l'ordre refusé journalisé, ou par un champ de `TickUpdate`).
2. **C-M2** : règle pour plusieurs ordres d'un même vaisseau dans un tick.
3. **C-M10** : modèle de concurrence (une seule boucle asyncio proposée).
4. **S-M8** : contrôle de nuit de la protection de `main`, promis par M0 : à M1 ou dans les Non-Goals.
5. **Y-M1, Y-M2, Y-M3** : renommages (« gisement », « fenêtre », « palier » ou « volet ») ; « gisement » touche aussi le glossaire.

Les autres constats nouveaux ont une correction technique sans choix de fond.

## Décompte

- Brut : 2 Blockers, 44 Majors, 34 Nits (80 constats).
- Après retrait des doublons : 2 Blockers (C-B1, S-B1), 29 Majors nouveaux (11 de conception, 4 de structure, 14 de style), 15 Majors qui recoupent les étapes 5 et 6 ou un autre relecteur.
