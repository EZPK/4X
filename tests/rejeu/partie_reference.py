"""La partie de référence et l'outil de régénération des références
(docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 8 et 9 ; plan détaillé, points 26 et 27).

La partie de référence : graine 1, jouée par ses `npc_count(1, réglages)` PNJ (hôte des PNJ,
politique `scripted_miner`), à travers le serveur en mode sans horloge, pendant 100 000 ticks, sur
les réglages de `tunables.toml`. Elle n'est jouée qu'à la régénération des références, lancée sur
l'ordinateur portable par :

    FOURX_REGENERER_REFERENCES=1 uv run pytest -m rejeu tests/rejeu/test_rejeu.py -s

L'outil vérifie la partie contre les bornes de l'économie (refus d'écrire si elle en sort), relève
les fenêtres, les gisements vidés et les départages, écrit
`tests/references/rules-<RULES_REVISION>/` (`orders.jsonl`, `reference.json`), supprime l'ancien
dossier, et affiche le rapport de différences avec la révision précédente.

Il vit sous `tests/` parce qu'il assemble `server`, `clients` et `policies` (Technical Plan,
point 8).
"""

import shutil
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest import mock

import msgspec

from fourx.__main__ import creer_pnj
from fourx.clients.npc_host import NpcHost
from fourx.core import keyed_random
from fourx.core import step as module_step
from fourx.core.fingerprints import Fingerprints
from fourx.core.state import State
from fourx.core.tunables import Tunables
from fourx.core.version import RULES_REVISION
from fourx.core.world import generate, npc_count
from fourx.policies.scripted_miner import decide
from fourx.schema.events import Event
from fourx.schema.orders import SubmittedOrder
from fourx.server.game import Game
from fourx.server.order_log import OrderLog, import_jsonl
from fourx.tools.divergence import first_divergence, texte
from fourx.tools.economy import WindowStats
from tests.economie.bornes import Bornes, bornes, ecarts

GRAINE = 1
TICKS = 100_000
PAS_DES_EMPREINTES = 1_000
RACINE = Path(__file__).resolve().parents[2]
REFERENCES = RACINE / "tests" / "references"


class Reference(msgspec.Struct, frozen=True):
    """`reference.json` : `rules_version`, et les empreintes tous les 1 000 ticks et au dernier."""

    rules_version: str
    fingerprints: tuple[Fingerprints, ...]


def dossier_de_revision(revision: int = RULES_REVISION) -> Path:
    return REFERENCES / f"rules-{revision}"


def releves(empreintes: Sequence[Fingerprints]) -> tuple[Fingerprints, ...]:
    """Les empreintes tous les 1 000 ticks, et celle du dernier tick."""
    dernier = empreintes[-1].tick if empreintes else 0
    return tuple(e for e in empreintes if e.tick % PAS_DES_EMPREINTES == 0 or e.tick == dernier)


def lire_reference(dossier: Path) -> Reference:
    return msgspec.json.decode((dossier / "reference.json").read_bytes(), type=Reference)


def lire_evenements(chemin: Path) -> tuple[Event, ...]:
    decodeur = msgspec.json.Decoder(Event)
    return tuple(decodeur.decode(ligne) for ligne in chemin.read_bytes().splitlines() if ligne)


def jouer(runs_dir: Path, tunables: Tunables, ticks: int = TICKS) -> Path:
    """Joue la partie de référence ; rend son dossier de partie."""
    jeu = Game(runs_dir, GRAINE, tunables)
    for ident in creer_pnj(jeu, GRAINE, tunables):
        jeu.attach(ident, NpcHost(ident, decide))
    jeu.advance(ticks)
    jeu.close()
    return jeu.run_dir


@dataclass
class Epuisement:
    """Ticks où un gisement s'est vidé, et ticks de départage, par gisement."""

    vides: dict[int, list[int]] = field(default_factory=dict)
    departages: dict[int, list[int]] = field(default_factory=dict)


