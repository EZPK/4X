"""Types d'acteur et activités d'un vaisseau.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 13.
"""

import enum


class ActorKind(enum.Enum):
    HUMAN = "human"
    AI_PLAYER = "ai_player"
    NPC = "npc"


class Activity(enum.Enum):
    IDLE = "idle"
    EN_ROUTE = "en_route"
    MINING = "mining"
