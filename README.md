# PTN-Library

Common utilities shared between PTN bots.

---

## Contents

- [Installation](#installation)
- [Global Constants](#global-constants)
- [WrappedBot](#wrappedbot)
- [GetOrFetch](#getorfetch)
- [Checks](#checks)
- [ErrorHandler](#errorhandler)
- [ErrorClasses](#errorclasses)
- [Logger](#logger)
- [Pagination](#pagination)
- [BotSettings](#botsettings)

---

## Installation

PTN-Library is not published to PyPI. Install directly from GitHub:

```toml
# pyproject.toml (uv)
[tool.uv.sources]
ptn-utils = { git = "https://github.com/PilotsTradeNetwork/PTN-Library.git", rev = "1.1.0" }
```

### Requirements

- Python 3.11+
- Dependencies: `discord-py>=2.0`, `python-dotenv>=0.15.0`, `loguru>=0.7.3`, `tomli_w>=1.0.0`

---

## Global Constants

`ptn_utils.global_constants` provides Discord guild/channel/role IDs, emoji IDs, embed colours, the bot token, and the data directory path. Values are selected automatically based on the `PTN_SERVICE` environment variable:

- `PTN_SERVICE=False` (default / unset) → dev/testing constants (PANTS test server)
- `PTN_SERVICE=True` → production constants (live PTN server)

The `.env` file at `DATA_DIR/.env` is loaded automatically on import. `DATA_DIR` defaults to `<cwd>/ptn/data` if the environment variable is not set.

```python
from ptn_utils.global_constants import (
    TOKEN,
    DISCORD_GUILD,
    CHANNEL_BOT_COMMANDS,
    ROLE_CCO,
    EMBED_COLOUR_OK,
    EMBED_COLOUR_ERROR,
)
```

### Naming conventions

| Prefix          | Type                    |
| --------------- | ----------------------- |
| `CHANNEL_`      | Channel and thread IDs  |
| `CAT_`          | Category IDs            |
| `ROLE_`         | Role IDs                |
| `EMOJI_`        | Custom emoji IDs        |
| `EMBED_COLOUR_` | Embed colour hex values |

When adding new constants, add matching entries to **both** `dev/` and `prod/` files — a constant missing in one environment will cause a `NameError` at runtime in that environment.

---

## WrappedBot

`ptn_utils.wrapped_bot.WrappedBot` is a `discord.py` `Bot` subclass with three utility objects pre-attached, and safe mention defaults in dev mode.

```python
from discord import Intents
from ptn_utils.wrapped_bot import WrappedBot

bot = WrappedBot(command_prefix="!", intents=Intents.default())

# Available on any WrappedBot instance:
bot.get_or_fetch   # GetOrFetch — cache-then-fetch Discord helpers
bot.checks         # Checks — role/channel decorator factory
bot.error_handler  # ErrorHandler — app-command and background error handler
```

In dev mode (`PTN_SERVICE` unset or `False`), `AllowedMentions.none()` is set automatically to prevent accidental pings during testing.

---

## GetOrFetch

`ptn_utils.get_or_fetch.GetOrFetch` wraps common Discord lookups to try the local cache before making an API call, and returns `None` on failure rather than raising.

```python
from ptn_utils.get_or_fetch import GetOrFetch

get_or_fetch = GetOrFetch(bot, guild_id=DISCORD_GUILD)

# All methods are async and return Optional[T]
channel = await get_or_fetch.channel(CHANNEL_BOT_COMMANDS)
member  = await get_or_fetch.member(user_id)
role    = await get_or_fetch.role(ROLE_CCO)
emoji   = await get_or_fetch.emoji(EMOJI_O7)
```

Available methods: `guild`, `channel`, `member`, `user`, `role`, `emoji`, `sticker`.

---

## Checks

`ptn_utils.helpers.checks.Checks` provides `discord.py` app-command decorators for restricting commands by role, channel, or category.

`Checks` is pre-attached to `WrappedBot` as `bot.checks`, or instantiate it directly with a `GetOrFetch` instance.

```python
# Restrict to specific roles
@bot.checks.roles([ROLE_COUNCIL, ROLE_MOD])
async def admin_command(interaction: discord.Interaction): ...

# Restrict to a specific channel
@bot.checks.command_channel(CHANNEL_BOT_COMMANDS)
async def channel_locked_command(interaction: discord.Interaction): ...

# Restrict by category, granting extra permissions to category-specific roles
# (e.g. Sommelier in the Somm category, Faction Operative in the Faction category)
@bot.checks.category_perms()
async def category_command(interaction: discord.Interaction): ...
```

On failure, these raise `CommandChannelError` or `CommandRoleError`, which `ErrorHandler` catches and turns into user-facing ephemeral messages automatically.

---

## ErrorHandler

`ptn_utils.helpers.error_handling.ErrorHandler` handles errors from slash commands and background tasks, sending formatted embeds to the user and a spam channel.

`ErrorHandler` is pre-attached to `WrappedBot` as `bot.error_handler` and wired up automatically. To use it standalone:

```python
from ptn_utils.helpers.error_handling import ErrorHandler

error_handler = ErrorHandler(get_or_fetch)

# Wire to discord.py's app command error hook
bot.tree.on_error = error_handler.on_app_command_error

# Wire to prefix command errors
bot.add_listener(error_handler.on_generic_error, "on_command_error")

# Call from a background task
await error_handler.on_background_error(BackgroundError("Something went wrong"))
```

Error routing behaviour:

| Exception type        | User message            | Visibility                    |
| --------------------- | ----------------------- | ----------------------------- |
| `GenericError`        | Exception text          | Public                        |
| `CustomError`         | `err.message`           | Controlled by `err.isprivate` |
| `AsyncioTimeoutError` | `err.message`           | Controlled by `err.isprivate` |
| `SilentError`         | None (silent)           | —                             |
| `CommandChannelError` | Permitted channels list | Ephemeral                     |
| `CommandRoleError`    | Permitted roles list    | Ephemeral                     |
| Other                 | Raw error text          | Ephemeral                     |

All errors are also reported to `CHANNEL_BOTSPAM`.

---

## ErrorClasses

`ptn_utils.classes.ErrorClasses` provides the custom exception hierarchy used across all PTN bots.

```python
from ptn_utils.classes.ErrorClasses import (
    CustomError,      # Show a custom message to the user; isprivate controls ephemeral
    GenericError,     # Show the exception text publicly
    SilentError,      # Swallow silently — no user message
    AsyncioTimeoutError,  # Timeout with a custom message
    CommandChannelError,  # Raised by Checks on channel mismatch
    CommandRoleError,     # Raised by Checks on role mismatch
    BackgroundError,  # For interactionless/background task errors
)

# CustomError: private by default
raise CustomError("You don't have permission to do that.")

# CustomError: public
raise CustomError("Mission posted successfully.", isprivate=False)

# GenericError: shows the str(exception) to the user
raise GenericError("Database connection failed")

# BackgroundError: no interaction, goes to spam channel only
raise BackgroundError("WMM sync failed")
```

---

## Logger

`ptn_utils.logger.logger` provides loguru-based structured logging with per-module sink filtering and a Discord slash command to change log levels at runtime.

### Setup

Call `setup_logging()` once at bot startup (it is also called automatically when the module is first imported):

```python
from ptn_utils.logger.logger import setup_logging, get_logger

setup_logging()  # configures loguru, intercepts stdlib logging
logger = get_logger("mybot.module")
```

The log level is controlled by the `PTN_LOG_LEVEL` environment variable (default: `INFO`). Valid values: `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, `TRACE`.

### Getting a logger

```python
from ptn_utils.logger.logger import get_logger

logger = get_logger("mybot.database")

logger.info("Bot started")
logger.debug(f"Loaded {n} carriers")
logger.trace("Very verbose detail")  # loguru-only level below DEBUG
logger.error("Something went wrong")
logger.exception(e)                  # logs traceback
```

Use hierarchical dot-separated names (`mybot.database`, `mybot.commands.mission`) — the `/set_logging_level` command supports prefix filtering on these names.

### Runtime log level command

Add the `Logger` cog to your bot to expose a `/set_logging_level` slash command, restricted to council roles:

```python
from ptn_utils.logger.logger import Logger

await bot.add_cog(Logger())
```

---

## Pagination

`ptn_utils.pagination.pagination.PaginationView` is a `discord.py` `LayoutView` for displaying a list of items across multiple pages, with optional per-item action buttons and a broadcast feature for ephemeral views.

```python
from ptn_utils.pagination.pagination import PaginationView

# content is a list of (title, description) string tuples
content = [("Carrier Alpha", "Loading at Jameson"), ("Carrier Beta", "Unloading at Farseer")]

view = PaginationView(
    title="Active Missions",
    content=content,
    ephemeral=True,       # adds a Broadcast button so the user can share the result
    page_length=10,       # items per page (default: 10)
)
await interaction.response.send_message(view=view, ephemeral=True)
view.message = await interaction.original_response()
```

#### Per-item action buttons

Pass `buttons_text` and `buttons_callback` to add a clickable button next to each item:

```python
async def on_item_click(interaction: discord.Interaction, title: str, index: int):
    await interaction.response.send_message(f"You selected: {title}", ephemeral=True)

view = PaginationView(
    title="Carriers",
    content=content,
    buttons_text="Select {title}",
    buttons_callback=on_item_click,
)
```

The view times out after 60 seconds of inactivity and collapses to a closed message automatically.

---

## BotSettings

`ptn_utils.settings.BotSettings` is a base class for managing a bot's runtime-mutable settings, persisted to a **TOML file**.

### Features

- Declarative field definition via annotated class attributes
- TOML file format (stdlib `tomllib` for reads, `tomli_w` for writes)
- Automatic type coercion on read, including `int | None`, `str | None`, etc.
- `display()` method returns the raw file contents as a string (for sending to Discord, logging, etc.)
- One-time automatic migration from a legacy `key = value` `.txt` file on first boot

### Usage

Subclass `BotSettings` and declare fields as annotated class attributes with defaults. `file_path` is an optional keyword argument to the class definition:

```python
from pathlib import Path
from ptn_utils.settings import BotSettings

# Explicit path
class Settings(BotSettings, file_path=Path("/data/settings/settings.toml")):
    wmm_autostart: bool = False
    commandid_stock: int | None = None
    server_reset_hour: int = 7
    ody_material_cleanup_days: int = 7

# Default path — resolves to {DATA_DIR}/settings/settings.toml at first instantiation
class Settings(BotSettings):
    wmm_autostart: bool = False
    commandid_stock: int | None = None
```

If `file_path` is omitted, the path is resolved **lazily at first instantiation** (not at class definition time) so that `DATA_DIR` from `.env` is already loaded by then. Resolution order:

1. `DATA_DIR` environment variable
2. `<cwd>/ptn/data` (mirrors the fallback in `global_constants`)

The resolved default is always `{DATA_DIR}/settings/settings.toml`.

#### Reading and writing

```python
settings = Settings()   # attributes initialised to declared defaults
settings.read()         # load values from the TOML file; missing file is handled gracefully
settings.write()        # persist current attribute values to the TOML file
```

`read()` only updates attributes whose names are declared as fields on the subclass. Unknown keys present in the file are ignored.

#### Displaying the file contents

```python
content = settings.display()  # returns raw TOML file text as a str
```

If the file does not exist, `display()` returns a descriptive string rather than raising.

#### Mutating a single field

```python
settings.read()
settings.wmm_autostart = True
settings.write()
```

### Type coercion

TOML natively represents `bool`, `int`, `float`, and `str`, so those types round-trip without any special handling.

For optional types (`T | None` / `Optional[T]`), `read()` additionally converts the string sentinel `"None"` (written by `write()` when a value is `None`) back to `None`. This is necessary because TOML has no null type.

| Annotation    | TOML value       | Python result    |
| ------------- | ---------------- | ---------------- |
| `bool`        | `true` / `false` | `True` / `False` |
| `int`         | `7`              | `7`              |
| `int \| None` | `7`              | `7`              |
| `int \| None` | `"None"`         | `None`           |
| `str \| None` | `"some-value"`   | `"some-value"`   |
| `str \| None` | `"None"`         | `None`           |

### Legacy migration

If the TOML file does not exist, `read()` automatically detects and migrates legacy settings files. Two formats are supported, tried in order:

1. **JSON** (`.json` extension) — used by BoozeBot. Values are already native Python types; no string coercion is needed.
2. **key = value** (`.txt` extension) — used by MissionAlertBot. Values are strings and are coerced using the declared field annotations.

In both cases the migration:

1. Parses the legacy file, ignoring unknown keys
2. Writes the migrated values to the new TOML file
3. Deletes the legacy file

This runs exactly once — on the first boot after upgrading — and is transparent to the caller.
