"""Mise en page de la carte, fonction pure.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 7 bis (« Mise en page de la
carte » et « Sortie de `layout` »). Les systèmes sont rangés en colonnes de 8 caractères selon
leur distance en sauts depuis le système 1, six colonnes par bande. Le parent d'un système est
son voisin de plus petit identifiant dans la colonne précédente ; un système prend le rang de son
parent s'il est libre, sinon le premier rang libre en dessous. Un lien entre deux colonnes
voisines d'une même bande et de même rang est tracé en traits horizontaux ; tout autre lien est
écrit sous la carte. La ligne des vaisseaux n'en fait pas partie : `frames.py` l'ajoute.
"""

from fourx.policies.geometry import distances
from fourx.schema.observation import Observation

LARGEUR_CASE = 8
COLONNES_PAR_BANDE = 6
LARGEUR = LARGEUR_CASE * COLONNES_PAR_BANDE
TRAIT = "─"  # U+2500
TIRET = "–"  # U+2013
DEBUT_LIENS = "liens : "


def rangs(observation: Observation) -> tuple[dict[int, int], dict[int, int]]:
    """La colonne (distance en sauts depuis le système 1) et le rang de chaque système."""
    voisins = {s.id: s.neighbors for s in observation.systems}
    colonnes = distances(observation.systems, 1)
    rang: dict[int, int] = {}
    for colonne in range(max(colonnes.values()) + 1):
        pris: list[int] = []
        for s in sorted(i for i, c in colonnes.items() if c == colonne):
            parents = [v for v in voisins[s] if colonnes.get(v) == colonne - 1]
            r = rang[min(parents)] if parents else 0
            while r in pris:
                r += 1
            rang[s] = r
            pris.append(r)
    return colonnes, rang


def _liens(observation: Observation) -> list[tuple[int, int]]:
    """Chaque lien une fois, (a, b) avec a < b, trié par a puis par b."""
    return sorted({(min(s.id, v), max(s.id, v)) for s in observation.systems for v in s.neighbors})


def _marques(observation: Observation, systeme: int) -> str:
    stations = "".join(f"S{s.id}" for s in observation.stations if s.system_id == systeme)
    gisements = "".join(
        chr(ord("a") + d.ore_id - 1) for d in observation.deposits if d.system_id == systeme
    )
    return stations + gisements


def _lignes_de_liens(ecrits: list[tuple[int, int]]) -> list[str]:
    """« liens : a–b, c–d », coupée à la largeur de la carte, la suite sur les lignes suivantes."""
    if not ecrits:
        return []
    morceaux = [f"{a}{TIRET}{b}" for a, b in ecrits]
    lignes = [DEBUT_LIENS + morceaux[0]]
    for morceau in morceaux[1:]:
        # La place d'une virgule finale reste réservée, si la ligne doit être coupée après.
        if len(lignes[-1]) + len(", ") + len(morceau) + len(",") <= LARGEUR:
            lignes[-1] += ", " + morceau
        else:
            lignes[-1] += ","
            lignes.append(morceau)
    return lignes


def layout(observation: Observation) -> list[str]:
    """Une ligne par rang, puis, pour chaque bande suivante, une ligne vide et ses rangs ; enfin
    les liens écrits (Technical Plan, point 7 bis, « Sortie de `layout` »)."""
    colonnes, rang = rangs(observation)
    traces = [
        (a, b)
        for a, b in _liens(observation)
        if abs(colonnes[a] - colonnes[b]) == 1
        and rang[a] == rang[b]
        and colonnes[a] // COLONNES_PAR_BANDE == colonnes[b] // COLONNES_PAR_BANDE
    ]
    vers_la_droite = [a if colonnes[a] < colonnes[b] else b for a, b in traces]
    place = {(colonnes[s], rang[s]): s for s in rang}
    lignes: list[str] = []
    bandes = max(colonnes.values()) // COLONNES_PAR_BANDE + 1
    for bande in range(bandes):
        dans_la_bande = [s for s in rang if colonnes[s] // COLONNES_PAR_BANDE == bande]
        if bande > 0:
            lignes.append("")
        for r in range(max(rang[s] for s in dans_la_bande) + 1):
            cases = []
            for position in range(COLONNES_PAR_BANDE):
                s = place.get((bande * COLONNES_PAR_BANDE + position, r))
                if s is None:
                    cases.append(" " * LARGEUR_CASE)
                    continue
                texte = f"[{s}]" + _marques(observation, s)
                remplissage = TRAIT if s in vers_la_droite else " "
                cases.append(texte + remplissage * (LARGEUR_CASE - len(texte)))
            lignes.append("".join(cases).rstrip())
    ecrits = [lien for lien in _liens(observation) if lien not in traces]
    return lignes + _lignes_de_liens(ecrits)
