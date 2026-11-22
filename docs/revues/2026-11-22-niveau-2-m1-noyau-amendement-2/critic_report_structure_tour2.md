# Étape 7, tour 2 — Structure (amendement 2)

**Cible :** `docs/designs/niveau-2-m1-noyau.md`, passages de l'amendement 2. Pièce liée : `docs/adr/0006-client-retro-8-bits.md`.
**Référentiels lus :** le persona structurel EGM ; le standard `feature-spec-standard.md` d'EGM ; l'en-tête « Amendements » du document (l. 23 à 49) ; `docs/adr/README.md` ; l'ADR 0005 ; le niveau 1 (Overview l. 16, alternative N l. 600 à 604, §11 l. 498) ; les rapports du tour 1 `critic_report_structure.md` et `goldfish_review_report.md`.
**Limites :** je n'avais pas accès à git. Je n'ai donc pu vérifier ni les numéros de pull requests « n° 23 à 27 » (l. 44), ni le texte remplacé par les marques « réécrit ».

**Verdict : aucun bloquant, 3 majeurs, 14 détails.** Les 9 constats majeurs du tour 1 sont corrigés. La numérotation 23 septies à 23 undecies et tous ses renvois sont justes. La liste « Passages touchés » de la ligne 2 est exacte. Les défauts restants sont de deux sortes :
- des passages non marqués que l'amendement 2 contredit (point 13, critère de sortie) ;
- un renvoi à des libellés, « E1 à E4 », que le document ne définit pas.

## 1. Suivi des majeurs du tour 1

| Constat du tour 1 | État | Où |
| :-- | :-- | :-- |
| M1. Règle du minimum (point 1) | Corrigé : « objectifs 12 à 19 », « ADR 0003 à 0006 », marque « réécrit », précision datée du 2026-11-22. La précision renvoie toutefois aux « réponses E1 à E4 », un libellé que le document ne définit pas (voir N1). | l. 279, 300 |
| M2. Point 28 bis sans mesure du rendu | Corrigé : puce « amendement 2, ajout » avec palier, graine, taille, durée et seuils. Les renvois des l. 631 et 1232 visent bien cette puce. | l. 1713 |
| M3. Verification Plan | Corrigé : bloc « (amendement 2) ». Les lignes « Mutation » et « Carte » de l'amendement 1 portent une marque de remplacement. | l. 1811, 1813, 1817 à 1824 |
| M4. Objectif 12, *Vérification* | Corrigé sur le fond : la carte n'est plus lue comme du texte, chaque information a son cadre. La portée de la marque reste discutable (voir D2). | l. 169 |
| M5. Règles d'intégration du volet B ter | Corrigé : « **Règles d'intégration (amendement 2).** » | l. 1601 |
| M6. Puce « Code livré » | Corrigé : livraison des points 23 bis à 23 sexies, terme « code de l'amendement 1 » défini. Le type de la marque est discutable (voir D1). | l. 44 |
| M7. Textes de l'amendement 1 devenus faux | Corrigé : phrase de remplacement du point 2 de l'Overview (l. 94), Non-Goals (l. 204, 205), risque « Carte illisible » qui renvoie au nouveau risque (l. 1220). | l. 94, 204, 205, 1220 |
| M8. Alertes et barres | Corrigé : tableau des cadres avec `#barre`, `#touches` et l'alerte dans `#etape` ; l. 540 et 954 alignées. | l. 596 à 606, 540, 954 |
| M9. « Journal » | Corrigé : le cadre s'appelle « Historique » partout. | l. 603, 656, 169 |