def relever_epuisement(
    initial: State, ordres: Sequence[tuple[SubmittedOrder, ...]], tunables: Tunables
) -> Epuisement:
    """Rejoue les états par `step` et relève, à chaque tick :
    - un gisement vidé : son stock passe d'une valeur positive à 0 pendant la phase de minage
      (lu juste après `_minage`, avant la régénération de la fin du tick) ;
    - un départage : plusieurs vaisseaux minent un même gisement dont le stock est inférieur à la
      somme de leurs débits. C'est exactement le cas où `step` tire leur ordre par `keyed_draw` ;
      chaque tirage est relevé avec le vaisseau, rangé par gisement de son système (un gisement au
      plus par système)."""
    releve = Epuisement()
    tires: list[int] = []
    tirage = keyed_random.keyed_draw
    minage = module_step._minage

    def espion_du_tirage(
        world_seed: int, tick: int, ident: int, motif: str, attempt: int = 0
    ) -> int:
        tires.append(ident)
        return tirage(world_seed, tick, ident, motif, attempt)

    def espion_du_minage(t: Any) -> None:
        avant = {i: g.stock for i, g in t.deposits.items()}
        minage(t)
        for i in sorted(t.deposits):
            if avant[i] > 0 and t.deposits[i].stock == 0:
                releve.vides.setdefault(i, []).append(t.tick)

    etat = initial
    with (
        mock.patch("fourx.core.step.keyed_draw", espion_du_tirage),
        mock.patch("fourx.core.step._minage", espion_du_minage),
    ):
        for soumis in ordres:
            tires.clear()
            etat, _ = module_step.step(etat, soumis, GRAINE, tunables)
            systeme_du_vaisseau = {s.id: s.system_id for s in etat.ships}
            gisement_du_systeme = {g.system_id: g.id for g in etat.deposits}
            par_gisement: dict[int, set[int]] = {}
            for ident in tires:
                gisement = gisement_du_systeme[systeme_du_vaisseau[ident]]
                par_gisement.setdefault(gisement, set()).add(ident)
            for gisement, vaisseaux in sorted(par_gisement.items()):
                if len(vaisseaux) >= 2:
                    releve.departages.setdefault(gisement, []).append(etat.tick)
    return releve


def texte_des_bornes(limites: Bornes) -> str:
    return (
        f"Bornes : N = {limites.n_pnj} PNJ, p_max = {limites.p_max}, d_min = {limites.d_min}, "
        f"C_min = {limites.duree_minimale_d_un_cycle} ticks, "
        f"b' = {limites.cycles_max_par_fenetre} cycles par fenêtre ; émission ORE_SALE par "
        f"fenêtre dans ]0, {limites.emission_max}]"
    )


def texte_des_fenetres(fenetres: Sequence[WindowStats]) -> str:
    lignes = [
        "| Fenêtre | Émission | Destruction | Croissance | Masse en fin |",
        "|---|---|---|---|---|",
    ]
    for f in fenetres:
        lignes.append(
            f"| {f.first_tick} | {sum(f.issued_by_reason)} | {sum(f.destroyed_by_reason)} | "
            f"{f.money_supply_growth} | {f.money_supply_end} |"
        )
    return "\n".join(lignes)


def texte_de_l_epuisement(releve: Epuisement) -> str:
    def resume(par_gisement: dict[int, list[int]]) -> str:
        if not par_gisement:
            return "aucun"
        return " ; ".join(
            f"deposit_{g} : {len(t)} fois (premier au tick {t[0]})"
            for g, t in sorted(par_gisement.items())
        )

    return f"Gisements vidés : {resume(releve.vides)}\nDépartages : {resume(releve.departages)}"


