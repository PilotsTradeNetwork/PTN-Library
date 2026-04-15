# AGENTS.md — Onboarding Guide for AI Coding Agents

Trust the instructions in this file. Only perform additional exploration if you
find information here to be incomplete or incorrect for the specific change you
are making.

---

## What This Repository Does

PTN-Library is a **shared Python utility library** consumed by multiple Discord
bots in the Pilots Trade Network (PTN) ecosystem. It is published as the
installable package `PTN-Utils` (import root `ptn_utils`) and provides:

- `GetOrFetch` — async helpers that wrap Discord's `.get_*` / `.fetch_*` calls.
- `WrappedBot` — a `discord.ext.commands.Bot` subclass that pre-wires
  `GetOrFetch`, `Checks`, and `ErrorHandler`.
- `Checks` — role, channel, and category-based permission decorators for slash
  commands.
- `ErrorHandler` — global error handler for slash commands, text commands, and
  background tasks.
- Custom exception hierarchy (`ErrorClasses`).
- Loguru-based structured logging with per-module sink control and a Discord
  slash command (`Logger` cog) to change log levels at runtime.
- `PaginationView` — a `discord.ui.LayoutView`-based paginated list UI.
- Shared Discord constants (channel IDs, role IDs, emoji IDs, embed colours)
  split into `dev/` and `prod/` namespaces selected via `PTN_SERVICE`.
- `CruiseSystemState` enum used by the Booze Cruise sub-system.

---

## Project At a Glance

| Property | Value |
|---|---|
| Language | Python `>=3.10` |
| Package manager | `uv` |
| Package name | `PTN-Utils` (pip), import root `ptn_utils` |
| Runtime deps | `discord-py>=2.0`, `python-dotenv>=0.15.0`, `loguru>=0.7.3` |
| Build backend | `setuptools` + `setuptools_scm` (version derived from git tags) |
| Linter/formatter | `ruff` — config in `pyproject.toml` under `[tool.ruff]` |
| Type checker (primary) | `ty` — configured under `[tool.ty.environment]` |
| Type checker (secondary) | `basedpyright` — configured under `[tool.basedpyright]` |
| Test suite | **None** — `pytest` is not a dependency; do not run tests |
| CI pipeline | **None** — no `.github/` directory, no automated checks on push |
| Pre-commit hooks | **None** |
| Line length | 120 characters |
| Target Python (ruff/ty) | `py313` / `3.13` |

---

## Repository Layout

```
PTN-Library/
├── ptn_utils/                       # Main source package
│   ├── __init__.py                  # Empty; package marker
│   ├── get_or_fetch.py              # GetOrFetch — async guild resource helpers
│   ├── wrapped_bot.py               # WrappedBot — pre-wired Bot subclass
│   ├── classes/
│   │   └── ErrorClasses.py          # Custom exception hierarchy
│   ├── enums/
│   │   ├── __init__.py              # Re-exports CruiseSystemState
│   │   └── booze_enums.py           # CruiseSystemState enum
│   ├── global_constants/
│   │   ├── __init__.py              # Switches dev/ vs prod/ via PTN_SERVICE
│   │   ├── dev/                     # Test-server constants (PANTS guild)
│   │   │   ├── __init__.py          # Star-imports channels, generic, roles
│   │   │   ├── channels.py          # CAT_*, CHANNEL_*, THREAD_* IDs (PANTS)
│   │   │   ├── generic.py           # TOKEN, DISCORD_GUILD, EMOJI_*, DATA_DIR
│   │   │   └── roles.py             # ROLE_* IDs (PANTS)
│   │   └── prod/                    # Live-server constants (PTN guild)
│   │       ├── __init__.py          # Star-imports channels, generic, roles
│   │       ├── channels.py          # CAT_*, CHANNEL_*, THREAD_* IDs (PTN)
│   │       ├── generic.py           # TOKEN, DISCORD_GUILD, EMOJI_*, DATA_DIR
│   │       └── roles.py             # ROLE_* IDs (PTN)
│   ├── helpers/
│   │   ├── checks.py                # Checks — permission decorators
│   │   └── error_handling.py        # ErrorHandler
│   ├── logger/
│   │   ├── intercept_handler.py     # stdlib logging → loguru bridge
│   │   └── logger.py                # setup_logging(), get_logger(), Logger cog
│   └── pagination/
│       └── pagination.py            # PaginationView
├── README.md                        # One-liner description
├── pyproject.toml                   # Build config, deps, ruff/ty/basedpyright config
└── uv.lock                          # Locked dependency graph (commit changes)
```

`PTN_Utils.egg-info/` and `build/` are generated artifacts — do not edit them.

---

## Environment & Secrets

The `dev/` vs `prod/` constant sub-package is selected at import time by:

| Variable | Effect |
|---|---|
| `PTN_SERVICE=False` (default/unset) | Loads `global_constants/dev/` — PANTS test server |
| `PTN_SERVICE=True` | Loads `global_constants/prod/` — live PTN server |

The Discord bot token is read from a `.env` file in the directory pointed to by
`DATA_DIR` (defaults to `<cwd>/ptn/data/`). The file must contain
`DISCORD_TOKEN_TESTING` (dev) or `DISCORD_TOKEN_PROD` (prod).

