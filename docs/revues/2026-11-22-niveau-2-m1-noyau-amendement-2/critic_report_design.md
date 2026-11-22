# Étape 7 — Conception (amendement 2)

**Cible :** `docs/designs/niveau-2-m1-noyau.md`, passages marqués « amendement 2 » (l. 4-8, 49, 92-94, 126-128, 158, 169, 178-183, 205, 533, 537, 577-614, 880-887, 1071-1093, 1143-1152, 1514-1550).
**Pièces liées lues :** `docs/adr/0006-client-retro-8-bits.md`, `docs/designs/architecture-niveau-1.md`, `docs/glossaire.md`.
**Gabarit :** `(plugin EGM) resources/document_standards/feature-spec-standard.md`. **Persona :** design_critic, mode REVIEW.
**Revue complète :** tous les fichiers requis ont été lus.

## Verdict

**Non approuvable en l'état : 1 bloquant, 8 majeurs, 14 détails.**

La décision de fond tient. Le client reste dans Textual, et le protocole, l'observation et les règles ne changent pas. La disposition est déterministe et calculée une seule fois. Le clavier reste suffisant, et une partie d'essai est prévue. Le coût de calcul de la disposition par forces est négligeable : 300 itérations sur 66 paires de systèmes au plus, une fois par partie. Il ne faut pas y chercher de risque.

Les défauts sont ailleurs :
- deux informations affichées ne viennent pas de l'observation ;
- la prochaine étape a des trous de justesse et de complétude ;
- la lisibilité de la carte n'est pas garantie par le critère retenu (0,08) ;
- la palette confond deux rôles ;
- le critère de rendu n'a pas d'effet ;
- plusieurs passages, dont le plan de vérification, sont devenus caducs sans marque.

---

## Bloquant

### B1. La graine et la taxe sont affichées, mais ne viennent pas de l'observation

