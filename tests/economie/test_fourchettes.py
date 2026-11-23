"""Les fourchettes de l'économie sur la partie de référence (docs/designs/niveau-2-m1-noyau.md,
objectif 5 ; Technical Plan, point 9 ; plan détaillé, point 27, amendement 1). Marque `lent`.

Rejoue le journal enregistré de la partie de référence par `replay_orders`, calcule les grandeurs
par `window_stats`, et vérifie chaque fenêtre de 10 000 ticks, la première comprise, contre les
bornes calculées par `bornes` à partir du monde de la graine 1, du nombre de PNJ et des réglages.
"""

import pytest

from fourx.core.world import generate, npc_count
from fourx.server.order_log import import_jsonl
from fourx.server.tunables_loader import load_tunables
from fourx.tools.replay import replay_orders
from tests.economie.bornes import bornes, ecarts
from tests.rejeu.partie_reference import GRAINE, TICKS, dossier_de_revision


@pytest.mark.lent
def test_l_economie_reste_dans_ses_fourchettes() -> None:
    tunables = load_tunables()
    _, ordres = import_jsonl(dossier_de_revision() / "orders.jsonl")
    initial = generate(GRAINE, tunables)
    _, evenements = replay_orders(initial, ordres, GRAINE, tunables)
    limites = bornes(initial, npc_count(GRAINE, tunables), tunables)
    fenetres, erreurs = ecarts(evenements, limites, tunables.tax_rate_bp, TICKS // limites.fenetre)
    for f in fenetres:
        print(f)
    assert not erreurs, "\n".join(erreurs)
