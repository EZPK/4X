"""Point d'entrée des scénarios en français (docs/designs/niveau-2-m0-garde-fous.md, Technical Plan,
point 10 ; docs/designs/niveau-2-m1-noyau.md, palier 3).

Chemin protégé. Chaque volet ajoute ici l'import de son module d'étapes.
"""

from pytest_bdd import scenarios

from tests.scenarios.steps.steps_noyau import *  # noqa: F403
from tests.scenarios.steps.steps_partie import *  # noqa: F403

scenarios(".")
