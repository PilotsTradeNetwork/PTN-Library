from enum import Enum


class CruiseSystemState(str, Enum):
    """Global state of the cruise system."""

    PREP = "prep"
    ACTIVE = "active"
    ENDED = "ended"
    CHANNELS_CLOSED = "channels_closed"
