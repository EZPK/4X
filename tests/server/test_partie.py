"""Tests de la partie en mémoire : boucle des ticks avec et sans horloge
(docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 6 ; plan détaillé, points 21 et 23)."""

import asyncio
import re
from collections.abc import Coroutine, Iterator
from datetime import UTC, datetime
from pathlib import Path

import msgspec.json
import pytest

from fourx.__main__ import creer_pnj, relayer
from fourx.clients.npc_host import NpcHost
from fourx.core import snapshot
from fourx.core.fingerprints import fingerprints
from fourx.core.step import step
from fourx.policies.scripted_miner import POLICY_ID, decide
from fourx.schema.actors import ActorKind
from fourx.schema.events import CharacterCreated, Event
from fourx.schema.orders import CreateCharacter, Move, Order, OrderCategory
from fourx.schema.protocol import NOMINAL_TICK_PERIOD_S, PROTOCOL_VERSION, SubmitOrders, TickUpdate
from fourx.server.game import Game
from fourx.server.order_log import OrderLog
from fourx.server.tunables_loader import load_tunables


@pytest.fixture
def jeu(tmp_path: Path) -> Iterator[Game]:
    partie = Game(tmp_path, world_seed=3, tunables=load_tunables())
    yield partie
    partie.close()


class Enregistreur:
    def __init__(self) -> None:
        self.mises_a_jour: list[TickUpdate] = []

    def on_update(self, update: TickUpdate) -> SubmitOrders | None:
        self.mises_a_jour.append(update)
        return None


def journal(jeu: Game) -> OrderLog:
    return OrderLog(jeu.run_dir / "orders.sqlite")


def test_dossier_de_la_partie(jeu: Game, tmp_path: Path) -> None:
    assert jeu.run_dir.parent == tmp_path
    assert (jeu.world_seed, jeu.period_s) == (3, NOMINAL_TICK_PERIOD_S)
    assert re.fullmatch(r"\d{8}-\d{6}-\d{6}", jeu.run_dir.name)
    fichiers = {f.name for f in jeu.run_dir.iterdir()}
    assert {"snapshot.msgpack", "orders.sqlite", "events.jsonl"} <= fichiers


def test_creation_des_personnages_au_tick_suivant(jeu: Game) -> None:
    assert jeu.create_character(ActorKind.HUMAN) == 1
    assert jeu.create_character(ActorKind.NPC) == 2
    avant = jeu.state.actors
    assert avant == ()
    jeu.advance(1)
    assert [(a.id, a.kind) for a in jeu.state.actors] == [(1, ActorKind.HUMAN), (2, ActorKind.NPC)]
    assert jeu.create_character(ActorKind.HUMAN) == 3
    (tick_1,) = journal(jeu).orders_by_tick()
    assert [(s.tick, s.sender_actor_id, s.order.category) for s in tick_1] == [
        (1, None, OrderCategory.ADMIN),
        (1, None, OrderCategory.ADMIN),
    ]
    assert [(s.order.actor_id, s.order.number) for s in tick_1] == [(1, 0), (2, 0)]
    assert [s.order.command for s in tick_1] == [
        CreateCharacter(actor_kind=ActorKind.HUMAN),
        CreateCharacter(actor_kind=ActorKind.NPC),
    ]


def test_ordre_d_une_connexion_entre_au_tick_suivant(jeu: Game) -> None:
    acteur = jeu.create_character(ActorKind.HUMAN)
    connexion = jeu.connect(acteur)
    assert jeu.connect(acteur) is connexion
    assert connexion.actor_id == acteur
    jeu.advance(1)
    vaisseau = jeu.state.ships[0]
    voisin = next(s for s in jeu.state.systems if s.id == vaisseau.system_id).neighbors[0]
    ordre = Order(
        actor_id=acteur,
        number=1,
        category=OrderCategory.PLAYER,
        policy_id=None,
        policy_version=None,
        command=Move(ship_id=vaisseau.id, target_system_id=voisin),
    )
    connexion.submit(SubmitOrders(protocol_version=PROTOCOL_VERSION, orders=(ordre,)))
    jeu.advance(1)
    tick_2 = journal(jeu).orders_by_tick()[1]
    assert [(s.tick, s.sender_actor_id, s.order) for s in tick_2] == [(2, acteur, ordre)]
    assert jeu.state.ships[0].route == (voisin,)
    # Une mise à jour par tick dans la file de la connexion, dans l'ordre des ticks.
    vues = [connexion.mises_a_jour.get_nowait().observation for _ in range(2)]
    assert [v.tick for v in vues] == [1, 2]
    assert all(v.actor_id == acteur and len(v.own_ships) == 1 for v in vues)
    assert connexion.mises_a_jour.empty()


def test_client_synchrone_attache_avant_la_creation(jeu: Game) -> None:
    acteur = jeu.create_character(ActorKind.HUMAN)
    client = Enregistreur()
    jeu.attach(acteur, client)
    jeu.advance(3)
    assert [m.observation.tick for m in client.mises_a_jour] == [1, 2, 3]
    assert all(m.protocol_version == PROTOCOL_VERSION for m in client.mises_a_jour)
    assert len(client.mises_a_jour[0].observation.own_ships) == 1


