"""Étapes du scénario d'exemple.

Elles sont recopiées dans les sessions imbriquées de `test_conftest_scenarios.py`.
"""

from pytest_bdd import given, parsers, then, when


@given(parsers.parse("un compteur à {depart:d}"), target_fixture="compteur")
def compteur(depart: int) -> list[int]:
    return [depart]


@when(parsers.parse("on l'augmente de {pas:d}"))
def augmenter(compteur: list[int], pas: int) -> None:
    compteur[0] += pas


@then(parsers.parse("il vaut {attendu:d}"))
def verifier(compteur: list[int], attendu: int) -> None:
    assert compteur[0] == attendu
