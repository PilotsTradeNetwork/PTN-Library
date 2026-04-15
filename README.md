# PTN-Library

Common utilities shared between PTN Discord bots.

---

## Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Global Constants](#global-constants)
- [WrappedBot](#wrappedbot)
- [GetOrFetch](#getorfetch)
- [Checks (Permission Decorators)](#checks-permission-decorators)
- [Error Handling](#error-handling)
- [Logging](#logging)
- [Pagination](#pagination)

---

## Installation

Always pin a tagged release for reproducible installs:

```toml
# pyproject.toml
[tool.uv.sources]
ptn-utils = { git = "https://github.com/PilotsTradeNetwork/PTN-Library", tag = "1.1.1" }

[project]
dependencies = ["ptn-utils"]
```

To upgrade, change the `tag` value and run `uv sync`. Available releases are on the
[GitHub releases page](https://github.com/PilotsTradeNetwork/PTN-Library/releases).

For local development with a checked-out copy:

```toml
[tool.uv.sources]
ptn-utils = { path = "../PTN-Library", editable = true }
```

---

## Project Structure

Your bot project must follow this layout for the library to locate its data files:

```
your-bot/
└── ptn/
    └── data/
        └── .env
```

The `.env` file is loaded automatically when the constants module is imported.
**Never commit `.env` to version control.**

The data directory is resolved as:
1. The `DATA_DIR` environment variable, if set.
2. `<cwd>/ptn/data/` otherwise.

---

## Environment Variables

### `PTN_SERVICE`

Selects which set of Discord constants (channel/role/emoji IDs) to load.
Must be set before importing anything from `ptn_utils`.

| Value | Effect |
|---|---|
| unset or `False` (default) | Development constants (PANTS test server) |
| `True` | Production constants (live PTN server) |

### `DATA_DIR`

Path to the directory containing the `.env` file. Defaults to `<cwd>/ptn/data/`.

### `.env` contents

```bash
DISCORD_TOKEN_TESTING=...   # used when PTN_SERVICE=False
DISCORD_TOKEN_PROD=...      # used when PTN_SERVICE=True
```

The active token is exposed as `ptn_utils.global_constants.TOKEN`.

### `PTN_LOG_LEVEL`

Initial log level for the default sink. One of `CRITICAL`, `ERROR`, `WARNING`,
`INFO` (default), `DEBUG`, `TRACE`.

---

## Global Constants

All constants are importable from `ptn_utils.global_constants`. The correct
dev or prod values are selected automatically based on `PTN_SERVICE`.

```python
from ptn_utils.global_constants import (
    TOKEN,           # Discord bot token (from .env)
    DISCORD_GUILD,   # Guild ID for the active environment
    guild_obj,       # discord.Object wrapping DISCORD_GUILD

    CHANNEL_BOTSPAM,
    ROLE_CCO,
    EMBED_COLOUR_OK,
    EMOJI_O7,

    # Pre-built role lists
    any_moderation_role,   # [ROLE_COUNCIL, ROLE_MOD]
    any_council_role,      # [ROLE_COUNCIL, ROLE_ADVISOR]
    any_elevated_role,     # council + mod + all functional roles
    functional_roles,
    color_roles,
    role_to_color,         # dict[int, int] — functional role → colour role
)
```

The full lists of available channel, role, and emoji constants are in
`ptn_utils/global_constants/dev/` (mirrored in `prod/`).

### Adding new constants

Always add to **both** `dev/` and `prod/`. Follow the naming conventions:

| What | Prefix | File |
|---|---|---|
| Category | `CAT_` | `channels.py` |
| Channel / thread | `CHANNEL_` / `THREAD_` | `channels.py` |
| Role | `ROLE_` | `roles.py` |
| Emoji | `EMOJI_` | `generic.py` |

Update the role-group lists in `global_constants/__init__.py` if a new role
belongs in `any_elevated_role`, `functional_roles`, `color_roles`, or
`role_to_color`.

---

## WrappedBot

A drop-in replacement for `discord.ext.commands.Bot` that pre-wires
`GetOrFetch`, `Checks`, and `ErrorHandler`. In non-production mode it also
sets `AllowedMentions.none()` by default to prevent accidental pings.

```python
import discord
from ptn_utils.wrapped_bot import WrappedBot
from ptn_utils.global_constants import TOKEN, guild_obj

bot = WrappedBot(command_prefix="!", intents=discord.Intents.default())

@bot.event
async def on_ready():
    await bot.tree.sync(guild=guild_obj)

bot.run(TOKEN)
```

After construction the bot exposes:

| Attribute | Type | Description |
|---|---|---|
| `bot.get_or_fetch` | `GetOrFetch` | Guild resource fetcher |
| `bot.checks` | `Checks` | Permission decorators |
| `bot.error_handler` | `ErrorHandler` | Error handler |

---

## GetOrFetch

Wraps Discord's cache (`get_*`) / API (`fetch_*`) calls into a single
awaitable. Tries the cache first, falls back to the API.

Use `bot.get_or_fetch` when working with a `WrappedBot`, or construct directly:

```python
from ptn_utils.get_or_fetch import GetOrFetch
gof = GetOrFetch(bot, guild_id=DISCORD_GUILD)
```

All methods are `async` and return `None` on error (except `guild()`, which raises):

```python
await gof.guild(guild_id)       # -> Guild  (raises on failure)
await gof.channel(channel_id)   # -> GuildChannel | Thread | None
await gof.member(user_id)       # -> Member | None
await gof.user(user_id)         # -> User | None
await gof.role(role_id)         # -> Role | None
await gof.emoji(emoji_id)       # -> Emoji | None
await gof.sticker(sticker_id)   # -> GuildSticker | None
```

---

## Checks (Permission Decorators)

`Checks` provides `@app_commands.check`-compatible decorators. Access them
via `bot.checks` or construct a standalone instance:

```python
from ptn_utils.helpers.checks import Checks
checks = Checks(GetOrFetch(bot, DISCORD_GUILD))
```

### `checks.roles(permitted_role_id)`

Restricts a command to users holding at least one of the given roles.

```python
@bot.tree.command()
@bot.checks.roles(ROLE_CCO)                  # single role
async def my_command(interaction): ...

@bot.tree.command()
@bot.checks.roles(any_moderation_role)       # pre-built list
async def mod_only(interaction): ...
```

### `checks.command_channel(permitted_channel_id)`

Restricts a command to one or more channels.

```python
@bot.tree.command()
@bot.checks.command_channel(CHANNEL_BOT_COMMANDS)
async def my_command(interaction): ...
```

### `checks.category_perms()`

Grants permission based on the category the command is run in, adding a
role-specific override on top of the base moderation roles:

| Category | Extra permitted role |
|---|---|
| `CAT_CT` | `ROLE_CM` |
| `CAT_SOMM` | `ROLE_SOMM` |
| `CAT_FACTION` | `ROLE_FO` |
| `CAT_SC` | `ROLE_PATH` |

> **Note:** `category_perms()` and `roles()` are independent — if both are
> applied to the same command, **both** must pass.

---

## Error Handling

### Exception classes

```python
from ptn_utils.classes.error_classes import (
    CustomError,         # show a custom message to the user (hides traceback)
    GenericError,        # show the raw exception string publicly
    SilentError,         # suppress all user-facing output; log only
    AsyncioTimeoutError, # report a timeout to the user
    BackgroundError,     # for errors in tasks with no Interaction context
)
```

| Exception | User sees | `isprivate` param |
|---|---|---|
| `CustomError(msg)` | `msg` as an ephemeral embed | yes (default `True`) |
| `CustomError(msg, isprivate=False)` | `msg` publicly | no |
| `GenericError(msg)` | raw exception string | — |
| `SilentError()` | nothing | — |
| `AsyncioTimeoutError(msg)` | timeout embed | yes (default `True`) |
| `BackgroundError(msg)` | warning in `CHANNEL_BOTSPAM` | — |

All types (except `BackgroundError`) also post a summary to `CHANNEL_BOTSPAM`.

### Usage

```python
@bot.tree.command()
async def my_command(interaction):
    if not valid:
        raise CustomError("That isn't valid here.")
    if should_be_silent:
        raise SilentError
```

For background tasks:

```python
await bot.error_handler.on_background_error(BackgroundError("task failed"))
```

---

## Logging

Built on [loguru](https://github.com/Delgan/loguru) with a stdlib bridge.
Initialised automatically on first import — no setup call needed.

```python
from ptn_utils.logger.logger import get_logger

logger = get_logger("mybot.commands.trade")
logger.info("Ready")
logger.debug("Detail")
logger.trace("Very verbose")
```

Use hierarchical dotted names so the `/set_logging_level` command can target
individual subsystems at runtime.

### `Logger` cog

Add the cog to expose `/set_logging_level` in Discord (restricted to
`ROLE_COUNCIL` / `ROLE_ADVISOR`):

```python
from ptn_utils.logger.logger import Logger as LoggerCog
await bot.add_cog(LoggerCog())
```

The command accepts an optional `logger_name` for per-subsystem control.
Setting no name resets all per-module overrides.

---

## Pagination

`PaginationView` renders a paginated list using Discord's Components V2 UI.
Requires **discord.py 2.6+**. Content is a list of `(title, detail)` tuples.

```python
from ptn_utils.pagination.pagination import PaginationView

@bot.tree.command()
async def list_things(interaction):
    view = PaginationView(
        title="Things",
        content=[("Item One", "detail"), ("Item Two", "detail")],
        ephemeral=True,   # adds a "Broadcast" button
        page_length=10,   # default
    )
    await interaction.response.send_message(view=view, ephemeral=True)
    view.message = await interaction.original_response()
```

To add a clickable button on each row, pass `buttons_text` (a format string
accepting `{title}` and `{info}`) and a `buttons_callback`:

```python
async def on_select(interaction, title: str, index: int):
    await interaction.response.send_message(f"Selected: {title}", ephemeral=True)

view = PaginationView(
    title="Carriers",
    content=[("Carrier Alpha", "Jameson"), ("Carrier Beta", "In transit")],
    ephemeral=True,
    buttons_text="Select {title}",
    buttons_callback=on_select,
)
```

- Times out after **60 seconds** of inactivity.
- Only the invoking user can interact with the view.
- "Broadcast" re-sends the current page publicly with buttons disabled.