"""Tests de l'outil de divergence (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 8 et
13 ; niveau 1, CUJ 4)."""

from pathlib import Path

import msgspec
import msgspec.structs
import pytest

from fourx.core.fingerprints import Fingerprints
from fourx.server.game import Game
from fourx.server.tunables_loader import load_tunables
from fourx.tools.divergence import COMPOSANTS, first_divergence, lire_empreintes, main, texte


def empreinte(tick: int, **changements: str) -> Fingerprints:
    valeurs = {c: f"{c}-{tick}" for c in COMPOSANTS} | changements
    return Fingerprints(tick=tick, **valeurs)


SUITE = tuple(empreinte(t) for t in range(1, 6))


def ecrire(chemin: Path, empreintes: tuple[Fingerprints, ...]) -> Path:
    chemin.write_bytes(b"".join(msgspec.json.encode(e) + b"\n" for e in empreintes))
    return chemin


def test_les_composants_sont_les_champs_des_empreintes_sauf_le_tick() -> None:
    assert COMPOSANTS == (
        "systems",
        "deposits",
        "stations",
        "actors",
        "ships",
        "ledger",
        "last_tick",
    )


def test_aucune_divergence() -> None:
    assert first_divergence(SUITE, SUITE) is None
    assert first_divergence((), ()) is None


def test_premier_tick_qui_differe_et_composants_dans_l_ordre_des_champs() -> None:
    autre = list(SUITE)
    autre[2] = empreinte(3, ledger="x", ships="y")
    autre[3] = empreinte(4, systems="z")
    assert first_divergence(SUITE, autre) == (3, ("ships", "ledger"))
    assert first_divergence(autre, SUITE) == (3, ("ships", "ledger"))


def test_tick_decale_sans_composant_different() -> None:
    decale = (*SUITE[:2], msgspec.structs.replace(SUITE[2], tick=9), *SUITE[3:])
    assert first_divergence(SUITE, decale) == (3, ())


def test_un_tick_present_d_un_seul_cote_differe_par_tous_ses_composants() -> None:
    assert first_divergence(SUITE, SUITE[:3]) == (4, COMPOSANTS)
    assert first_divergence(SUITE[:3], SUITE) == (4, COMPOSANTS)
    assert first_divergence((), SUITE) == (1, COMPOSANTS)


def test_texte() -> None:
    assert texte(None) == "aucune divergence"
    assert texte((50, ("ledger",))) == "tick 50 : ledger"
    assert texte((7, ("ships", "ledger"))) == "tick 7 : ships, ledger"


def test_lire_un_fichier_d_empreintes(tmp_path: Path) -> None:
    chemin = ecrire(tmp_path / "e.jsonl", SUITE)
    chemin.write_bytes(chemin.read_bytes() + b"\n")  # une ligne vide en fin de fichier est ignorée
    assert lire_empreintes(chemin) == SUITE


def test_lire_un_dossier_de_partie(tmp_path: Path) -> None:
    jeu = Game(tmp_path, world_seed=1, tunables=load_tunables())
    jeu.advance(3)
    jeu.close()
    empreintes = lire_empreintes(jeu.run_dir)
    assert [e.tick for e in empreintes] == [1, 2, 3]


def test_commande(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    a = ecrire(tmp_path / "a.jsonl", SUITE)
    b = ecrire(tmp_path / "b.jsonl", (*SUITE[:4], empreinte(5, actors="x")))
    assert main([str(a), str(a)]) == 0
    assert capsys.readouterr().out == "aucune divergence\n"
    assert main([str(a), str(b)]) == 1
    assert capsys.readouterr().out == "tick 5 : actors\n"
