# language: fr
# Volet C de M1 (docs/designs/niveau-2-m1-noyau.md, plan détaillé, point 24 ; Technical Plan, points 8
# et 13 ; CUJ 4 du niveau 1). Les parties passent par le serveur en mémoire, en mode sans horloge, sur
# les réglages de tunables.toml : les outils en ligne de commande lisent ces réglages.

Fonctionnalité: Le rejeu d'une partie et l'outil de divergence

  Scénario: Une partie jouée à travers le serveur se rejoue avec les mêmes empreintes à chaque tick, refus compris
    Étant donné une partie du serveur en mémoire sur les réglages de tunables.toml, graine 1, sans horloge
    Et le propriétaire et un autre acteur, chacun avec son vaisseau
    Et un PNJ joué par l'hôte des PNJ avec la politique scripted_miner
    Quand le serveur joue 1 tick
    Et le propriétaire soumet, au nom de l'autre acteur, l'ordre de miner ore_a
    Et le propriétaire envoie son vaisseau vers le système où il se trouve
    Et le serveur joue 1 tick
    Et le propriétaire envoie son vaisseau vers un système voisin
    Et le serveur joue 1000 ticks
    Alors le journal des ordres de la partie contient un ordre refusé par la réception avec le code ACTOR_MISMATCH
    Et le journal des événements contient un ordre refusé avec le code ALREADY_THERE
    Quand on rejoue la partie par replay_orders depuis son instantané initial et son journal des ordres
    Alors le rejeu donne les empreintes du journal des ordres à chaque tick, du tick 1 au dernier tick joué
    Et le rejeu donne les événements du journal des événements, dans le même ordre
    Et l'outil de rejeu, lancé sur le dossier de la partie, finit avec le code 0

  Scénario: L'outil de divergence signale au tick 50, composant ledger, une partie dont le registre est modifié au tick 50
    Étant donné une partie du serveur en mémoire sur les réglages de tunables.toml, graine 1, sans horloge
    Et un PNJ joué par l'hôte des PNJ avec la politique scripted_miner
    Quand le serveur joue 100 ticks
    Et on rejoue la partie par step depuis son instantané initial et son journal des ordres, en modifiant son registre au tick 50
    Et on lance l'outil de divergence sur le dossier de la partie et le fichier d'empreintes de ce rejeu
    Alors l'outil de divergence affiche « tick 50 : ledger » et finit avec le code 1
    Et first_divergence, sur les empreintes du journal des ordres et celles de ce rejeu, renvoie le tick 50 et le seul composant ledger
    Quand on rejoue la partie par step depuis son instantané initial et son journal des ordres, sans modification
    Et l'outil de rejeu, lancé sur le dossier de la partie, exporte ses empreintes dans un fichier
    Et on lance l'outil de divergence sur le fichier exporté par l'outil de rejeu et le fichier d'empreintes de ce rejeu
    Alors l'outil de divergence affiche « aucune divergence » et finit avec le code 0
    Et first_divergence, sur les empreintes du journal des ordres et celles de ce rejeu, ne renvoie rien
