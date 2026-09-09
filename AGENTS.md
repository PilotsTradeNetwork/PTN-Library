# PTN-Library – Agent Onboarding Guide

Trust these instructions first. Only search the codebase if information here is incomplete or appears incorrect.

---

## What This Repository Does

PTN-Library (`ptn-utils`) is a shared Python library consumed by multiple PTN Discord bots (MissionAlertBot, BoozeBot, and others). It provides:

- **Global constants** — Discord guild/channel/role IDs, emoji IDs, embed colours, the bot token, and data path resolution. Values are selected automatically based on the `PTN_SERVICE` environment variable (dev vs. prod split).
- **BotSettings** — a base class for file-backed, runtime-mutable bot settings persisted as TOML.
- **WrappedBot** — a `discord.py` `Bot` subclass pre-wired with `GetOrFetch`, `Checks`, and `ErrorHandler`.
- **GetOrFetch** — helpers that try the local cache before falling back to a Discord API fetch.
- **Checks** — `discord.py` app-command decorators for role and channel enforcement.
- **ErrorHandler** — global app-command and background error handlers.
- **Logger** — loguru-based logging setup with per-sink filtering and a `/set_logging_level` slash command.
- **Pagination** — a `discord.py` `LayoutView` for paginated embeds.
- **ErrorClasses** — custom exception hierarchy (`CustomError`, `GenericError`, `CommandRoleError`, etc.).
- **Enums** — shared enumerations (e.g. `CruiseSystemState`).

---

## Repository Facts

- **Type:** Pure Python library (not a runnable bot)
- **Size:** ~15 source files, ~1 500 lines
- **Python:** `>=3.11`
- **Package manager:** `setuptools` + `setuptools_scm` (version from git tags). No `uv.lock` — this is a library, not an application.
- **Build backend:** `setuptools.build_meta`
- **Published to:** Not PyPI. Installed by consumer bots via a git source, e.g. `{ git = "https://github.com/PilotsTradeNetwork/PTN-Library.git", rev = "1.1.0" }`.
- **CI/CD:** None. There is no `.github/` directory, no Actions workflow, and no CI pipeline of any kind.
- **Linting/formatting:** No `ruff`, `pyright`, or `pre-commit` configuration exists in this repository. There are no pre-commit hooks.
- **Tests:** None. There is no test suite and `pytest` is not a dependency. Do not attempt to run tests.

---

## No Build or Validation Steps

Because there is no CI, no linter config, and no test suite, there is nothing to "run" to validate changes. The only validation is:

1. **Import check** — the library must be importable without errors.
2. **Consumer bots** — changes are validated when a consumer bot (e.g. MissionAlertBot) installs the library and runs.

If you want to verify a change doesn't break imports, you can do:

```sh
python -c "import ptn_utils"
```

This requires the library's dependencies to be installed (`discord-py`, `python-dotenv`, `loguru`, `tomli_w`).

---

## Dev/Prod Split

`PTN_SERVICE` environment variable controls which constants are loaded:

- **Unset or `False`** (default) → `ptn_utils/global_constants/dev/` (PANTS test server IDs)
- **`True`** → `ptn_utils/global_constants/prod/` (live PTN server IDs)

This is resolved in `ptn_utils/global_constants/__init__.py` using `ast.literal_eval(os.environ.get("PTN_SERVICE", "False"))`. Always leave `PTN_SERVICE` unset for local development.

---

## Secrets and Credentials

- The Discord bot token is read from a `.env` file loaded by `python-dotenv` at import time in `global_constants/dev/generic.py` and `prod/generic.py`.
- Dev token env var: `DISCORD_TOKEN_TESTING`
- Prod token env var: `DISCORD_TOKEN_PROD`
- The `.env` file must live at `DATA_DIR/.env`. `DATA_DIR` defaults to `<cwd>/ptn/data` if the env var is not set.
- **Never hardcode tokens or secrets.** Always follow the `.env` pattern.

---

## Project Layout

```
PTN-Library/
├── pyproject.toml                        # Package metadata, deps, build config
├── README.md                             # User-facing documentation
├── .gitignore                            # Standard Python gitignore
├── .gitattributes
└── ptn_utils/
    ├── __init__.py                       # Empty
    ├── settings.py                       # BotSettings base class (TOML-backed runtime settings)
    ├── wrapped_bot.py                    # WrappedBot: discord.py Bot subclass
    ├── get_or_fetch.py                   # GetOrFetch: cache-then-fetch Discord helpers
    ├── global_constants/
    │   ├── __init__.py                   # Dev/prod selector; star-imports chosen subpackage
    │   ├── dev/
    │   │   ├── __init__.py               # Star-imports channels, generic, roles
    │   │   ├── channels.py               # Dev channel/category/thread IDs + reddit config
    │   │   ├── generic.py                # Dev token, guild ID, emoji IDs, data path
    │   │   └── roles.py                  # Dev role IDs
    │   └── prod/
    │       ├── __init__.py               # Star-imports channels, generic, roles
    │       ├── channels.py               # Prod channel/category/thread IDs + reddit config
    │       ├── generic.py                # Prod token, guild ID, emoji IDs, data path
    │       └── roles.py                  # Prod role IDs
    ├── helpers/
    │   ├── __init__.py
    │   ├── checks.py                     # Checks class: role/channel/category decorators
    │   └── error_handling.py             # ErrorHandler class: app/background error handlers
    ├── logger/
    │   ├── __init__.py
    │   ├── logger.py                     # Loguru setup, get_logger(), Logger cog, log level command
    │   └── InterceptHandler.py           # stdlib logging → loguru bridge
    ├── classes/
    │   ├── __init__.py
    │   └── ErrorClasses.py               # Custom exception classes
    ├── enums/
    │   ├── __init__.py
    │   └── booze_enums.py                # CruiseSystemState enum
    └── pagination/
        └── pagination.py                 # PaginationView (discord.py LayoutView)
```

