from enum import Enum


class Activities(Enum):
    """Enum for activities"""

    ROTARY_DRILLING = "rotary_drilling"
    SLIDE_DRILLING = "slide_drilling"
    TRIPPING_IN = "tripping_in"
    TRIPPING_OUT = "tripping_out"
    CASING = "casing"
    CIRCULATING = "circulating"
