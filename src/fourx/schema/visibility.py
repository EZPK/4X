"""Classes de visibilité (docs/designs/niveau-2-m1-noyau.md, Technical Plan, points 5 et 13)."""

import enum

import msgspec


class Visibility(enum.Enum):
    PUBLIC = "public"
    CORPORATION = "corporation"
    PRIVATE = "private"
    ADMIN = "admin"


def visible(classe: Visibility) -> msgspec.Meta:
    """Métadonnée qui déclare la classe de visibilité d'un champ de données."""
    return msgspec.Meta(extra={"visibility": classe.value})


def classe_de(extra: dict[str, object] | None) -> Visibility | None:
    """Relit la classe de visibilité dans les métadonnées d'un champ, ou None."""
    if not extra or "visibility" not in extra:
        return None
    return Visibility(extra["visibility"])
