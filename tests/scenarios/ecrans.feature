# language: fr
# Amendement 1 de M1 : l'écran unique, lu à travers le modèle client et la mise en page, sans Textual
# (docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 23 ter ; Technical Plan, points 7 bis et 13).
# Le propriétaire est joué par ClientModel, attaché au serveur en mémoire comme client synchrone ;
# ses ordres partent par le modèle. Réglages de test : ceux de tunables.toml, sauf jump_ticks = 5
# et mining_rate = 10 ; « aux gisements vides » : de plus deposit_stock = 0.

Fonctionnalité: L'écran unique, lu à travers le modèle client

  Scénario: Un refus faute de gisement du minerai demandé est traduit et dit où aller
    Étant donné une partie du serveur en mémoire sur les réglages de test, graine 1, sans horloge
    Et le propriétaire joué par le modèle client
    Quand le serveur joue 1 tick
    Et le propriétaire ordonne à son vaisseau de miner un minerai qui n'a pas de gisement dans son système
    Et le serveur joue 1 tick
    Alors le refus traduit dit qu'il n'y a pas de gisement de ce minerai ici, et nomme le système du plus proche avec sa distance en sauts
    Et l'historique du modèle client contient ce refus traduit

  Scénario: Un refus sur un gisement vide nomme le plus proche gisement du même minerai qui n'est pas connu comme vide
    Étant donné une partie du serveur en mémoire sur les réglages de test aux gisements vides, sur la première graine dont le gisement le plus proche de la station 1 a un gisement du même minerai à deux sauts ou plus de lui, sans horloge
    Et le propriétaire joué par le modèle client
    Quand le serveur joue 1 tick
    Et le propriétaire envoie son vaisseau vers le gisement le plus proche
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de miner le gisement de son système
    Et le serveur joue 1 tick
    Alors le refus traduit dit que le gisement est vide, et nomme le plus proche gisement du même minerai qui n'est pas connu comme vide
    Et l'historique du modèle client contient ce refus traduit

  Scénario: Les ticks restants d'un trajet annoncés par le modèle client sont ceux du jeu
    Étant donné une partie du serveur en mémoire sur les réglages de test, sur la première graine dont un système est à deux sauts de la station 1, sans horloge
    Et le propriétaire joué par le modèle client
    Quand le serveur joue 1 tick
    Et le propriétaire envoie son vaisseau vers un système à deux sauts du sien
    Et le serveur joue 1 tick
    Alors les ticks restants annoncés par le modèle client sont ceux que le serveur joue ensuite jusqu'à l'arrivée

  Scénario: Les ticks restants d'un minage annoncés par le modèle client sont ceux du jeu
    Étant donné une partie du serveur en mémoire sur les réglages de test, graine 1, sans horloge
    Et le propriétaire joué par le modèle client
    Quand le serveur joue 1 tick
    Et le propriétaire envoie son vaisseau vers le gisement le plus proche
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de miner le gisement de son système
    Et le serveur joue 1 tick
    Alors les ticks restants annoncés par le modèle client sont ceux que le serveur joue ensuite jusqu'à la cargaison pleine

  Scénario: Vendre toute une cargaison mêlée part en deux ordres, sur deux ticks, tous deux acceptés
    Étant donné une partie du serveur en mémoire sur les réglages de test, graine 1, sans horloge
    Et le propriétaire joué par le modèle client
    Quand le serveur joue 1 tick
    Et le propriétaire envoie son vaisseau vers le gisement de ore_a le plus proche
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de miner ore_a
    Et le serveur joue 2 ticks
    Et le propriétaire envoie son vaisseau vers le gisement de ore_b le plus proche
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de miner ore_b
    Et le serveur joue jusqu'à ce que la cargaison du propriétaire soit pleine
    Et le propriétaire envoie son vaisseau vers la station qui paie le mieux ore_b
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire vend toute sa cargaison par le modèle client
    Et le serveur joue 3 ticks
    Alors le journal des événements montre deux ventes du propriétaire, d'un minerai chacune, sur deux ticks qui se suivent, la plus grosse d'abord

  Scénario: Une alerte signale l'arrivée à destination, et aucune un saut intermédiaire
    Étant donné une partie du serveur en mémoire sur les réglages de test, sur la première graine dont un système est à deux sauts de la station 1, sans horloge
    Et le propriétaire joué par le modèle client
    Quand le serveur joue 1 tick
    Et le propriétaire envoie son vaisseau vers un système à deux sauts du sien
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Alors le modèle client a une seule alerte d'arrivée, levée au tick de l'arrivée, qui nomme le système atteint

  Scénario: Une alerte signale la fin d'un minage arrêté par une cargaison pleine
    Étant donné une partie du serveur en mémoire sur les réglages de test, graine 1, sans horloge
    Et le propriétaire joué par le modèle client
    Quand le serveur joue 1 tick
    Et le propriétaire envoie son vaisseau vers le gisement le plus proche
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de miner le gisement de son système
    Et le serveur joue jusqu'à ce que la cargaison du propriétaire soit pleine
    Et le serveur joue 1 tick
    Alors le modèle client a une seule alerte de fin de minage, qui donne le minerai et la cargaison pleine

  Scénario: Aucune alerte ne signale un minage interrompu par un ordre
    Étant donné une partie du serveur en mémoire sur les réglages de test, graine 1, sans horloge
    Et le propriétaire joué par le modèle client
    Quand le serveur joue 1 tick
    Et le propriétaire envoie son vaisseau vers le gisement le plus proche
    Et le serveur joue jusqu'à l'arrivée du vaisseau du propriétaire
    Et le propriétaire ordonne à son vaisseau de miner le gisement de son système
    Et le serveur joue 2 ticks
    Et le propriétaire envoie son vaisseau vers un système voisin
    Et le serveur joue 2 ticks
    Alors le modèle client n'a aucune alerte de fin de minage

  Scénario: La carte d'un monde de 12 systèmes contient chaque système et chaque lien une fois
    Étant donné une partie du serveur en mémoire sur les réglages de test à 12 systèmes, graine 1, sans horloge
    Et le propriétaire joué par le modèle client
    Quand le serveur joue 1 tick
    Alors la carte du modèle client contient chaque système une fois, et chaque lien une fois, tracé ou écrit
