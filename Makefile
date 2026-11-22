# Commandes courantes du projet 4X. `make` seul affiche l'aide.
#
# « Version stable » : le dernier état de la branche main sur GitHub. Rien n'y entre sans
# contrôles CI verts et sans la fusion du propriétaire. Elle est jouée depuis un dossier de
# travail à part (.worktrees/stable, à la racine du dépôt), remis à jour à chaque lancement :
# la branche sur laquelle on travaille n'est jamais touchée.
#
# Options : GRAINE=42 (graine du monde), DEV=1 (mode développement : pause, accélération).
# Exemple : make jouer GRAINE=1 DEV=1

GRAINE ?=
DEV ?=
OPTIONS := $(if $(GRAINE),--graine $(GRAINE)) $(if $(DEV),--dev)

RACINE := $(shell dirname "$$(git rev-parse --path-format=absolute --git-common-dir)")
STABLE := $(RACINE)/.worktrees/stable

.DEFAULT_GOAL := aide
.PHONY: aide jouer stable jouer-ici tests

aide:
	@echo "make jouer      lance la dernière version stable du jeu (main sur GitHub)"
	@echo "make jouer-ici  lance la version du dossier courant (la branche en cours)"
	@echo "make stable     met seulement à jour la version stable, sans la lancer"
	@echo "make tests      lance les tests rapides"
	@echo ""
	@echo "Options : GRAINE=42 (graine du monde), DEV=1 (mode développement)."
	@echo "Le terminal doit faire au moins 120 colonnes × 36 lignes."

stable:
	@git fetch --quiet origin main
	@if [ -d "$(STABLE)" ]; then \
		git -C "$(STABLE)" checkout --quiet --detach origin/main; \
	else \
		git worktree add --quiet --detach "$(STABLE)" origin/main; \
	fi
	@echo "Version stable : $$(git -C "$(STABLE)" log -1 --format='%h, %cs : %s')"

jouer: stable
	cd "$(STABLE)" && uv run --locked python -m fourx $(OPTIONS)

jouer-ici:
	uv run --locked python -m fourx $(OPTIONS)

tests:
	uv run --locked pytest -q -m "not rejeu and not lent and not mesure"
