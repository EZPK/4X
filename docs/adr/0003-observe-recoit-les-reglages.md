# ADR 0003 — `observe` reçoit les réglages

- **Numéro :** 0003
- **Titre :** `observe` reçoit les réglages
- **Statut :** acceptée
- **Date :** 2026-11-12
- **Décideur :** le propriétaire
- **Contexte :** l'amendement 1 du niveau 2 de M1 fait du temps une ressource : un saut dure `jump_ticks` = 400 ticks, et remplir une cargaison vide prend `cargo_capacity` ÷ `mining_rate` = 100 ticks. Le joueur doit voir ces durées : coût d'un déplacement avant de le confirmer, ticks restants d'un trajet ou d'un minage. Or ces valeurs sont des réglages, pas des champs de l'état. Le niveau 1, §5, dit que `observe(état, acteur)` ne renvoie que les champs visibles de l'état, et qu'« il n'y a pas d'autre canal vers le joueur ». Le client ne peut donc pas les connaître aujourd'hui, et les joueurs IA non plus.
- **Options :**
  - **(a)** `observe(état, acteur, réglages)` : l'observation reçoit une vue des réglages publics, recopiée de `Tunables`. L'état, `step`, les empreintes et l'instantané ne changent pas. La signature du niveau 1 change ;
  - **(b)** copier ces valeurs sur les entités de l'état à leur création : la vitesse et le laser sur le vaisseau, la taxe sur la station. `observe` et le niveau 1 ne changent pas, et cela prépare des valeurs propres à chaque vaisseau. Mais `State`, `step`, les empreintes et l'instantané changent, et un rééquilibrage des réglages ne toucherait pas les vaisseaux déjà créés ;
  - **(c)** un champ dans `TickUpdate`, hors de l'observation, et une modification de la règle « pas d'autre canal ». Rien ne change dans l'état ni dans `observe`. Mais les joueurs IA, qui s'entraînent sur l'observation seule, n'y auraient pas accès.
- **Décision :** l'option (a). `observe(state, actor_id, tunables)` ajoute à l'observation `public_tunables`, une vue de deux réglages publics nommés un à un : `jump_ticks` et `mining_rate`. Les autres réglages restent invisibles : la capacité de cargaison est déjà dans la vue du vaisseau, et le paiement et la taxe d'une vente dans l'événement de vente. `Tunables` ne porte pas de classe de visibilité : ce n'est pas un champ de l'état. La règle « pas d'autre canal » reste inchangée : l'observation reste le seul canal. `protocol_version` passe à 2.
- **Conséquences :**
  - le niveau 1, §5, écrit `observe(état, acteur, réglages)`, et dit que l'observation contient, en plus de l'état visible et des événements visibles, les réglages publics ;
  - le glossaire met à jour la fonction `observe` et ajoute « réglages publics » ;
  - le serveur passe ses réglages à `observe` ; les tests de visibilité vérifient qu'aucun réglage hors de la liste n'apparaît dans l'observation ;
  - la liste des réglages publics est fermée : en ajouter un passe par une modification du niveau 2 du jalon concerné.
- **Condition de révision :** une durée devient propre à un vaisseau, à un lien ou à une station (laser, vitesse, distance) : la valeur passe alors dans la vue de l'entité, et sort de la vue des réglages publics.
- **Section du niveau 1 modifiée :** §5 (acteurs, égalité d'accès et visibilité), la puce sur les classes de visibilité et `observe`.
