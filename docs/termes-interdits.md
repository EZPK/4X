# Termes interdits

Vocabulaire d'EVE Online à ne pas reprendre ([§10 du niveau 1](designs/architecture-niveau-1.md#10-les-garde-fous-sur-le-code-écrit-par-lia)). Liste à compléter par le propriétaire.

Seuls les termes de cette liste sont interdits, dans tout le dépôt, les messages de commit, les noms de branche et les pull requests. En cas de doute sur un autre terme, demander au propriétaire.

Format : les termes sont les lignes non vides comprises entre le titre « ## Termes » et le titre suivant, un par ligne, sans puce. Les fichiers exclus sont les lignes non vides sous le titre « ## Fichiers exclus », un motif par ligne, dans la syntaxe de `.github/chemins-proteges.txt`. La recherche ne tient pas compte de la casse et se fait par mots entiers : un terme n'est trouvé que s'il n'est ni précédé ni suivi d'une lettre (accents compris), d'un chiffre ou d'un souligné. Le tiret fait partie du terme. Une pull request qui ne modifie que ce fichier est dispensée de la vérification de sa description et de ses messages de commit.

## Termes

ISK
CONCORD
null-sec

## Fichiers exclus

docs/termes-interdits.md
docs/designs/mmo-gestion-spatiale-ia.md
docs/revues/**
docs/designs/architecture-niveau-1.md
docs/designs/niveau-2-m0-garde-fous.md
