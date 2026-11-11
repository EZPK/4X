"""Tests de la sortie JSONL des événements (docs/designs/niveau-2-m1-noyau.md, Technical Plan,
points 5 et 6 ; plan détaillé, points 21 et 23)."""

from pathlib import Path

import msgspec.json

from fourx.schema.events import Arrived, Departed, Event, MiningStarted
from fourx.schema.orders import Mine, Move
from fourx.server.events_writer import EventsWriter
from tests.aide_monde import avancer, monde, ordre, vaisseau


def lire(chemin: Path) -> list[Event]:
    decodeur = msgspec.json.Decoder(Event)
    return [decodeur.decode(ligne) for ligne in chemin.read_bytes().splitlines()]


def test_une_ligne_par_evenement_a_jour_apres_chaque_ecriture(tmp_path: Path) -> None:
    state = monde((vaisseau(1, 1, system=1), vaisseau(2, 2, system=1)))
    commandes = (
        ordre(state, 1, 1, Move(ship_id=1, target_system_id=2)),
        ordre(state, 2, 1, Move(ship_id=2, target_system_id=3)),
    )
    state, premiers = avancer(state, commandes, n=5)
    assert [type(e.payload) for e in premiers] == [Departed, Arrived, Departed, Arrived]
    sortie = EventsWriter(tmp_path / "events.jsonl")
    sortie.write(tuple(premiers))
    # Le fichier est lisible sans fermer l'écriture.
    assert lire(tmp_path / "events.jsonl") == premiers
    state, suivants = avancer(state, (ordre(state, 1, 2, Mine(ship_id=1, ore_id=1)),))
    assert [type(e.payload) for e in suivants] == [MiningStarted]
    sortie.write(tuple(suivants))
    sortie.write(())
    sortie.close()
    assert lire(tmp_path / "events.jsonl") == premiers + suivants


def test_ajoute_a_un_fichier_existant(tmp_path: Path) -> None:
    state = monde((vaisseau(1, 1, system=1),))
    _, evenements = avancer(state, (ordre(state, 1, 1, Move(ship_id=1, target_system_id=2)),), n=5)
    assert evenements
    for _ in range(2):
        sortie = EventsWriter(tmp_path / "events.jsonl")
        sortie.write(tuple(evenements))
        sortie.close()
    assert lire(tmp_path / "events.jsonl") == evenements + evenements
