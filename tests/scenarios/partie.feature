# language: fr
# Volet B de M1, réécrit par l'amendement 1 (docs/designs/niveau-2-m1-noyau.md, plan détaillé, points 20 et 23 ter).
# Les scénarios passent par le serveur en mémoire, en mode sans horloge, et par le protocole, sans le client Textual.
# Ils ne supposent pas la carte : les étapes lisent la géométrie dans l'observation. Réglages de test : ceux de
# tunables.toml, sauf jump_ticks = 5 et mining_rate = 10.

Fonctionnalité: Une partie jouée à travers le serveur en mémoire

  Scénario: Le propriétaire extrait ore_b, le ramène à la station qui le paie le mieux et le vend
    Étant donné une partie du serveur en mémoire sur les réglages de test, graine 1, sans horloge
    Et le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Alors le monde de la partie a au moins 8 systèmes
    Quand le propriétaire envoie son vaisseau vers le gisement de ore_b le plus proche
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de miner ore_b
    Et le serveur joue jusqu'à ce que la cargaison du propriétaire soit pleine
    Et le propriétaire envoie son vaisseau vers la station qui paie le mieux ore_b
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de vendre toute sa cargaison
    Et le serveur joue 1 tick
    Alors la dernière mise à jour du propriétaire montre la vente de sa cargaison au prix de la station de son système
    Et la dernière mise à jour du propriétaire montre un portefeuille égal au paiement moins la taxe
    Et aucune mise à jour de l'autre acteur ne montre la vente du propriétaire
    Et le journal des événements contient l'écriture de vente et l'écriture de taxe de cette vente

  Scénario: Les durées lues dans l'observation sont celles du jeu, sur les vrais réglages
    Étant donné une partie du serveur en mémoire sur les réglages de tunables.toml, graine 1, sans horloge
    Et le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Alors la dernière mise à jour du propriétaire montre dans ses réglages publics le jump_ticks et le mining_rate de tunables.toml
    Quand le propriétaire envoie son vaisseau vers un système voisin
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Alors le trajet du propriétaire a duré jump_ticks ticks
    Quand le propriétaire envoie son vaisseau vers le gisement le plus proche
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de miner le gisement de son système
    Et le serveur joue jusqu'à ce que la cargaison du propriétaire soit pleine
    Alors le minage du propriétaire a duré cargo_capacity ÷ mining_rate ticks

  Scénario: Une vente à une autre station que la station 1 se fait au prix de cette station
    Étant donné une partie du serveur en mémoire sur les réglages de test, graine 1, sans horloge
    Et le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Et le propriétaire envoie son vaisseau vers le gisement de ore_b le plus proche
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de miner ore_b
    Et le serveur joue jusqu'à ce que la cargaison du propriétaire soit pleine
    Et le propriétaire envoie son vaisseau vers la station 2
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de vendre toute sa cargaison
    Et le serveur joue 1 tick
    Alors la dernière mise à jour du propriétaire montre la vente de sa cargaison au prix de la station de son système

  Scénario: On ne voit un autre vaisseau, et le stock d'un gisement, qu'à proximité
    Étant donné une partie du serveur en mémoire sur les réglages de test, sur la première graine dont un système est à deux sauts de la station 1, un gisement à deux sauts ou plus, et un autre à un saut ou moins, sans horloge
    Et le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Et l'autre acteur envoie son vaisseau vers un système à deux sauts de celui du propriétaire
    Et le serveur joue jusqu'à l'arrivée du vaisseau de l'autre acteur
    Alors la dernière mise à jour du propriétaire ne montre pas le vaisseau de l'autre acteur
    Et la dernière mise à jour du propriétaire montre comme inconnu le stock de chaque gisement à deux sauts ou plus, et connu celui des autres
    Quand l'autre acteur envoie son vaisseau vers un système voisin de celui du propriétaire
    Et le serveur joue jusqu'à l'arrivée du vaisseau de l'autre acteur
    Alors la dernière mise à jour du propriétaire montre le vaisseau de l'autre acteur dans son système

  Scénario: Dans le système d'une station, on mine puis on vend sans saut
    Étant donné une partie du serveur en mémoire sur les réglages de test, sur la première graine dont une station et un gisement partagent un système, sans horloge
    Et le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Et le propriétaire envoie son vaisseau vers le plus proche système qui a une station et un gisement
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de miner le gisement de son système
    Et le serveur joue jusqu'à ce que la cargaison du propriétaire soit pleine
    Et le propriétaire ordonne à son vaisseau de vendre toute sa cargaison
    Et le serveur joue 1 tick
    Alors la dernière mise à jour du propriétaire montre la vente de sa cargaison au prix de la station de son système

  Scénario: Le PNJ vend une cargaison en 2 000 ticks sur un monde généré
    Étant donné une partie du serveur en mémoire sur les réglages de test, graine 1, sans horloge
    Et un PNJ joué par l'hôte des PNJ avec la politique scripted_miner
    Quand le serveur joue 2000 ticks
    Alors le journal des événements contient au moins une vente du PNJ
    Et le monde de la partie a au moins 8 systèmes

  Scénario: Un ordre au nom d'un autre acteur est refusé par la réception
    Étant donné une partie du serveur en mémoire sur les réglages de test, graine 1, sans horloge
    Et le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Et le propriétaire soumet, au nom de l'autre acteur, l'ordre de miner ore_a
    Et le serveur joue 1 tick
    Alors la dernière mise à jour du propriétaire montre son ordre refusé avec le code ACTOR_MISMATCH

  Scénario: Un ordre d'administration soumis par un client est refusé par la réception
    Étant donné une partie du serveur en mémoire sur les réglages de test, graine 1, sans horloge
    Et le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Et le propriétaire soumet, en son propre nom, un ordre d'administration d'aller dans un système voisin
    Et le serveur joue 1 tick
    Alors la dernière mise à jour du propriétaire montre son ordre refusé avec le code FORBIDDEN_CATEGORY
    Et la dernière mise à jour du propriétaire montre son vaisseau dans son système de départ, à l'arrêt

  Scénario: Au-delà du quota d'ordres d'un tick, les plus petits numéros sont gardés
    Étant donné une partie du serveur en mémoire sur les réglages de test, graine 1, sans horloge
    Et le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Et le propriétaire soumet dans le même tick 7 ordres d'aller dans un système voisin, numérotés de 1 à 7
    Et le serveur joue 1 tick
    Alors les ordres 6 et 7 du propriétaire sont refusés avec le code QUOTA_EXCEEDED
    Et aucun des ordres 1 à 5 du propriétaire n'est refusé avec le code QUOTA_EXCEEDED
