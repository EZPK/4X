# language: fr
# Volet A de M1 : le noyau, les règles et le registre (docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 15).
# Chaque scénario part d'un état construit explicitement, sans dépendre de la graine, et applique step directement.
# Les trois invariants du registre et des biens sont vérifiés après chaque tick.

Fonctionnalité: Les règles de la tranche 0 appliquées par le noyau

  Contexte:
    Étant donné les réglages de M1
    Et une carte de trois systèmes en chaîne, la station dans system_1, le gisement de ore_a dans system_2 et celui de ore_b dans system_3

  Scénario: Un vaisseau va de system_1 à system_3 en deux sauts
    Étant donné actor_1 et son vaisseau ship_1 dans system_1
    Quand actor_1 ordonne à ship_1 d'aller dans system_3
    Et 9 ticks passent
    Alors ship_1 n'est pas encore dans system_3
    Et ship_1 est dans system_2
    Et ship_1 est en route
    Quand 1 tick passe
    Alors ship_1 est dans system_3
    Et ship_1 est à l'arrêt
    Et ship_1 a quitté system_1 puis system_2, et est arrivé dans system_2 puis system_3

  Scénario: Un vaisseau mine jusqu'à remplir sa cargaison, puis s'arrête
    Étant donné actor_1 et son vaisseau ship_1 dans system_2
    Quand actor_1 ordonne à ship_1 de miner ore_a
    Et 9 ticks passent
    Alors la cargaison de ship_1 contient 90 unités de ore_a
    Quand 1 tick passe
    Alors la cargaison de ship_1 contient 100 unités de ore_a
    Et ship_1 est à l'arrêt
    Et le gisement de ore_a contient 19900 unités
    Et une fin de minage de ship_1 porte 100 unités

  Scénario: Une vente produit l'écriture de vente et celle de la taxe
    Étant donné actor_1 et son vaisseau ship_1 dans system_1, avec 100 unités de ore_b en cargaison
    Quand actor_1 ordonne à ship_1 de vendre 100 unités de ore_b
    Et 1 tick passe
    Alors le registre contient une écriture de vente de 1500 vers le portefeuille de actor_1
    Et le registre contient une écriture de taxe de 150 depuis le portefeuille de actor_1
    Et le portefeuille de actor_1 vaut 1350
    Et la cargaison de ship_1 contient 0 unités de ore_b

  Scénario: Une taxe qui tombe entre deux unités paie l'unité supérieure
    Étant donné actor_1 et son vaisseau ship_1 dans system_1, avec 3 unités de ore_b en cargaison
    Quand actor_1 ordonne à ship_1 de vendre 3 unités de ore_b
    Et 1 tick passe
    Alors le registre contient une écriture de vente de 45 vers le portefeuille de actor_1
    Et le registre contient une écriture de taxe de 5 depuis le portefeuille de actor_1
    Et le portefeuille de actor_1 vaut 40

  Scénario: Un gisement vidé s'arrête de rendre, puis se régénère
    Étant donné une régénération des gisements tous les 10 ticks, jusqu'à 25 unités
    Et actor_1 et son vaisseau ship_1 dans system_2
    Et le gisement de ore_a contient 25 unités
    Quand actor_1 ordonne à ship_1 de miner ore_a
    Et 3 ticks passent
    Alors la cargaison de ship_1 contient 25 unités de ore_a
    Et le gisement de ore_a contient 0 unités
    Et ship_1 est à l'arrêt
    Quand 6 ticks passent
    Alors le gisement de ore_a contient 0 unités
    Quand 1 tick passe
    Alors le gisement de ore_a contient 25 unités

  Scénario: Deux vaisseaux sur un gisement trop petit sont départagés par tirage à clé
    Étant donné actor_1 et son vaisseau ship_1 dans system_2
    Et actor_2 et son vaisseau ship_2 dans system_2
    Et le gisement de ore_a contient 15 unités
    Quand actor_1 ordonne à ship_1 de miner ore_a
    Et actor_2 ordonne à ship_2 de miner ore_a
    Et 1 tick passe
    Alors le vaisseau au plus petit tirage à clé reçoit 10 unités de ore_a et l'autre 5
    Et le gisement de ore_a contient 0 unités
    Et la même partie rejouée donne les mêmes empreintes

  Scénario: Deux ventes du même vaisseau dans un tick, seule la première est examinée
    Étant donné actor_1 et son vaisseau ship_1 dans system_1, avec 100 unités de ore_b en cargaison
    Quand actor_1 ordonne à ship_1 de vendre 60 unités de ore_b, avec le numéro 1
    Et actor_1 ordonne à ship_1 de vendre 60 unités de ore_b, avec le numéro 2
    Et 1 tick passe
    Alors l'ordre numéro 1 de actor_1 est accepté
    Et l'ordre numéro 2 de actor_1 est refusé avec le code SUPERSEDED
    Et la cargaison de ship_1 contient 40 unités de ore_b

  Scénario: Un ordre sur le vaisseau d'un autre acteur est refusé
    Étant donné actor_1 et son vaisseau ship_1 dans system_2
    Et actor_2 et son vaisseau ship_2 dans system_1
    Quand actor_2 ordonne à ship_1 de miner ore_a, avec le numéro 1
    Et 1 tick passe
    Alors l'ordre numéro 1 de actor_2 est refusé avec le code NOT_OWNER
    Et ship_1 est à l'arrêt

  Scénario: Une vente hors du système de la station est refusée
    Étant donné actor_1 et son vaisseau ship_1 dans system_2, avec 10 unités de ore_a en cargaison
    Quand actor_1 ordonne à ship_1 de vendre 10 unités de ore_a, avec le numéro 1
    Et 1 tick passe
    Alors l'ordre numéro 1 de actor_1 est refusé avec le code NOT_AT_STATION
    Et la cargaison de ship_1 contient 10 unités de ore_a

  Scénario: Un ordre au-delà du budget d'actions est refusé
    Étant donné actor_1 et son vaisseau ship_1 dans system_2
    Et actor_1 n'a plus aucune action
    Quand actor_1 ordonne à ship_1 de miner ore_a, avec le numéro 1
    Et 1 tick passe
    Alors l'ordre numéro 1 de actor_1 est refusé avec le code NO_ACTION_LEFT
    Et ship_1 est à l'arrêt
