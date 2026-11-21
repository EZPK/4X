# ADR 0004 — Fourchettes de la tranche 0

- **Numéro :** 0004
- **Titre :** Fourchettes de la tranche 0
- **Statut :** proposée
- **Date :** 2026-11-12
- **Décideur :** le propriétaire
- **Contexte :** le CUJ 1 du niveau 1 décrit la tranche 0 comme « un monde hors ligne généré à partir d'une graine, avec 3 à 5 systèmes reliés en graphe ; deux minerais, et une station PNJ qui rachète chacun à son propre prix fixe ». Le niveau 2 de M1 en a retenu le bas : 3 systèmes en ligne, 1 station, 1 PNJ. Après la partie de test du 2026-11-11, le propriétaire veut, « sans rentrer dans l'excessif », plus de nœuds, plus d'endroits où miner, plus de vaisseaux qui bougent et plus de points de vente. Avec trois systèmes en ligne et une station, il n'y a ni choix de route, ni choix du lieu de vente.
- **Options :**
  - **(a)** rester dans les fourchettes du niveau 1 : 5 systèmes, les deux minerais répartis en plusieurs gisements, plusieurs PNJ, une seule station. Aucune ADR, mais aucun choix du lieu de vente ;
  - **(b)** 5 systèmes et plusieurs stations, en précisant « au moins une station » ;
  - **(c)** une carte plus grande, dont la taille est tirée par la graine dans des fourchettes plus larges.
- **Décision :** l'option (c). La graine tire, dans le monde de la tranche 0 :
  - 8 à 12 systèmes reliés en un graphe connexe ;
  - 4 à 6 gisements, au moins deux de chaque minerai ;
  - 2 à 3 stations, chacune rachetant chaque minerai à son propre prix fixe, écrit dans les réglages ;
  - deux minerais, comme avant ;
  - 3 à 5 PNJ, chacun avec un vaisseau ;
  - une station et un gisement peuvent partager un système (décision du propriétaire, 2026-11-12) : un tel gisement rapporte vite puis s'épuise, et oblige à aller miner ailleurs. Au moins une station partage son système avec un gisement dans 84 % des mondes générés, et avec un gisement de `ore_b` dans 52 % (calculs du 2026-11-12 et du 2026-11-13).

  Les fourchettes sont des réglages : les changer change `rules_version`.
- **Conséquences :**
  - le CUJ 1 du niveau 1 reprend les fourchettes de systèmes, de gisements et de stations (il ne donne pas de nombre de PNJ) ;
  - la décision « Taille de la tranche 0 » du niveau 2 de M1 est remplacée par l'amendement 1 ;
  - `world.generate` tire la taille, le graphe (un arbre puis quelques liens) et l'emplacement des sites ; les scénarios ne supposent plus une carte fixe ;
  - le client affiche une carte en graphe ;
  - les bornes de l'économie du volet C se calculent sur la carte de la partie de référence : au moins une vente par fenêtre, et un plafond tiré de la carte ;
  - option écartée : interdire la colocalisation, qui aurait demandé au moins 9 systèmes (alternative AA du niveau 2 de M1).
- **Condition de révision :** la carte devient illisible sur un terminal de 80 × 24 ; ou la durée du rejeu de la partie de référence dépasse la limite de la CI ; ou un jalon suivant fixe la taille du monde en ligne.
- **Section du niveau 1 modifiée :** CUJ 1 (le propriétaire joue la tranche 0), les deux premières puces de « Given ».
