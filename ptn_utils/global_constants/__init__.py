# ruff: noqa: F403
# ruff: noqa: F405
import ast
import os

PRODUCTION = ast.literal_eval(os.environ.get("PTN_SERVICE", "False"))

if PRODUCTION:
    from ptn_utils.global_constants.prod import *
else:
    from ptn_utils.global_constants.dev import *

############################
### Generic Variables    ###
############################

# Embed colours
EMBED_COLOUR_CAUTION = 0xFFFF00
EMBED_COLOUR_CLOSED = 0xFF0000  # red
EMBED_COLOUR_DISCORD = 0x8080FF  # purple
EMBED_COLOUR_ERROR = 0x800000  # dark red
EMBED_COLOUR_EVIL = 0xFF0000
EMBED_COLOUR_EXPIRED = 0x808080  # grey
EMBED_COLOUR_LOADING = 0x00D9FF  # PTN faded blue
EMBED_COLOUR_OK = 0x80FF80  # we're good here thanks, how are you?
EMBED_COLOUR_OPEN = 0x80FFFF  # blue
EMBED_COLOUR_ORANG = 0xFFAB00
EMBED_COLOUR_PTN_DEFAULT = 42971  # used by various embeds throughout the server
EMBED_COLOUR_QU = 0x00D9FF  # que?
EMBED_COLOUR_REDDIT = 0xFF0000  # red
EMBED_COLOUR_RP = 0xE63946  # PTN red
EMBED_COLOUR_STATUS = 0xEE3563
EMBED_COLOUR_UNLOADING = 0x80FF80  # PTN emph blue
EMBED_COLOUR_WARNING = 0xFFD700  # and it was all yellow

############################
### Dicts                ###
############################

any_moderation_role: list[int] = [ROLE_COUNCIL, ROLE_MOD]
any_council_role: list[int] = [ROLE_COUNCIL, ROLE_ADVISOR]
any_elevated_role: list[int] = [
    ROLE_COUNCIL,
    ROLE_MOD,
    ROLE_ALUMNI,
    ROLE_SOMM,
    ROLE_CONN,
    ROLE_FO,
    ROLE_AGENT,
    ROLE_CM,
    ROLE_PILLAR,
    ROLE_CCO,
    ROLE_GRAPE,
    ROLE_PATH,
    ROLE_SPEC,
]
color_roles: list[int] = [
    ROLE_COLOR_ALUMNI,
    ROLE_COLOR_SOMM,
    ROLE_COLOR_CONN,
    ROLE_COLOR_FO,
    ROLE_COLOR_AGENT,
    ROLE_COLOR_CM,
    ROLE_COLOR_PILLAR,
    ROLE_COLOR_CCO,
    ROLE_COLOR_GRAPE,
    ROLE_COLOR_PATH,
    ROLE_COLOR_SPEC,
]

functional_roles: list[int] = [
    ROLE_ALUMNI,
    ROLE_GRAPE,
    ROLE_SOMM,
    ROLE_CONN,
    ROLE_FO,
    ROLE_AGENT,
    ROLE_CM,
    ROLE_PILLAR,
    ROLE_CCO,
    ROLE_PATH,
    ROLE_SPEC,
]

# Mapping of functional roles to color roles
role_to_color: dict[int, int] = {
    ROLE_ALUMNI: ROLE_COLOR_ALUMNI,
    ROLE_GRAPE: ROLE_COLOR_GRAPE,
    ROLE_SOMM: ROLE_COLOR_SOMM,
    ROLE_CONN: ROLE_COLOR_CONN,
    ROLE_FO: ROLE_COLOR_FO,
    ROLE_AGENT: ROLE_COLOR_AGENT,
    ROLE_CM: ROLE_COLOR_CM,
    ROLE_PILLAR: ROLE_COLOR_PILLAR,
    ROLE_CCO: ROLE_COLOR_CCO,
    ROLE_PATH: ROLE_COLOR_PATH,
    ROLE_SPEC: ROLE_COLOR_SPEC,
}