- **Passages :**
  - l. 583 : « En haut, une barre : tick, durée de jeu estimée, solde, **graine** » ;
  - l. 607 : « Marché : […] **la taxe est rappelée** » ;
  - à confronter avec l. 579 (« tout ce que l'écran montre se calcule à partir de l'observation et du modèle client »), l. 512 (« [la graine et le dossier] restent hors de l'écran de jeu : le client ne reçoit du jeu que l'observation (niveau 1, §5 ; ADR 0003) ») et l. 172 (`public_tunables` = `jump_ticks`, `mining_rate` seulement ; « la taxe [est] dans l'événement de vente »).
- **Problème :** la graine n'est pas dans `Observation`. `tax_rate_bp` n'est pas dans `PublicTunablesView`. Avant la première vente, le client ne peut connaître la taxe qu'en lisant les réglages ou en codant la valeur en dur. Les deux cas ouvrent un canal que le niveau 1, §5, interdit. L'autre issue serait d'élargir l'observation, ce qui change `protocol_version` et contredit « rien ne change dans le protocole ».
- **Conséquence :** l'agent de code doit choisir entre deux violations : un canal de plus vers le joueur, ou un changement de protocole sans ADR. La l. 512, qui fait foi depuis l'amendement 1, est contredite sans marque.
- **Proposition :**
  - retirer la graine de la barre : elle reste affichée au lancement et à la fermeture, comme le dit la l. 512 ;
  - pour la taxe, soit afficher « taxe : connue après la première vente », puis le taux déduit du dernier événement `Sale` (taxe ÷ paiement brut), soit retirer la mention.
  - Si le propriétaire veut vraiment la taxe dès le départ, il faut ajouter `tax_rate_bp` à `PublicTunablesView`, ce qui demande un complément à l'ADR 0003, `protocol_version` 3, et un amendement qui ne se dit plus « sans toucher aux règles/protocole ».

---

## Majeurs

### M1. La règle du minimum et la liste des ADR (point 1) ne sont pas mises à jour

- **Passages :**
  - l. 276 : « n'en ajoute aucune sauf le seuil de mutation ci-dessous et les objectifs 12 à 16, et ne le change que par les ADR 0003 à 0005 » ;
  - l. 297 : « comme les objectifs 12 à 16 » ;
  - l. 49 : la liste des passages touchés ne cite pas le point 1 ;
  - niveau 1, §11, ligne M1 (l. 498) : « client Textual minimal ».
- **Problème :** l'amendement ajoute les objectifs 17 à 19 et change le niveau 1 par l'ADR 0006. Or la règle qui gouverne le document dit encore qu'il n'y a rien au-delà des objectifs 12 à 16 ni d'autre ADR que 0003 à 0005. Aucune phrase ne dit non plus que les décisions du propriétaire du 2026-11-22 priment sur la règle du minimum, comme la l. 276 le fait pour l'amendement 1. Enfin, la souris, le zoom, la mini-carte, les bulles et l'aide s'écartent d'un client « minimal » au sens du niveau 1, §11, sans que l'ADR le traite : elle ne modifie que l'Overview.
- **Conséquence :** un relecteur ou un agent qui applique la règle du minimum peut juger les objectifs 17 à 19 hors cadre. Le document se contredit sur sa propre règle de rédaction.
- **Proposition :**
  - à la l. 276, ajouter « (amendement 2, précisé) : les décisions du propriétaire du 2026-11-22 priment aussi (objectifs 17 à 19) ; ADR 0006 » ;
  - corriger la l. 297 ;
  - ajouter le point 1 à la l. 49 ;
  - dans l'ADR 0006, écrire une phrase sur le « client Textual minimal » du §11 : soit il reste minimal au sens où il ne fait que lire l'observation, soit le §11 est aussi modifié.

### M2. Prochaine étape : les sept règles ne sont ni toutes justes ni complètes

- **Passage :** l. 595-603 et l. 180.
- **Problèmes :**
  1. **Il manque une règle pour un ordre en attente.** Après `d`, Entrée, ou `v`, le vaisseau reste « à l'arrêt » jusqu'au résultat, soit un tick, 3 s à la période nominale. Pendant ce temps, les règles 4 ou 7 redisent « vendre (`v`) » ou « aller… (`d`) ». Un second appui produit `SUPERSEDED`, `SHIP_EN_ROUTE`, ou remet la file de vente à zéro (l. 555). Le modèle connaît pourtant `pending` (l. 874).
  2. **La règle 3 est fausse dans un cas.** « en minage : soute pleine dans n ticks » ne vaut pas quand le stock est la borne. La l. 572 calcule bien min(capacité libre, stock). Il faut annoncer « fin du minage dans n ticks (soute pleine / gisement vide) », et « au plus n ticks » si d'autres vaisseaux visibles minent le même gisement.
  3. **La règle 7 n'a pas de repli.** Si tous les gisements du minerai le mieux payé sont connus vides, ou si aucun ne convient, rien n'est dit. La politique PNJ, elle, passe à l'autre minerai, puis reste à l'arrêt (l. 525).
  4. **Les départages ne sont pas fixés.** Les règles 5 et 7 ne disent pas quoi faire à prix égal entre stations ou minerais, ni à distance égale. Or les tests « cas par cas » (l. 181, l. 1545) supposent une sortie unique. La politique PNJ fixe ces départages (l. 524-525).
  5. **La logique est dupliquée.** Les règles 4 à 7 recopient presque les règles 1 à 3 de `scripted_miner`, avec des différences non dites : la règle 6 fait miner le gisement local quel que soit son prix. Deux implémentations voisines divergeront.
  6. **La durée manque.** L'objectif 18 promet « sa durée », mais les règles 6 et 7 n'en donnent aucune pour le minage.
- **Conséquence :** le panneau peut se tromper au moment où le joueur en a le plus besoin, juste après une action. Les tests ne peuvent pas être écrits sans trancher les cas ouverts.
- **Proposition :**
  - insérer une règle 1 bis : « un ordre envoyé attend son résultat : attendre (ordre affiché) » ;
  - réécrire la règle 3 comme ci-dessus ;
  - ajouter une règle 8 de repli (« autre minerai », puis « aucun gisement connu disponible : attendre la régénération ou explorer ») ;
  - reprendre explicitement les départages de la politique : prix, puis sauts, puis identifiant ;
  - soit réutiliser des fonctions de `policies` sans logique de décision, soit écrire une phrase qui liste les écarts voulus avec `scripted_miner` ;
  - donner la durée du minage dans les règles 6 et 7.

### M3. Disposition par forces : le critère retenu ne garantit pas la lisibilité

- **Passages :** l. 585 (« au moins 0,08 ; les tests de propriétés le vérifient »), l. 583 (carte sur environ 60 % de 120 × 36), l. 589 (pastille numérotée, `S1`, losange et stock ou « ? »), l. 1151 (parade : « distance minimale vérifiée ; zoom et bulle »).
- **Problèmes :**
  - **Les libellés se chevauchent au zoom ×1.** La carte fait environ 70 × 26 cases utiles, soit environ 70 × 52 pixels en demi-blocs. 0,08 correspond à 4 à 6 colonnes et à 2 lignes. Un système porte jusqu'à environ 10 caractères : « 12 », « S1 », « ◆20000 ». Les libellés de deux systèmes proches se chevaucheront donc presque à coup sûr.
  - **Le passage du carré [0, 1]² à une zone de 70 × 52 n'est pas défini :** ni le rapport d'aspect (étirement ou bandes), ni la normalisation après la simulation. Un étirement fausse la distance minimale.
  - **Les croisements de liens ne sont ni mesurés ni traités.** Le départ « sur un cercle, dans l'ordre des identifiants » favorise les croisements pour un arbre tiré au hasard. Le risque de la l. 1151 nomme les liens qui se croisent, mais sa parade n'y répond pas. L'amendement 1 mesurait au moins la part des liens tracés ; ce relevé disparaît sans remplaçant.
  - **« Toujours » n'est vérifié que sur un échantillon.** Aucune correction n'est prévue pour une graine qui violerait la distance : passe de séparation, mise à l'échelle.
  - **Les constantes restent ouvertes :** longueur du ressort, coefficients, décroissance du pas. Or la l. 105 exige « sans décision ouverte ».
- **Conséquence :** l'objectif 17 (« d'un coup d'œil »), réponse directe à la plainte du propriétaire, peut échouer à la partie d'essai pour une raison que les tests déclarent verte.
- **Proposition :**
  - définir la normalisation : boîte englobante, mise à l'échelle uniforme, marge ;
  - exprimer la distance minimale en cases après le passage à 120 × 36 et au zoom ×1, dérivée de la largeur du plus long libellé ;
  - ou n'afficher au zoom ×1 que la pastille et le losange, et laisser le stock à la bulle et aux zooms supérieurs ;
  - ajouter une passe finale de séparation ;
  - mesurer le nombre de croisements sur de nombreuses graines, le publier au compte rendu, et lui fixer un seuil d'alerte ;
  - envisager un départ en largeur d'abord (couches par distance à la station 1) plutôt que le cercle ;
  - fixer les constantes dans le document.

### M4. Palette : un rôle en double, une identité portée par la seule couleur, une dégradation non testée

- **Passages :** l. 581 (accent `#3FD0E0`, `ore_b` `#3FD0E0`), l. 589 (« un losange de la couleur de son minerai »), l. 614 et l. 1147 (« palette pensée pour rester lisible en 256 couleurs »).
- **Problèmes :**
  - **L'accent et `ore_b` ont la même couleur.** Tout élément d'accent (sélection, titre, curseur) se lit comme « `ore_b` ».
  - **Le minerai d'un gisement n'est porté que par la couleur au zoom ×1.** Le panneau Marché donne les prix, pas l'emplacement. L'objectif 12 (« où se trouve chaque minerai ») dépend donc d'une couleur ambiguë.
  - **La tenue en 256 couleurs n'est qu'affirmée.** Les cinq tons de fond et de trait (`#0B0E1A`, `#121830`, `#1B2444`, `#26304F`, `#2B3557`) tombent sur très peu d'entrées de la table xterm-256 : la séparation panneau / panneau clair / trait peut disparaître. En 16 couleurs (tmux sans couleurs vraies, console), Textual retombe sur le thème du terminal, ce qui est imprévisible.
  - **Les couples testés ne sont pas listés.** Le test de contraste porte sur les « couples employés », sans dire lesquels. Une étiquette colorée du journal (l. 608), par exemple du texte `#E8ECF8` sur alerte `#F0506E`, donne environ 2,9:1 et échouerait s'il était dans la liste. Personne ne le saura s'il n'y est pas.
- **Conséquence :** une information de jeu (le minerai) est mal codée. La parade du risque principal (l. 1147) n'est pas vérifiée.
- **Proposition :**
  - donner à l'accent une teinte propre, distincte des deux minerais ;
  - ajouter une lettre ou un glyphe distinct par minerai (« a » / « b », ◆ / ●) pour que la couleur ne soit jamais le seul support ;
  - déclarer dans `palette.py` une liste explicite des couples texte/fond employés, et la tester ;
  - tester aussi le contraste et la séparation des fonds après la réduction de Textual en 256 couleurs ;
  - inscrire dans le compte rendu de la partie d'essai si le terminal est en couleurs vraies (`COLORTERM`).

### M5. Rendu : le critère de redessin est sans effet, et la mesure renvoie à un point qui ne la contient pas

- **Passages :** l. 614 (« La carte n'est redessinée que si le zoom, la vue, la fenêtre ou l'observation changent. Le temps de rendu […] est mesuré au plan détaillé, point 28 bis ») et l. 1150.
- **Problèmes :**
  - **L'observation change à chaque tick.** Le tick, la fraction du saut et les stocks proches changent tout le temps. Le critère revient donc à redessiner à chaque tick, soit environ 33 fois par seconde au palier ×100 pour un canevas de 70 × 26 cases en Python.
  - **Le point 28 bis (l. 1607-1612) n'a reçu aucun ajout de l'amendement 2.** Aucune mesure de rendu n'y figure, et il porte sur « chaque pull request du palier 3 », après la partie d'essai du point 23 decies.
  - **Aucun seuil ni aucune décision n'est attaché à la mesure.**
- **Conséquence :** le risque « rendu trop lent aux paliers rapides » n'a ni signal effectif ni parade effective. La partie d'essai se jouera sans mesure.
- **Proposition :**
  - redessiner seulement si les données dérivées de la carte changent : position du vaisseau en pixels, ensemble des systèmes à portée, stocks visibles, vaisseaux visibles ;
  - plafonner la fréquence d'affichage, par exemple à 10 Hz ;
  - ajouter au point 28 bis un « Proposed Changes (amendement 2, ajout) » : mesurer le temps de rendu d'une mise à jour au palier ×100 sur la PR du point 23 nonies, avant le point 23 decies, avec un seuil (par exemple au-delà de 30 ms, l'agent le signale).