**Never hardcode secrets.** Always follow the existing `os.getenv()` +
`load_dotenv()` pattern found in `global_constants/dev/generic.py` and
`global_constants/prod/generic.py`.

Always keep `PTN_SERVICE` unset (or `False`) for local development.

---

## Bootstrap

Always run `uv sync` before linting, type-checking, or building:

```bash
uv sync
```

This installs all runtime dependencies into `.venv` and builds `ptn-utils` in
editable mode. Re-run after any change to `pyproject.toml` or `uv.lock`.

There are no optional extras or dev dependency groups.

---

## Linting & Formatting

Ruff is configured in `pyproject.toml` under `[tool.ruff]` and `[tool.ruff.lint]`:

- **Line length**: 120
- **Target Python**: `py313`
- **Selected rule sets**: `E`, `W`, `F`, `PL`, `I`, `N`, `RUF`, `B`, `C4`,
  `A`, `UP`, `S`, `EXE`, `FA`, `ICN`, `LOG`, `PIE`, `RSE`, `SIM`, `TC`,
  `PERF`, `FURB`, `RET`, `ARG`, `FIX`, `DTZ`, `PTH`, `BLE`, `C90`
- **Ignored rules**: `E501` (line length handled by formatter), `S101` (assert
  used intentionally for type narrowing)

```bash
uv run ruff format .          # auto-format all files (always run before committing)
uv run ruff format --check .  # check formatting without writing
uv run ruff check .           # check for lint errors
uv run ruff check --fix .     # auto-fix fixable lint issues
```

Both `ruff check .` and `ruff format --check .` must pass cleanly before
submitting changes. Always run `uv run ruff format .` on any files you touch.

---

## Type Checking

Two type checkers are configured. `ty` is the primary check and must pass
cleanly. `basedpyright` has a large number of pre-existing errors (mostly due
to the star-import pattern in `global_constants/` and untyped loguru internals)
and is **not expected to be clean**.

```bash
uv run ty check           # must pass with zero errors
uv run basedpyright       # informational only — pre-existing errors are expected
```

`ty` is configured via `[tool.ty.environment]` in `pyproject.toml`:
- `python-version = "3.13"`

`basedpyright` is configured via `[tool.basedpyright]` in `pyproject.toml`:
- `include = ["ptn_utils"]`
- `reportAny = "information"`
- `reportUnusedCallResult = false`
- `reportMissingTypeStubs = false`

The bulk of `basedpyright` errors are `reportUnboundVariable` in
`global_constants/__init__.py` caused by the conditional star-import pattern —
these are intentional and pre-existing. Do not attempt to fix them.

---

## Building a Distribution

```bash
uv build
```

This succeeds with harmless `SetuptoolsDeprecationWarning` messages about the
`project.license` table format and a `listing git files failed` note when run
outside a git context. Neither indicates a failure.

---

## Tests

There is **no test suite**. `pytest` is not installed. Do not attempt to run
tests.

---

## CI / GitHub Actions

There is **no CI pipeline**. There is no `.github/` directory. No automated
checks run on push or pull request. You are solely responsible for ensuring
`ruff format --check .`, `ruff check .`, and `ty check` all pass before
submitting changes.

---

## Module Dependency Rules

Import direction within the library (no cycles permitted):

```
pagination/       →  logger/
helpers/          →  logger/, classes/, global_constants/, get_or_fetch
wrapped_bot       →  get_or_fetch, helpers/, global_constants/
logger/logger.py  →  global_constants/   (imports any_council_role)
global_constants/ →  (no internal ptn_utils imports)
classes/          →  (no internal ptn_utils imports)
enums/            →  (no internal ptn_utils imports)
```

Critical rules to preserve:

- **`global_constants/__init__.py`** uses a conditional star-import (`from
  ptn_utils.global_constants.dev import *` or `prod`) at module load time based
  on `PTN_SERVICE`. The `# ruff: noqa: F403` and `# ruff: noqa: F405`
  suppressions at the top of that file are required. Do not refactor this
  pattern.
- **`global_constants/dev/__init__.py`** and **`global_constants/prod/__init__.py`**
  also use star-imports from their sub-modules. Same suppressions apply.
- **`logger/logger.py`** calls `setup_logging()` at module import time. This is
  intentional — any module calling `get_logger()` triggers log setup
  automatically.

---

## Adding New Constants

Add to **both** `dev/` and `prod/` sub-packages. Naming conventions (enforced
by comments in each file):

- Categories: `CAT_` prefix → `channels.py`
- Channels/threads: `CHANNEL_` / `THREAD_` prefix → `channels.py`
- Roles: `ROLE_` prefix → `roles.py`
- Emoji, tokens, generic IDs: `EMOJI_` prefix or descriptive name → `generic.py`

The top-level `global_constants/__init__.py` also defines shared lists
(`any_moderation_role`, `any_elevated_role`, `role_to_color`, etc.) that
reference role constants — update these if you add new roles that belong in
them.

---

## Validated Command Sequence

The following sequence has been validated and works correctly:

```bash
uv sync                       # install/update all dependencies
uv run ruff format .          # apply formatting
uv run ruff check .           # verify lint — must show "All checks passed!"
uv run ty check               # verify types — must show "All checks passed!"
uv run python -c "import ptn_utils; print('ok')"  # smoke-test import
```