def rapport_de_differences(
    precedente: Path | None, nouvelle: Reference, ordres_lignes: int, taille: int
) -> str:
    """Le rapport de différences avec la révision précédente des références."""
    entete = f"Rapport de différences : {precedente.name if precedente else 'aucune'} → "
    entete += f"rules-{RULES_REVISION}"
    lignes = [entete]
    if precedente is None:
        lignes.append("- révision précédente : aucune (première création des références)")
    else:
        ancienne = lire_reference(precedente)
        ancienne_taille = sum(f.stat().st_size for f in precedente.iterdir())
        anciennes_lignes = len((precedente / "orders.jsonl").read_bytes().splitlines()) - 1
        divergence = first_divergence(ancienne.fingerprints, nouvelle.fingerprints)
        lignes += [
            f"- rules_version : {ancienne.rules_version} → {nouvelle.rules_version}",
            f"- ordres soumis : {anciennes_lignes} → {ordres_lignes}",
            f"- premier relevé d'empreintes qui diffère : {texte(divergence)}",
            f"- taille du dossier : {ancienne_taille} → {taille} octets",
        ]
    if precedente is None:
        lignes += [
            f"- rules_version : {nouvelle.rules_version}",
            f"- ordres soumis : {ordres_lignes}",
            f"- relevés d'empreintes : {len(nouvelle.fingerprints)}",
            f"- taille du dossier : {taille} octets",
        ]
    return "\n".join(lignes)


def regenerer(runs_dir: Path, tunables: Tunables, afficher: Callable[[str], None]) -> None:
    """L'outil de régénération. Refuse d'écrire si la partie sort des bornes de l'économie."""
    run_dir = jouer(runs_dir, tunables)
    initial = generate(GRAINE, tunables)
    limites = bornes(initial, npc_count(GRAINE, tunables), tunables)
    fenetres, erreurs = ecarts(
        lire_evenements(run_dir / "events.jsonl"),
        limites,
        tunables.tax_rate_bp,
        TICKS // limites.fenetre,
    )
    afficher(texte_des_bornes(limites))
    afficher(texte_des_fenetres(fenetres))
    if erreurs:
        raise AssertionError(
            "la partie de référence sort des bornes : références non écrites\n" + "\n".join(erreurs)
        )
    journal = OrderLog(run_dir / "orders.sqlite")
    try:
        empreintes = journal.fingerprints_by_tick()
        version = journal.en_tete().rules_version  # celle de la partie jouée
        ordres = journal.orders_by_tick()
    finally:
        journal.close()
    afficher(texte_de_l_epuisement(relever_epuisement(initial, ordres, tunables)))
    reference = Reference(rules_version=version, fingerprints=releves(empreintes))
    nouveau = dossier_de_revision()
    autres = sorted(
        (p for p in REFERENCES.glob("rules-*") if p != nouveau),
        key=lambda p: int(p.name.removeprefix("rules-")),
    )
    # La révision précédente : le dossier de la même révision s'il existe (régénération sans
    # changement de règles), sinon la plus haute des autres.
    precedente = nouveau if nouveau.is_dir() else (autres[-1] if autres else None)
    temporaire = REFERENCES / f".rules-{RULES_REVISION}.nouveau"
    shutil.rmtree(temporaire, ignore_errors=True)
    temporaire.mkdir(parents=True)
    try:
        journal = OrderLog(run_dir / "orders.sqlite")
        try:
            journal.export_jsonl(temporaire / "orders.jsonl")
        finally:
            journal.close()
        (temporaire / "reference.json").write_bytes(
            msgspec.json.format(msgspec.json.encode(reference))
        )
        lignes = len((temporaire / "orders.jsonl").read_bytes().splitlines()) - 1
        taille = sum(f.stat().st_size for f in temporaire.iterdir())
        afficher(rapport_de_differences(precedente, reference, lignes, taille))
        _, relus = import_jsonl(temporaire / "orders.jsonl")
        if len(relus) != TICKS:
            raise AssertionError(f"orders.jsonl relu : {len(relus)} ticks au lieu de {TICKS}")
        for ancien in autres:
            shutil.rmtree(ancien)
        shutil.rmtree(nouveau, ignore_errors=True)
        temporaire.rename(nouveau)
    finally:
        shutil.rmtree(temporaire, ignore_errors=True)