def test_les_ordres_renvoyes_par_un_client_entrent_au_tick_suivant(jeu: Game) -> None:
    pnj = jeu.create_character(ActorKind.NPC)
    jeu.attach(pnj, NpcHost(pnj, decide))
    jeu.advance(2)
    tick_1, tick_2 = journal(jeu).orders_by_tick()
    assert all(s.sender_actor_id is None for s in tick_1)
    assert tick_2
    assert all(
        (s.tick, s.sender_actor_id, s.order.policy_id, s.reception_refusal)
        == (2, pnj, POLICY_ID, None)
        for s in tick_2
    )


def test_journal_evenements_et_empreintes_a_chaque_tick(jeu: Game) -> None:
    pnj = jeu.create_character(ActorKind.NPC)
    jeu.attach(pnj, NpcHost(pnj, decide))
    jeu.advance(30)
    log = journal(jeu)
    assert len(log.orders_by_tick()) == 30
    empreintes = log.fingerprints_by_tick()
    assert [e.tick for e in empreintes] == list(range(1, 31))
    assert empreintes[-1] == fingerprints(jeu.state)
    decodeur = msgspec.json.Decoder(Event)
    lignes = (jeu.run_dir / "events.jsonl").read_bytes().splitlines()
    evenements = [decodeur.decode(ligne) for ligne in lignes]
    assert isinstance(evenements[0].payload, CharacterCreated)
    assert [e.tick for e in evenements] == sorted(e.tick for e in evenements)
    assert [(e.tick, e.seq) for e in evenements] == sorted({(e.tick, e.seq) for e in evenements})


def test_cree_les_dossiers_parents(tmp_path: Path) -> None:
    partie = Game(tmp_path / "a" / "b", world_seed=3, tunables=load_tunables())
    partie.close()
    assert partie.run_dir.parent == tmp_path / "a" / "b"


class HorlogeFixe:
    """Remplace `datetime` dans fourx.server.game : une seule heure, demandée en UTC."""

    @staticmethod
    def now(tz: object) -> datetime:
        assert tz is UTC
        return datetime(2026, 11, 21, 8, 30, 5, 123456, tzinfo=UTC)


def test_dossier_de_partie_horodate_en_utc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("fourx.server.game.datetime", HorlogeFixe)
    partie = Game(tmp_path, world_seed=3, tunables=load_tunables())
    partie.close()
    assert partie.run_dir == tmp_path / "20261121-083005-123456"


