# language: fr
# Volet B de M1 : le serveur, le client et le PNJ (docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 20).
# Les scénarios passent par le serveur en mémoire, en mode sans horloge, et par le protocole, sans le client Textual.
# Avec la graine 1, la station est dans system_1, le gisement de ore_a dans system_2 et celui de ore_b dans system_3.

Fonctionnalité: Une partie jouée à travers le serveur en mémoire

  Contexte:
    Étant donné une partie du serveur en mémoire, graine 1, avec les réglages de M1, sans horloge

  Scénario: Le propriétaire extrait ore_b, le ramène à la station et le vend
    Étant donné le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Alors la dernière mise à jour du propriétaire montre son vaisseau dans system_1
    Quand le propriétaire envoie son vaisseau vers system_3
    Et le serveur joue 5 ticks
    Alors la dernière mise à jour du propriétaire montre son vaisseau dans system_2, en route
    Quand le serveur joue 5 ticks
    Alors la dernière mise à jour du propriétaire montre son vaisseau dans system_3
    Quand le propriétaire ordonne à son vaisseau de miner ore_b
    Et le serveur joue 10 ticks
    Alors la dernière mise à jour du propriétaire montre 100 unités de ore_b en cargaison
    Quand le propriétaire envoie son vaisseau vers system_1
    Et le serveur joue 10 ticks
    Alors la dernière mise à jour du propriétaire montre son vaisseau dans system_1
    Quand le propriétaire ordonne à son vaisseau de vendre 100 unités de ore_b
    Et le serveur joue 1 tick
    Alors la dernière mise à jour du propriétaire montre une vente de 100 unités de ore_b, payée 1500 et taxée 150
    Et la dernière mise à jour du propriétaire montre un portefeuille de 1350
    Et aucune mise à jour de l'autre acteur ne montre la vente du propriétaire
    Et le journal des événements contient une écriture de vente de 1500 et une écriture de taxe de 150

  Scénario: Un ordre au nom d'un autre acteur est refusé par la réception
    Étant donné le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Et le propriétaire soumet, au nom de l'autre acteur, l'ordre de miner ore_a
    Et le serveur joue 1 tick
    Alors la dernière mise à jour du propriétaire montre son ordre refusé avec le code ACTOR_MISMATCH

  Scénario: Un ordre d'administration soumis par un client est refusé par la réception
    Étant donné le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Et le propriétaire soumet, en son propre nom, un ordre d'administration d'aller dans system_2
    Et le serveur joue 1 tick
    Alors la dernière mise à jour du propriétaire montre son ordre refusé avec le code FORBIDDEN_CATEGORY
    Et la dernière mise à jour du propriétaire montre son vaisseau dans system_1, à l'arrêt

  Scénario: Au-delà du quota d'ordres d'un tick, les plus petits numéros sont gardés
    Étant donné le propriétaire et un autre acteur, chacun avec son vaisseau
    Quand le serveur joue 1 tick
    Et le propriétaire soumet dans le même tick 7 ordres d'aller dans system_2, numérotés de 1 à 7
    Et le serveur joue 1 tick
    Alors les ordres 6 et 7 du propriétaire sont refusés avec le code QUOTA_EXCEEDED
    Et aucun des ordres 1 à 5 du propriétaire n'est refusé avec le code QUOTA_EXCEEDED

  Scénario: Le PNJ vend au moins une cargaison en 100 ticks
    Étant donné un PNJ joué par l'hôte des PNJ avec la politique scripted_miner
    Quand le serveur joue 100 ticks
    Alors le journal des événements contient au moins une vente du PNJ