### M6. Objectif 12 : la vérification automatique ne correspond plus à l'écran

- **Passage :** l. 169 : « au besoin après défilement du cadre Carte : le test lit le contenu du cadre ».
- **Problème :**
  - la carte ne défile plus : elle se zoome et se déplace ;
  - c'est un canevas en demi-blocs, dont le contenu texte n'est plus une liste lisible ;
  - les prix n'apparaissent sur la carte qu'à partir du zoom ×2 ;
  - l'emplacement de chaque minerai n'est donné que par des losanges colorés (voir M4).

  La phrase « (amendement 2, réécrit) » ne change que la taille et le monde.
- **Conséquence :** le test promis ne peut pas être écrit tel quel. La part automatique de l'objectif 12 n'est plus définie.
- **Proposition :** dire, pour chacune des cinq informations, quel cadre la porte et comment le test la lit :
  - minerai et prix : panneau Marché, ou modèle de dessin de `MapView` (liste des libellés placés), ou carte au zoom ×2 ;
  - état et durées : panneau Vaisseau ;
  - ordres en attente : panneau Vaisseau ;
  - refus : journal.

### M7. Des passages devenus caducs ne sont pas marqués, et le plan de vérification n'est pas amendé

- **Passages :**
  - l. 79 (Overview, amendement 1 : « sans thème de couleur ») ;
  - l. 1138 (risque « Carte illisible », parade « rang du parent… autres liens écrits en texte », propre à `map_layout.py`) ;
  - l. 1710 (« `clients/model.py`, `map_layout.py` et `texts.py` sont mutés sans plancher ») ;
  - l. 1712 (« Carte : part des liens tracés et hauteur de la carte… publiées au compte rendu ») ;
  - l. 49 (le Verification Plan et le point 28 bis manquent dans la liste des passages touchés).
