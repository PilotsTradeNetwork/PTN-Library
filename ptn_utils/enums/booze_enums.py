from enum import StrEnum


class CruiseSystemState(StrEnum):
    """Global state of the cruise system."""

    PREP = "prep"
    ACTIVE = "active"
    ENDED = "ended"
    CHANNELS_CLOSED = "channels_closed"