def test_un_dossier_de_partie_existant_n_est_pas_reutilise(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("fourx.server.game.datetime", HorlogeFixe)
    (tmp_path / "20261121-083005-123456").mkdir()
    with pytest.raises(FileExistsError):
        Game(tmp_path, world_seed=3, tunables=load_tunables())


def test_boucle_avec_horloge(tmp_path: Path) -> None:
    async def jouer() -> list[int]:
        partie = Game(tmp_path, world_seed=3, tunables=load_tunables(), period_s=0.001)
        acteur = partie.create_character(ActorKind.HUMAN)
        connexion = partie.connect(acteur)
        horloge = asyncio.create_task(partie.run())
        try:
            return [(await connexion.next_update()).observation.tick for _ in range(3)]
        finally:
            horloge.cancel()
            with pytest.raises(asyncio.CancelledError):
                await horloge
            partie.close()

    assert asyncio.run(jouer()) == [1, 2, 3]


def test_premier_tick_immediat(tmp_path: Path) -> None:
    """Le mode avec horloge joue un tick dès son lancement, sans attendre la période."""

    async def jouer() -> int:
        partie = Game(tmp_path, world_seed=3, tunables=load_tunables(), period_s=60.0)
        acteur = partie.create_character(ActorKind.HUMAN)
        connexion = partie.connect(acteur)
        horloge = asyncio.create_task(partie.run())
        try:
            mise_a_jour = await asyncio.wait_for(connexion.next_update(), timeout=5)
            return int(mise_a_jour.observation.tick)
        finally:
            horloge.cancel()
            with pytest.raises(asyncio.CancelledError):
                await horloge
            partie.close()

    assert asyncio.run(jouer()) == 1


# --- Vitesse de l'univers (amendement 1 ; Technical Plan, point 6)


def lignes_de_vitesse(dossier: Path) -> list[dict[str, object]]:
    return [
        msgspec.json.decode(ligne)
        for ligne in (dossier / "speed.jsonl").read_text(encoding="utf-8").splitlines()
    ]


def test_speed_jsonl_en_tete_periode_initiale_et_changements(jeu: Game) -> None:
    assert lignes_de_vitesse(jeu.run_dir) == [
        {"speed_log_schema_version": 1},
        {"tick": 0, "period_s": NOMINAL_TICK_PERIOD_S},
    ]
    jeu.advance(2)
    jeu.set_period(0.3)
    jeu.advance(1)
    jeu.set_period(None)
    assert jeu.period_s is None
    assert lignes_de_vitesse(jeu.run_dir)[2:] == [
        {"tick": 2, "period_s": 0.3},
        {"tick": 3, "period_s": None},
    ]


async def avec_horloge(partie: Game, test: Coroutine[None, None, None]) -> None:
    """Lance l'horloge, attend la coroutine de test, puis arrête l'horloge et ferme la partie."""
    horloge = asyncio.create_task(partie.run())
    try:
        await test
    finally:
        horloge.cancel()
        with pytest.raises(asyncio.CancelledError):
            await horloge
        partie.close()


def test_pause_puis_reprise(tmp_path: Path) -> None:
    releves: list[int] = []

    async def jouer() -> None:
        partie = Game(tmp_path, world_seed=3, tunables=load_tunables(), period_s=0.001)
        connexion = partie.connect(partie.create_character(ActorKind.HUMAN))

        async def test() -> None:
            while (await connexion.next_update()).observation.tick < 3:
                pass
            partie.set_period(None)
            await asyncio.sleep(0.05)
            releves.append(partie.state.tick)
            await asyncio.sleep(0.1)
            releves.append(partie.state.tick)
            partie.set_period(0.001)
            while partie.state.tick < releves[-1] + 3:
                await asyncio.sleep(0.005)
            releves.append(partie.state.tick)

        await avec_horloge(partie, test())

    asyncio.run(jouer())
    en_pause, toujours, repris = releves
    assert en_pause == toujours
    assert repris >= toujours + 3


def test_une_periode_plus_courte_reveille_l_horloge(tmp_path: Path) -> None:
    """À 60 s par tick, le passage à 1 ms joue le tick suivant sans attendre la minute."""
    ticks: list[int] = []

    async def jouer() -> None:
        partie = Game(tmp_path, world_seed=3, tunables=load_tunables(), period_s=60.0)
        connexion = partie.connect(partie.create_character(ActorKind.HUMAN))

        async def test() -> None:
            await asyncio.wait_for(connexion.next_update(), timeout=5)
            partie.set_period(0.001)
            mise_a_jour = await asyncio.wait_for(connexion.next_update(), timeout=5)
            ticks.append(mise_a_jour.observation.tick)

        await avec_horloge(partie, test())

    asyncio.run(jouer())
    assert ticks == [2]


def test_une_periode_plus_longue_attend_le_reste(tmp_path: Path) -> None:
    """Juste après un tick, passer à 60 s ne joue aucun tick tout de suite."""
    releves: list[int] = []

    async def jouer() -> None:
        partie = Game(tmp_path, world_seed=3, tunables=load_tunables(), period_s=0.001)
        connexion = partie.connect(partie.create_character(ActorKind.HUMAN))

        async def test() -> None:
            await connexion.next_update()
            partie.set_period(60.0)
            releves.append(partie.state.tick)
            await asyncio.sleep(0.1)
            releves.append(partie.state.tick)

        await avec_horloge(partie, test())

    asyncio.run(jouer())
    avant, apres = releves
    assert apres == avant


def test_rejeu_exact_d_une_partie_jouee_en_accelere(tmp_path: Path) -> None:
    """Une partie avec PNJ jouée à plusieurs vitesses, avec une pause : les ordres du journal,
    rejoués par step depuis l'instantané initial, redonnent les empreintes du journal
    (l'outil de rejeu n'existe qu'au volet C)."""
    reglages = load_tunables()
    dossiers: list[Path] = []

    async def jouer() -> None:
        partie = Game(tmp_path, world_seed=3, tunables=reglages, period_s=0.002)
        dossiers.append(partie.run_dir)
        humain = partie.create_character(ActorKind.HUMAN)
        pnj = creer_pnj(partie, 3, reglages)
        relais = [asyncio.create_task(relayer(partie.connect(i), NpcHost(i, decide))) for i in pnj]
        temoin = partie.connect(humain)

        async def test() -> None:
            for periode in (0.0002, None, 0.002, 0.0002):
                partie.set_period(periode)
                if periode is None:
                    await asyncio.sleep(0.02)
                    continue
                cible = partie.state.tick + 40
                while (await temoin.next_update()).observation.tick < cible:
                    pass

        try:
            await avec_horloge(partie, test())
        finally:
            for tache in relais:
                tache.cancel()

    asyncio.run(jouer())
    dossier = dossiers[0]
    initial = snapshot.decode((dossier / "snapshot.msgpack").read_bytes())
    log = OrderLog(dossier / "orders.sqlite")
    ordres, empreintes = log.orders_by_tick(), log.fingerprints_by_tick()
    log.close()
    assert len(ordres) >= 120
    assert any(s.order.policy_id == POLICY_ID for du_tick in ordres for s in du_tick)
    etat = initial.state
    rejouees = []
    for du_tick in ordres:
        etat, _ = step(etat, du_tick, 3, reglages)
        rejouees.append(fingerprints(etat))
    assert tuple(rejouees) == empreintes
    assert [ligne["period_s"] for ligne in lignes_de_vitesse(dossier)[1:]] == [
        0.002,
        0.0002,
        None,
        0.002,
        0.0002,
    ]