- **Problème :** la règle de préséance (l. 27) couvre le conflit en théorie, mais ces passages décrivent un module supprimé (l. 1093, l. 1544) et des mesures qui n'existent plus. Le plan de vérification ignore les objectifs 17 à 19, `force_layout.py`, `guide.py` et `palette.py`, la partie d'essai du point 23 decies, et les nouvelles mesures (disposition, croisements, rendu).
- **Conséquence :** le critère de sortie (l. 1703, « chaque objectif… correspond à une preuve ») ne sait pas quoi exiger. Un agent sans contexte suivra le plan de vérification d'origine.
- **Proposition :**
  - marquer les l. 79, 1138, 1710 et 1712 « (remplacé par l'amendement 2, voir Technical Plan, point 7 ter) » ;
  - ajouter un bloc « (amendement 2) » au Verification Plan : tests et propriétés de la disposition, croisements publiés, contrastes, `en_attente.txt` vide pour `ecrans.feature` à la fin du point 23 nonies, partie d'essai du point 23 decies, mesure de rendu ;
  - compléter la l. 49.

### M8. Alternatives : l'animation demandée par le propriétaire n'est pas pesée

- **Passages :** l. 128 (« une forme de gravité entre les nodes, comme le graphe d'Obsidian »), l. 585 (disposition statique : « la carte ne bouge pas »), alternatives AB à AE (l. 1071-1093), ADR 0006, options (a) à (d).
- **Problèmes :**
  - **La disposition est statique, alors que la demande citée évoque un graphe animé** et manipulable (dans Obsidian, les nœuds se déplacent et se tirent). C'est peut-être le bon choix (stabilité, tests, coût), mais il n'est ni dit ni justifié.
  - **Aucune autre méthode de disposition n'est pesée :** coordonnées tirées à la génération (l'alternative Y les rejetait pour l'état, mais pas une disposition par couches côté client), disposition par contraintes de distance, ou disposition en largeur d'abord.
  - **L'ADR ne compare aucune technique de dessin dans le terminal,** alors que c'est le cœur du risque de rendu : demi-blocs, Braille (2 × 4 points par case, des traits plus fins), protocoles graphiques kitty ou sixel (du vrai pixel art dans le terminal, avec Textual).
- **Conséquence :** la règle des alternatives du gabarit n'est pas satisfaite pour le choix central de l'amendement. La condition de révision de l'ADR saute directement aux options (c) et (d) et ignore les options qui restent dans le terminal.
- **Proposition :**
  - ajouter une alternative AF « carte animée façon Obsidian (simulation continue, nœuds déplaçables) », rejetée ou reportée pour des raisons datées : stabilité visuelle, tests du pilote, coût de rendu au palier ×100, et confirmation du propriétaire ;
  - ajouter une alternative AG sur la méthode de disposition ;
  - dans l'ADR, ajouter une option (b′) « graphismes du terminal (Braille / kitty / sixel) », et la citer dans la condition de révision.

---

## Détails

| N° | Passage (ligne) | Problème | Conséquence | Proposition |
| :-- | :-- | :-- | :-- | :-- |
| D1 | l. 94, 205 (« aide au premier lancement ») ; l. 610 (« s'ouvre au lancement de chaque partie ») | Deux comportements différents | Tests et attentes divergent | Choisir « à chaque lancement » (il n'y a pas de reprise avant M5) et aligner l'Overview et les Non-Goals |
| D2 | l. 610 (`help_pages(observation)`, aide au lancement) ; l. 507 | Au montage de l'application, aucune `TickUpdate` n'est encore arrivée ; la signature n'accepte pas `None` | Plantage ou durées absentes à l'ouverture | Ouvrir l'aide à la première mise à jour, ou accepter `Observation \| None` avec un texte d'attente |
| D3 | l. 610, 612 | Entrée ferme l'aide et acquitte aussi les alertes ; les flèches changent de page et déplacent aussi la vue ; Échap n'est pas cité | Ambiguïté des touches dans le pilote | Fixer la priorité : l'aide est modale, Entrée et Échap la ferment, les flèches tournent les pages tant qu'elle est ouverte |
| D4 | l. 591 (pas de 1,25, « à partir de ×2 ») | Les pas donnent 1,95 puis 2,44 : ×2 n'est jamais atteint, et le centre du zoom à la molette n'est pas défini | Seuil flou, zoom désorientant | Fixer le seuil à ≥ 1,9 (ou des pas 1 ; 1,5 ; 2 ; 3 ; 4) et zoomer autour du pointeur |
| D5 | l. 592-593 | Ni seuil entre glisser et cliquer, ni comportement du clic pendant une saisie, une alerte ou un trajet | Clics parasites ; ordre voué à `SHIP_EN_ROUTE` | Seuil de quelques cases ; clic ignoré si une saisie ou une alerte est ouverte ; en route, la bulle dit « en route » au lieu d'ouvrir la confirmation |
| D6 | l. 590, 593 | Pendant un saut, la distance de la bulle part du système quitté. Les vaisseaux proches ne sont visibles que par leur système et s'empilent sur le nœud | Distances fausses en route ; ▲ superposés | Calculer depuis le prochain système de la route (+ `ticks_to_next_jump`) ; afficher « ▲×3 » quand plusieurs vaisseaux partagent un système |
| D7 | l. 583 (« durée de jeu estimée ») | Sans « ≈ … à 3 s », elle contredit la règle de la l. 575 en `--dev` ou avec un autre `--periode` | Estimation trompeuse | Appliquer le même libellé que `duration_text` |
| D8 | l. 180 (« en tête de l'écran ») vs l. 583 (en haut de la colonne droite) ; place de la carte dans la hiérarchie | Écart de formulation ; la carte, 60 % de l'écran, est absente de la hiérarchie annoncée | Attente ambiguë à la partie d'essai | Écrire « en tête de la colonne droite » et situer la carte dans la hiérarchie |
| D9 | l. 583 (entre 100 × 30 et 120 × 36) | Ce qui rétrécit n'est pas dit | Cas non testé | Dire que la carte rétrécit et que les panneaux gardent leur largeur ; tester en 100 × 30 |
| D10 | l. 180 (« à partir de l'observation seule ») vs l. 881 (`next_step(observation, model)`) ; règle 7 (« pas connu comme vide ») | Le guide lit aussi le modèle. Sans mémoire des gisements vus vides (le PNJ en a une), il peut renvoyer le joueur vers un gisement déjà trouvé vide, soit au moins 40 minutes perdues par aller-retour à 3 s | Conseils répétés et coûteux | Écrire « l'observation et l'état du client, sans autre canal » ; faire garder au modèle les gisements vus vides, comme `NpcHost` |
| D11 | l. 1532 (scénario « la prochaine étape suit un cycle : aller miner, miner… ») | Si la station de départ partage son système avec un gisement, la première étape est « miner » et non « aller miner » | Scénario fragile selon le monde | Fixer le monde du scénario dans les étapes |
| D12 | l. 1532, 1545 (« toujours les mêmes ») | Comparer à des positions flottantes écrites en dur peut varier selon la plateforme | Faux échecs en CI | Comparer deux appels dans le même processus, ou deux sous-processus, jamais des valeurs écrites en dur |
| D13 | l. 1540-1543 ; l. 304 (toute dépendance nouvelle passe par une PR protégée) | Rien ne dit si le canevas demande une bibliothèque, alors que le point 23 septies ne touche pas `pyproject.toml` | Blocage possible au point 23 nonies | Écrire « sans dépendance nouvelle (rendu par segments Rich) », ou ajouter la dépendance au point 23 septies |
| D14 | ADR 0006, contexte et condition de révision ; l. 1080 (« comme les maquettes l'ont montré ») | Les maquettes, preuve du rejet de l'option (c), sont hors du dépôt. La révision ne vise que les causes « propres au terminal » | Justification invérifiable par un relecteur sans contexte ; rien n'est prévu si l'écran reste illisible pour une autre raison | Verser une capture SVG des maquettes (Textual sait l'exporter) dans le dossier de revue ; prévoir le cas « illisible pour une autre cause » (retour à la conception du point 7 ter) |
| D15 | l. 1536-1545 (une seule PR de fonctionnalité) | Le point 23 nonies réunit palette, guide, aide, panneaux, canevas, souris, zoom et mini-carte. Les plaintes du propriétaire (hiérarchie, aide, tutoriel) sont les moins coûteuses à traiter | Grosse PR, revue difficile, partie d'essai retardée | Couper en deux : 23 nonies (a) panneaux, guide, aide et palette ; (b) carte, souris et zoom |
| D16 | Glossaire ; Technical Plan, point 12 | « Portée » (définie à l'objectif 6 et très employée), « prochaine étape » (`next_step`), « disposition par forces » (`force_layout`), « aide » (`help_pages`) n'ont pas d'entrée | Vocabulaire non tenu | Ajouter ces entrées au glossaire, et le glossaire à la l. 49 |

---

## Cohérence avec le reste du document et le niveau 1 : synthèse

- **Visibilité par proximité :** cohérente pour les halos, les stocks « ? », les vaisseaux proches et la règle 6. Deux écarts relèvent de B1 (graine, taxe).
- **Point 7 bis :** le renvoi (l. 537) est propre. Il manque dans la liste des modules de la l. 531-535 `guide.py` et `palette.py`, qui ne figurent qu'au point 7 ter. C'est acceptable.
- **Non-Goals :** la l. 205 est cohérente avec l'ADR. La l. 204 (« disposition non figée ») reste vraie.
- **Niveau 1 :** l'Overview est déjà modifiée (l. 16) ; l'alternative N reste retenue. Restent le §11 « minimal » (M1) et le §5 (B1).