Détails du tour 1 : D1 à D9, D11 et D12 sont corrigés (l. 25 et 963 ; ligne « 2 (amendement 2) » ; en-tête et volet B ter dans la liste ; l. 536 ; l. 1622 ; Create, Modify et Delete ; « chemins protégés » à la l. 1616 ; verdict dans les *Vérification* 17 à 19 ; l. 128 ; l. 225, 1243, 1254 et 1255 ; ADR, « niveau 1, alternative N », « l'option (b) »). Deux restent ouverts :
- D10, l. 235 : le *Given* du CUJ A (voir D5) ;
- D12, l. 1136 et 1137 : deux lignes vides de suite avant l'alternative AB (voir D10).

## 2. Ce qui est conforme

- **Numéros.** Objectifs 17 à 19 ; point 7 ter ; alternatives AB à AG ; points 23 septies, octies, nonies, decies et undecies ; volet B ter. Rien n'est renuméroté.
- **Renvois au plan détaillé :**
  - « 23 decies » vise toujours la pull request de la carte : l. 1555, 1623, 1627, 1648, 1713 et 1821. Le renvoi de remplacement de la l. 1555 est juste, puisque le point 23 decies modifie `tests/proprietes/test_proprietes.py` (l. 1644).
  - « 23 undecies » vise toujours la partie d'essai : l. 44, 169 (deux fois), 179, 181, 183, 279, 1601 et 1824.
  - « 23 septies », « octies » et « nonies » sont justes : l. 1603, 1616, 1627 et 1638.
- **Marques.**
  - En titre : 7 ter, AB à AG, 23 septies à 23 undecies.
  - Seules sur leur ligne : l. 92, 126, 1817.
  - En tête de puce ou d'objectif : l. 178, 180, 182, 204 à 206, 1220, 1243, 1254, 1255.
  - Lignes de code marquées : l. 940 à 950 et 954.
  - Tableau « Risques ajoutés par l'amendement 2 » : l. 1225.
  - Marques de remplacement : l. 1555, 1811, 1813.
- **Liste « Passages touchés » (l. 49).** J'ai relevé toutes les occurrences de « amendement 2 ». Chaque passage marqué est cité, et chaque passage cité porte une marque : en-tête ; Overview ; The Problem ; objectifs 11, 12 et 17 à 19 ; Non-Goals ; Open Questions ; vue d'ensemble ; points 1, 7 bis, 7 ter, 12 et 13 ; introduction des alternatives ; AB à AG ; Risks ; Additional Resources ; Future Improvements ; points 23 quater, B ter et 28 bis ; Verification Plan. Il n'y a rien en trop ni en moins, sauf les passages non marqués relevés plus bas.
- **Gabarit.** Pour l'amendement, Problem (l. 128), Goals (17 à 19), Non-Goals, Open Questions (l. 225), Architecture (7 ter), Alternatives (AB à AG, avec « Retenu »), Risks, Additional Resources et Future Improvements sont présents. La hiérarchie des titres est sans saut : `####` sous `### Palier 3`, `###` sous `##`.
- **ADR 0006.** Ses onze puces suivent le modèle de `docs/adr/README.md`, dans l'ordre. Le titre est identique à celui de l'index (README, l. 28) et le statut « proposée » concorde. La puce « Section du niveau 1 modifiée » correspond au niveau 1, l. 16, qui est déjà modifié avec un lien vers l'ADR.

## 3. Constats

### Majeurs

**N1. l. 128, 225 et 279 : les « réponses E1 à E4 » renvoient à un libellé défini hors du document, qui entre en collision avec un libellé interne.**
- **Problème :**
  - Le document cite « réponses E1 à E4 du dossier de revue » (l. 128), « les quatre décisions posées pendant sa revue (E1 à E4) » (l. 225) et « réponses E1 à E4 de la revue » (l. 279). Il ne dit nulle part ce que sont E1, E2, E3 et E4 : seul `goldfish_review_report.md` les définit.
  - Le Verification Plan emploie déjà « les essais E1 à E5 (point 32 bis) » (l. 1800) : le même libellé désigne deux choses différentes.
  - La règle des Open Questions (l. 219) veut qu'une question tranchée « rejoigne le Technical Plan ». L'amendement 1 avait mis ses décisions en lignes datées dans le tableau du point 1 (l. 309 à 316). L'amendement 2 n'y ajoute aucune ligne, alors que la l. 279 dit que ces décisions « priment ».
- **Proposition :**
  - Ajouter au tableau du point 1 quatre lignes « (amendement 2) » datées du 2026-11-22 : carte fixe (alternative AF) ; souris sans mini-carte ; deux pull requests de fonctionnalité ; verdict non bloquant et volet C en parallèle (point 23 undecies, l. 1601).
  - Aux l. 128, 225 et 279, remplacer « E1 à E4 » par « les décisions du 2026-11-22 du tableau du point 1 ».

**N2. l. 1804, Verification Plan, « Critère de sortie » : texte non marqué que contredit le verdict non bloquant.**
- **Problème :** « chaque objectif de ce document correspond[ent] à une preuve du compte rendu ». Or le point 23 undecies (l. 1649), le point 1 (l. 279) et l'ADR 0006 (l. 21) permettent de livrer M1 même si le verdict sur les objectifs 12 et 17 à 19 est défavorable. Un lecteur peut prendre le critère de sortie pour une exigence de verdict favorable, ce qui contredirait la décision du propriétaire. La phrase est dans une section que l'amendement 2 touche déjà.
- **Proposition :** ajouter dans le bloc « (amendement 2) » du Verification Plan : « **Critère de sortie :** pour les objectifs 12 et 17 à 19, la preuve est le verdict consigné, favorable ou non (point 23 undecies) ; le critère de sortie du niveau 1, §11, ne change pas. »

**N3. l. 936 et 937, Technical Plan, point 13 : ancienne signature de l'historique non marquée, contredite deux lignes plus bas dans le même bloc.**
- **Problème :** le bloc garde `history: tuple[str, ...]` (l. 936), avec ses exemples de chaînes. La l. 950 « (amendement 2) » donne `ClientModel.history -> tuple[HistoryEntry, ...]`. Selon la légende (l. 35), une ligne de code marquée est « ajoutée ou récrite ». Ici, la ligne d'origine n'est ni récrite ni marquée comme remplacée, et le point 13 « fige ces noms » (l. 768). Un agent de code y lit deux types contraires pour le même champ. La préséance tranche, mais seulement si l'on sait la chercher.
- **Proposition :** récrire sur place les l. 936 et 937 (`history: tuple[HistoryEntry, ...]`, exemples donnés comme `text`), avec « (amendement 2) » en fin de ligne. Ne garder à la l. 949 que `HistoryEntry` et `HistoryKind`.

### Détails

**D1. l. 44 : le type de la marque ne convient pas.** « **(amendement 2, précisé)** Les points 23 bis à 23 sexies sont livrés » suit une phrase d'origine qui dit qu'ils « ne le sont pas ». Or « précisé » veut dire que « le passage d'origine reste vrai » (l. 31). *Proposition :* récrire le membre de phrase d'origine en « les points 23 bis à 23 sexies, ajoutés par l'amendement 1, sont livrés (pull requests n° 23 à 27) (amendement 2, réécrit) », et garder la suite en « précisé ».

**D2. l. 168 et 169 : portée de la marque de la *Vérification* de l'objectif 12.** La ligne « *Vérification (amendement 2, réécrit) :* » suit la l. 168 sans ligne vide : elle est donc dans le même paragraphe Markdown. Son intitulé est en italique, alors que la règle de la l. 40 parle d'un intitulé « en gras ». Selon la l. 43, la marque ne couvrirait que le membre de phrase qui la précède. *Proposition :* insérer une ligne vide entre les l. 168 et 169, comme aux l. 159 et 160 pour l'objectif 11, pour que la marque soit « en tête d'un paragraphe ». Ou étendre la l. 40 à « en gras ou en italique ».

**D3. l. 536 : la seconde phrase de la puce n'est pas marquée.** « (amendement 2, réécrit) », placé en fin de première phrase, ne couvre que celle-ci (l. 43). « Ils remplacent `clients/map_layout.py`… » passe donc pour du texte de l'amendement 1. *Proposition :* mettre « **(amendement 2, réécrit)** » en tête de la puce.

**D4. l. 651 : fonction absente du point 13.** `scripted_miner.mettre_a_jour` n'est pas déclarée au point 13 (l. 923 à 925 : seulement `POLICY_VERSION` et `decide`). Elle existe dans `src/fourx/policies/scripted_miner.py`. *Proposition :* ajouter au bloc du point 13 « `mettre_a_jour(observation: Observation, seen_empty: frozenset[int]) -> frozenset[int]   (amendement 2)` ».

**D5. l. 235, CUJ A, *Given* : texte devenu inexact, hors de la liste des passages touchés.** Au démarrage, l'aide est désormais ouverte (l. 670), et l'écran décrit est celui de l'amendement 1. *Proposition :* une précision marquée, par exemple « (amendement 2, précisé) l'aide est ouverte ; il la ferme par Entrée », puis ajouter « CUJ A » à la l. 49. Ou dire, à la l. 94, que la préséance couvre le CUJ A.

**D6. l. 1229, risque « Rendu différent selon le terminal » : la parade dépasse ce que le document prévoit.**
- « contraste testé sur les seize couleurs » : `CONTRAST_PAIRS` exclut les traits et `ombre` (l. 592).
- « rendu en 256 couleurs jugé à la partie d'essai » : le point 23 undecies (l. 1649) ne demande pas ce jugement.

*Proposition :* écrire « contraste testé sur les couples de `CONTRAST_PAIRS` ». Ajouter au point 23 undecies l'essai en 256 couleurs, ou le retirer du risque.

**D7. l. 1388 et 1262 : « trois volets de jeu » ne correspond plus au plan.** Le palier 3 compte désormais cinq volets : A, B, B bis, B ter et C. L'écart date de l'amendement 1, et l'amendement 2 l'aggrave. *Proposition :* une précision marquée, par exemple « (amendement 2, précisé) les volets B bis et B ter s'y insèrent ».

**D8. l. 1601 : formulations peu durables ou inexactes.**
- « le volet C démarre dès maintenant » : l'expression est datée par le contexte. Écrire plutôt « dès le 2026-11-22 ».
- « Ils ne touchent que le client » : le point 23 septies touche aussi la documentation, le niveau 1 et les ADR ; les points 23 octies et 23 decies touchent les scénarios et `tests/proprietes/`. Écrire plutôt « Dans `src/`, ils ne touchent que `clients` ».

**D9. l. 49 : « conventions » est ambigu.** L'amendement 2 touche la convention de numérotation du paragraphe « Amendements » (l. 25), pas les « Autres conventions » (l. 16 à 21). *Proposition :* « en-tête (statut, date, puce Amendements, numérotation des amendements, code livré) ».

**D10. l. 1136 et 1137 : deux lignes vides de suite avant l'alternative AB** (reste du tour 1, D12). Ailleurs, le double saut ne précède que les séparateurs. *Proposition :* en supprimer une.

**D11. l. 183 et 670 : touches de fermeture de l'aide incohérentes.** La *Vérification* de l'objectif 19 teste la « fermeture par Entrée et Échap », alors que le point 7 ter ajoute `h`. *Proposition :* « fermeture par Entrée, Échap et `h` ».

**D12. l. 1811 et 1813 : portée de la légende.** Les marques « *(remplacé par l'amendement 2…)* » sont réservées au « plan détaillé seulement » (l. 36). Le Verification Plan est bien un `###` du Detailed Implementation Plan, mais les lignes 1 et 2 du tableau le citent à part du « plan détaillé ». *Proposition :* écrire à la l. 36 « dans le plan détaillé (Verification Plan compris) ».

**D13. l. 1609, point 23 septies : il manque la clause de refus de l'ADR.** Le point 23 bis (l. 1506) dit ce qui est retiré si le propriétaire refuse une ADR. *Proposition :* « S'il refuse l'ADR 0006, la modification du niveau 1 et les passages de l'amendement 2 qui en dépendent sont retirés avant la fusion. »

**D14. ADR 0006, l. 9 : présent devenu faux.** « Le niveau 1 décrit le jeu comme « … le client ASCII » » est inexact depuis la modification du niveau 1, l. 16. *Proposition :* « Le niveau 1 décrivait (avant cette ADR) ». Les ADR voisines emploient aussi le présent (0005 : « Aujourd'hui… ») : ce n'est qu'un détail.

## 4. Synthèse pour le correcteur

1. **Fond :** N1 (décisions du 2026-11-22 en lignes du point 1, retrait du libellé « E1 à E4 ») ; N2 (critère de sortie et verdict non bloquant).
2. **Point 13 :** N3 (`history` récrit sur place) ; D4 (`mettre_a_jour`).
3. **Marques et portées :** D1 (l. 44), D2 (l. 169), D3 (l. 536), D12 (légende).
4. **Passages non marqués :** D5 (CUJ A, à ajouter à la l. 49 si on l'amende), D7 (« trois volets »).
5. **Cohérence :** D6, D8, D11, D13 ; forme : D9, D10, D14.
