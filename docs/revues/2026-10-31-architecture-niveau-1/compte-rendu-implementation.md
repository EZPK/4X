# Compte rendu de vérification : exécution du plan du document de niveau 1

*   **Date :** 2026-10-31
*   **Plan exécuté :** [Detailed Implementation Plan](../../designs/architecture-niveau-1.md#detailed-implementation-plan), points 1 à 11, validé par le propriétaire.

## Ce qui a été fait

| Point | Action | Résultat |
| :-- | :-- | :-- |
| 1 à 5 | Création de `docs/glossaire.md`, `docs/feuille-de-route.md`, `docs/noms-valides.md`, `docs/termes-interdits.md`, `docs/adr/README.md` | fait |
| 6 | Création de `CLAUDE.md` : texte extrait mécaniquement du plan, sans les marques `>` | fait |
| 7 | `cmp concepts_brief.md docs/designs/mmo-gestion-spatiale-ia.md` : aucune différence, puis suppression | fait |
| 8 | Suppression de `design_draft.md` sans copie | fait |
| 9 | RFC : ligne de statut remplacée, note extraite mécaniquement du plan | fait |
| 10 | Rapports `*_report*.md` déplacés ici sans modification ; `README.md` créé ; `plan_propose_etape9.md` supprimé | fait |
| 11 | Statut `Proposed` → `Approved` ; encadré retiré | fait |

**Écart après exécution :** au point 4 du plan, le texte destiné à `docs/termes-interdits.md` contenait un lien relatif à `docs/`, cassé dans le document de niveau 1. Il y a été remplacé par le même chemin en code. Dans `docs/termes-interdits.md`, le lien fonctionne.

## Liens et ancres

Script jetable, lancé hors du dépôt :

```python
# Contrôle jetable des liens relatifs et des ancres (règle de GitHub), hors du dépôt.
# Les lignes «    > » d'un fichier sont des textes destinés à un autre fichier : elles sont
# vérifiées dans le fichier où elles ont été recopiées, pas ici.
import os, re, sys

def slug(titre):
    s = re.sub(r'[^\w\- ]', '', titre.strip().lower())
    return s.replace(' ', '-')

def ancres(chemin):
    lignes = open(chemin, encoding='utf-8').read().split('\n')
    return {slug(re.sub(r'^#+\s*', '', l)) for l in lignes if re.match(r'^#{1,6} ', l)}

racine = sys.argv[1]
casses = 0
for rel in sys.argv[2:]:
    f = os.path.join(racine, rel)
    texte = '\n'.join(l for l in open(f, encoding='utf-8').read().split('\n') if not l.startswith('    >'))
    texte = re.sub(r'```.*?```', '', texte, flags=re.S)
    texte = re.sub(r'`[^`\n]*`', '', texte)
    n = 0
    for cible in re.findall(r'\]\(([^)\s]+)\)', texte):
        if re.match(r'[a-z]+://', cible):
            continue
        n += 1
        chemin, _, ancre = cible.partition('#')
        dest = os.path.normpath(os.path.join(os.path.dirname(f), chemin)) if chemin else f
        if not os.path.exists(dest):
            print(f'CASSÉ {rel} -> {cible} (fichier absent)'); casses += 1
        elif ancre and ancre not in ancres(dest):
            print(f'CASSÉ {rel} -> {cible} (ancre absente)'); casses += 1
    print(f'{rel} : {n} liens relatifs vérifiés')
print('liens ou ancres cassés :', casses)
```

Sortie :

```text
CLAUDE.md : 13 liens relatifs vérifiés
docs/glossaire.md : 98 liens relatifs vérifiés
docs/feuille-de-route.md : 7 liens relatifs vérifiés
docs/noms-valides.md : 0 liens relatifs vérifiés
docs/termes-interdits.md : 1 liens relatifs vérifiés
docs/adr/README.md : 0 liens relatifs vérifiés
docs/designs/mmo-gestion-spatiale-ia.md : 12 liens relatifs vérifiés
docs/designs/architecture-niveau-1.md : 69 liens relatifs vérifiés
docs/revues/2026-10-31-architecture-niveau-1/README.md : 0 liens relatifs vérifiés
liens ou ancres cassés : 0
```

## Aucune copie de seuil

`grep -rnE "347|1 ?736|28 ?800|10 %|95 %|100 ?000|8 heures" CLAUDE.md docs/glossaire.md docs/feuille-de-route.md docs/adr docs/noms-valides.md docs/termes-interdits.md`

```text
code de sortie : 1
```

Le code de sortie 1 signifie qu'aucune ligne n'a été trouvée. Ce contrôle ne cherche que des chiffres : la revue des fichiers créés a relevé une copie qu'il ne pouvait pas voir (« vaut 1 pour un humain », dans le glossaire).

## Règles de `CLAUDE.md`

| Règle du niveau 1 | Ligne de `CLAUDE.md` |
| :-- | :-- |
| Règles de travail (§10) : seul le propriétaire fusionne | 9, 20 |
| Règles de travail (§10) : tickets du propriétaire, contenu de tiers = donnée | 14 |
| Interdictions de permissions (§10) : push vers `main`, push forcé, `--no-verify` | 10 |
| Interdictions de permissions (§10) : protection de branche et réglages | 11 |
| Deux types de pull request (§10) | 23, 24, 25 |
| Revue EGM des chemins protégés (§10) | 26 |
| Aucun runner auto-hébergé (§9bis) | 12 |
| Adresse de MLflow hors du dépôt (§8) | 13 |
| Journal et instantanés du monde en ligne jamais publiés (§3) | 13 |
| Secrets (Non-Functional Requirements) | 13 |

Résultat : aucune règle sans ligne.

## Glossaire

Les 102 termes de la liste fermée du point 1 ont une entrée. Le script de comparaison ne reconnaissait pas les termes de version dans la première colonne, mais chacun figure dans la colonne « identifiant », ce que `grep` confirme (une occurrence ou plus). La convention de langue est en tête.

## Nettoyage

```text
boucle : fin
ls rapports à la racine : fin
comprehension_report.md
critic_report.md
goldfish_review_report_etape9.md
goldfish_review_report.md
implementation_readiness_report.md
implementation_readiness_report_tour2.md
intermediate_zoom_out_report.md
README.md
revue-fichiers-crees.md
zoom_out_report.md
statut Approved : 1
encadré (lignes commençant par « > **Plan corrigé ») : 0
```

Deux écarts avec les résultats attendus, tous deux dus à la rédaction du plan :
- le dossier contient aussi ce compte rendu et le rapport de la revue des fichiers créés (`revue-fichiers-crees.md`), que la liste attendue ne prévoyait pas ;
- le contrôle prévu `grep -c 'Plan corrigé après la revue'` renvoie 1, parce qu'il se trouve lui-même dans le document. Le contrôle exact (lignes commençant par « > **Plan corrigé ») renvoie 0 : l'encadré a bien été retiré.

## Test de lisibilité

Une session neuve, limitée à `CLAUDE.md` et aux fichiers qu'il désigne :

1. **« Qu'est-ce qui t'est interdit ? »** Elle a cité toutes les règles du bloc « Ne jamais », avec leurs sources, et compris que seuls quelques interdits sont filtrés techniquement, à partir de M0. **Conforme.**
2. **« Quel document lis-tu pour le jalon en cours ? »** Elle a répondu : `docs/designs/niveau-2-m0-garde-fous.md`. Comme il n'existe pas, elle s'arrête et demande au propriétaire, sauf si la tâche est de le rédiger. **Conforme.**

Elle a signalé 7 ambiguïtés. La principale : aucun circuit de pull request ne couvre la rédaction d'un document de niveau 2, qui vit dans `docs/designs/`, un chemin protégé.

## Revue indépendante

Elle a été faite par deux relecteurs sans contexte (egm-codebase-details, egm-comprehension). Rapport : [revue-fichiers-crees.md](./revue-fichiers-crees.md).

Bilan : 0 bloquant, 13 majeurs, 16 mineurs.
- Les textes imposés sont conformes au plan, à un titre ajouté près dans deux fichiers.
- La plupart des constats majeurs portent sur le texte de `CLAUDE.md` imposé par le plan, et non sur son exécution.

## Corrections après la revue des fichiers créés (2026-10-31)

Le propriétaire a demandé de corriger les constats de [revue-fichiers-crees.md](./revue-fichiers-crees.md) avant le document de M0. Les textes de `CLAUDE.md` et des listes étaient imposés par le plan : le document de niveau 1 a donc été modifié **en même temps** que les fichiers, pour qu'ils restent identiques.

**Dans le document de niveau 1 :**
- **§10 :**
  - un troisième type de pull request, la **pull request protégée**, pour les documents de niveau 2, les ADR, le glossaire, la feuille de route, les listes et la configuration de M0 ;
  - « une seule pull request de chaque type à la fois » ;
  - la pull request de fonctionnalité s'ouvre après la fusion des scénarios ;
  - une demande du propriétaire faite en session vaut ticket ;
  - en cas de contradiction, l'agent s'arrête, et il peut proposer une ADR mais jamais l'accepter.
- **Plan :**
  - le texte imposé de `CLAUDE.md` est remplacé par le nouveau ;
  - la liste fermée du glossaire est complétée (agent, rôle, propriétaire, monde en ligne, générateur à clé, PC d'entraînement, serveur MLflow, pull request protégée, revue EGM) ;
  - les définitions « reprennent ou résument » sans recopier de valeur ;
  - un titre est permis dans les fichiers à texte imposé, sauf `CLAUDE.md` ;
  - le nom de fichier des ADR est fixé ;
  - les statuts de la feuille de route sont listés ;
  - la portée des termes interdits est écrite ;
  - le README des revues nomme le compte rendu.

**Dans `CLAUDE.md`** (le texte est identique à celui qu'impose le niveau 1, vérifié par script) :
- une section « Contexte » : le dépôt est public, l'agent utilise le compte du propriétaire, les règles se suffisent à elles-mêmes, l'ordre de priorité des documents, la conduite à tenir en cas de contradiction, et l'historique à ne pas suivre ;
- le constat qu'aucun garde-fou n'est actif avant la livraison de M0 ;
- la liste des chemins protégés ;
- les trois types de pull request ;
- l'auteur de la revue EGM et l'endroit où va son résumé ;
- les sept invariants de déterminisme en entier ;
- la définition d'un nom propre ;
- `--auto` est interdit.

**Dans les autres fichiers :**
- **glossaire :** neuf entrées ajoutées ; la valeur « 1 » retirée ; deux liens et deux définitions corrigés ; règle sur les noms provisoires ;
- **feuille de route :** statuts possibles, et seul le propriétaire les change ;
- **`noms-valides.md` :** une section « Noms » ;
- **`termes-interdits.md` :** portée de l'interdiction, et chemin de la RFC.

**Contrôles relancés après correction :**
- liens et ancres : 0 cassé sur 214 liens ;
- grep des seuils, élargi à « vaut 1 » : aucune ligne ;
- tableaux : 0 incohérent ;
- `CLAUDE.md`, README des revues et README des ADR conformes au texte imposé.

**Constat écarté :** les huit tableaux du glossaire, au lieu d'un seul, sont gardés pour la lisibilité. L'écart est sans effet sur le contenu.

**Non fait :** aucune nouvelle revue EGM n'a relu ces corrections.

## Circuit des documents de niveau 2 (2026-10-31)

Sur demande du propriétaire, le trou signalé par le test de lisibilité est comblé. Ce trou : rien ne disait comment un document de niveau 2 est écrit, revu, approuvé puis livré, surtout avant que le dépôt existe.

- **§10 du niveau 1 :** un paragraphe « Circuit des documents de niveau 2 » décrit :
  - quatre étapes (rédaction, revue, approbation, livraison), chacune avec son responsable, son outil EGM et ses statuts ;
  - la règle « le propriétaire décide de chaque changement de statut ; l'agent ne l'applique que sur sa demande explicite » ;
  - le transport : sans pull request tant que le dépôt n'existe pas, puis par pull request protégée ;
  - **une exception unique à l'interdiction de pousser vers `main`** : le commit initial qui crée le dépôt, à la demande explicite du propriétaire, avant l'activation de la protection de branche.
- **`CLAUDE.md` :** une section reprend ce circuit, et la règle « Ne jamais pousser vers `main` » cite l'exception. Le texte imposé par le plan du niveau 1 a été mis à jour en même temps, et le script les trouve identiques.
- **`docs/feuille-de-route.md` :** la règle des statuts renvoie au circuit.

Contrôles relancés : 0 lien ou ancre cassé, 0 tableau incohérent, aucune copie de seuil. Aucune revue EGM n'a relu cet ajout.