---

## Module Dependency Order

There is no enforced import order in this library, but the internal dependency graph is:

```
global_constants   (no internal deps)
logger             → global_constants
classes            (no internal deps)
get_or_fetch       (no internal deps — only discord.py)
helpers/checks     → get_or_fetch, global_constants, logger, classes
helpers/error_handling → get_or_fetch, global_constants, logger, classes
wrapped_bot        → get_or_fetch, helpers/checks, helpers/error_handling, global_constants
settings           (no internal deps — only stdlib + tomli_w + loguru)
pagination         → logger
```

**Do not import `wrapped_bot` or `helpers/*` from within `global_constants`, `logger`, `classes`, or `settings`** — that would create circular imports.

---

## Dependencies

Declared in `pyproject.toml`:

| Package         | Version constraint | Purpose                                                    |
| --------------- | ------------------ | ---------------------------------------------------------- |
| `discord-py`    | `>=2.0`            | Discord API client                                         |
| `python-dotenv` | `>=0.15.0`         | `.env` file loading                                        |
| `loguru`        | `>=0.7.3`          | Structured logging                                         |
| `tomli_w`       | `>=1.0.0`          | Writing TOML files (`tomllib` for reading is stdlib ≥3.11) |

No private or non-PyPI dependencies — this library itself is the non-PyPI dep consumed by bots.

---

## Key Modules in Detail

### `ptn_utils/settings.py` — BotSettings

A base class for runtime-mutable settings persisted to a TOML file. Consumer bots subclass it:

```python
from pathlib import Path
from ptn_utils.settings import BotSettings

class Settings(BotSettings, file_path=Path("/data/settings/settings.toml")):
    wmm_autostart: bool = False
    commandid_stock: int | None = None
    server_reset_hour: int = 7
```

- Fields are declared as annotated class attributes with defaults.
- `file_path` is an optional keyword argument to the class definition (via `__init_subclass__`). If omitted, it defaults to `{DATA_DIR}/settings/settings.toml` resolved at first instantiation (so `DATA_DIR` from `.env` is already loaded by then).
- `settings.read()` — loads TOML into instance attributes; handles missing file gracefully; ignores unknown keys.
- `settings.write()` — serialises all declared fields to TOML. `None` values are written as the string `"None"` (TOML has no null type) and converted back on read.
- `settings.display()` — returns raw file contents as a string; returns a descriptive message if the file is absent.
- **Legacy migration:** if the TOML file is absent, `read()` automatically detects and migrates legacy files. Two formats are supported, tried in order:
    1. **`.json`** (same stem) — used by BoozeBot. Values are already native Python types; no string coercion is needed.
    2. **`.txt`** (same stem) — used by MissionAlertBot. `key = value` lines; values are coerced via the declared annotations.
       Whichever is found first is parsed, written to TOML, and deleted. Runs once, transparently.

### `ptn_utils/global_constants/__init__.py` — Constants

Star-imports everything from either `dev/` or `prod/` subpackage. The `F403`/`F405` noqa comments are intentional — do not remove them.

### `ptn_utils/logger/logger.py` — Logging

Call `get_logger("bot.module")` to get a bound loguru logger. Call `setup_logging()` once at startup. The `Logger` cog provides a `/set_logging_level` slash command. Logging level is controlled by the `PTN_LOG_LEVEL` env var (default: `INFO`).

### `ptn_utils/wrapped_bot.py` — WrappedBot

Subclass `discord.py`'s `Bot` with three attributes pre-attached: `bot.get_or_fetch`, `bot.checks`, `bot.error_handler`. In dev mode (`_production=False`), `AllowedMentions.none()` is set by default to prevent accidental pings.

---

## Adding a New Module

1. Create `ptn_utils/your_module.py`.
2. Follow the dependency order above — only import from modules lower in the graph.
3. Use `from ptn_utils.logger.logger import get_logger` for logging.
4. There is no `__all__` enforcement — public symbols are whatever you define at module level.
5. No registration step is needed; consumers import directly.

## Adding Constants

- Add dev values to `ptn_utils/global_constants/dev/channels.py`, `roles.py`, or `generic.py`.
- Add the matching prod values to the corresponding `prod/` file.
- Follow the naming conventions: `CHANNEL_` prefix for channels, `ROLE_` prefix for roles, `CAT_` for categories, `EMOJI_` for emoji.
- Both files must be kept in sync — a constant missing in one environment will cause a `NameError` at runtime in that environment.
