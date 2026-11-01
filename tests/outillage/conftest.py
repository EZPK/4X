"""Configuration commune des tests de l'outillage de M0."""

import importlib.util
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

collect_ignore = ["exemple"]

RACINE = Path(__file__).resolve().parents[2]


@pytest.fixture
def racine() -> Path:
    return RACINE


@pytest.fixture
def charger_script() -> Callable[[str], ModuleType]:
    """Charge un script du dépôt à partir de son chemin relatif à la racine."""

    def charger(chemin: str) -> ModuleType:
        fichier = RACINE / chemin
        spec = importlib.util.spec_from_file_location(fichier.stem, fichier)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    return charger
