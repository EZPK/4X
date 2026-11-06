# ADR 0002 — Règles `deny` et worktrees liés

- **Numéro :** 0002
- **Titre :** Règles `deny` et worktrees liés
- **Statut :** acceptée
- **Date :** 2026-11-06
- **Décideur :** le propriétaire
- **Contexte :** le §10 du niveau 1 interdit à l'agent de code d'éditer `.claude/` et `.git/hooks/`, par des règles `deny` placées dans `.claude/settings.json` (`Edit(/.claude/**)`, `Edit(/.git/hooks/**)`). Le `/` initial désigne la racine du projet de la session. Le propriétaire travaille aussi dans des worktrees liés (`git worktree add`). Dans un worktree lié :
  - `.git` est un fichier : la règle sur `/.git/hooks/**` ne vise aucun dossier réel. Les hooks que git exécute sont dans le sous-dossier `hooks/` du dossier git commun (`git rev-parse --git-common-dir`), c'est-à-dire dans le dépôt principal ;
  - la règle sur `/.claude/**` ne couvre que le `.claude/` du dossier de la session, pas celui des autres dossiers de travail, où vivent le hook Claude Code et les réglages d'une autre session.

  Ce trou existait depuis M0, mais restait sans effet tant que le hook Claude Code refusait tout commit lancé depuis un worktree lié. La pull request #9 a corrigé ce refus : le hook cherche maintenant le hook pre-commit dans le dossier git commun. Un agent de code qui y placerait un faux hook ferait accepter un commit sans `gitleaks`. La revue EGM de la pull request #9 l'a relevé.
- **Options :**
  - **(a)** des règles `deny` sur les chemins absolus, dans les réglages utilisateur du propriétaire (`~/.claude/settings.json`), hors du dépôt : le dossier des hooks du dossier git commun, le `.claude/` du dépôt principal, et le `.claude/` de chaque worktree. Elles valent pour toutes les sessions de la machine. Elles ne sont pas dans le dépôt, donc aucun contrôle ne vérifie leur présence, et il faut les poser sur chaque machine ;
  - **(b)** les mêmes règles dans le `.claude/settings.json` du dépôt : le chemin personnel du propriétaire deviendrait public, et une règle relative (`Edit(/.worktrees/**/.claude/**)`) ne couvrirait que les sessions lancées depuis le dépôt principal ;
  - **(c)** ne rien ajouter, et documenter la limite seulement.
- **Décision :** l'option (a), avec trois règles (en Claude Code, un chemin absolu s'écrit avec `//`) :
  - `Edit(//<dépôt principal>/.git/hooks/**)` ;
  - `Edit(//<dépôt principal>/.claude/**)` ;
  - `Edit(//<dépôt principal>/.worktrees/**/.claude/**)`.
- **Conséquences :**
  - `CLAUDE.md`, sa copie dans le niveau 1 et le §10 décrivent la limite et les règles utilisateur ;
  - l'agent de code n'édite ni le dossier des hooks du dossier git commun, ni le `.claude/` d'aucun dossier de travail, même là où aucune règle ne l'en empêche ;
  - le niveau 2 de M0 décrit le dossier où le hook Claude Code cherche désormais le hook pre-commit.
- **Condition de révision :** les worktrees ne sont plus rangés sous `.worktrees/` ; ou Claude Code permet d'ancrer une règle du projet sur le dossier git commun ; ou le projet est travaillé sur une autre machine.
- **Section du niveau 1 modifiée :** §10 (interdictions dans les permissions de Claude Code) et la copie de `CLAUDE.md` du Detailed Implementation Plan, phase 2.
