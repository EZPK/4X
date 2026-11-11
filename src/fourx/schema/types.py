"""Types entiers bornés sur 64 bits.

Document : docs/designs/niveau-2-m1-noyau.md, Technical Plan, point 13.
"""

from typing import Annotated

import msgspec

MIN_INT64 = -(2**63)
MAX_INT64 = 2**63 - 1

Int64 = Annotated[int, msgspec.Meta(ge=MIN_INT64, le=MAX_INT64)]
Id = Annotated[int, msgspec.Meta(ge=1, le=MAX_INT64)]
