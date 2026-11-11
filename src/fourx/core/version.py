"""Version des règles (docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 8 ; niveau 1, §3).

`rules_version` est formé du numéro de révision, tenu à la main, et de l'empreinte des
réglages, calculée sur leur encodage MessagePack (un commentaire de tunables.toml ne la change
pas). RULES_REVISION vaut 0 au volet A ; il passe à 1 avec la première création des références,
et le contrôle de garde exige qu'il augmente de un à chaque régénération.
"""

import hashlib

import msgspec.msgpack

from fourx.core.tunables import Tunables

RULES_REVISION = 0


def tunables_fingerprint(tunables: Tunables) -> str:
    return hashlib.blake2b(msgspec.msgpack.encode(tunables), digest_size=8).hexdigest()


def rules_version(tunables: Tunables) -> str:
    return f"rules-{RULES_REVISION}+{tunables_fingerprint(tunables)}"
