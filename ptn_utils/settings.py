from __future__ import annotations

import json
import os
import tomllib
from pathlib import Path
from typing import Any, Union, get_args, get_origin

import tomli_w
from loguru import logger


class BotSettings:
    _file_path: Path
    _fields: dict[str, Any]

    def __init_subclass__(cls, file_path: Path | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # None means "resolve at instantiation time via _default_file_path()"
        cls._file_path = file_path  # type: ignore[assignment]

        fields: dict[str, Any] = {}
        for name in cls.__annotations__:
            if name.startswith("_"):
                continue
            if hasattr(cls, name):
                fields[name] = getattr(cls, name)
            else:
                fields[name] = None
        cls._fields = fields

    def __init__(self) -> None:
        # Resolve the default path lazily so DATA_DIR is already set by the
        # time the first instance is created.
        if self._file_path is None:
            self._file_path = _default_file_path()
        for name, default in self._fields.items():
            setattr(self, name, default)

    def read(self) -> None:
        try:
            with open(self._file_path, "rb") as f:
                data = tomllib.load(f)
        except FileNotFoundError:
            if self._migrate_legacy_file():
                return
            logger.debug(f"Settings file not found at {self._file_path}, using defaults.")
            return

        for key, value in data.items():
            if key not in self._fields:
                logger.debug(f"Ignoring unknown key '{key}' from {self._file_path}")
                continue
            coerced = self._coerce_value(key, value)
            setattr(self, key, coerced)
            logger.debug(f"Settings read: {key} = {coerced!r}")

    def write(self) -> None:
        payload: dict[str, Any] = {}
        for key in self._fields:
            val = getattr(self, key)
            if val is None:
                # tomli_w does not support None; store as string sentinel
                payload[key] = "None"
            else:
                payload[key] = val

        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._file_path, "wb") as f:
            tomli_w.dump(payload, f)
        logger.debug(f"Settings written to {self._file_path}: {payload}")

    def display(self) -> str:
        try:
            return self._file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return f"Settings file not found at {self._file_path}"

    def _coerce_value(self, name: str, value: Any) -> Any:
        annotations = {}
        for cls in type(self).__mro__:
            if "__annotations__" in cls.__dict__:
                for k, v in cls.__annotations__.items():
                    if k not in annotations:
                        annotations[k] = v

        annotation = annotations.get(name)
        if annotation is None:
            return value

        # Resolve string annotations if needed
        if isinstance(annotation, str):
            return value

        origin = get_origin(annotation)
        args = get_args(annotation)

        # Handle Union types (e.g. str | None, int | None, Optional[str])
        is_optional = origin is Union and type(None) in args
        if is_optional:
            non_none_args = [a for a in args if a is not type(None)]

            # Convert "None" / "none" string to actual None
            if isinstance(value, str) and value.lower() == "none":
                return None

            if non_none_args:
                inner_type = non_none_args[0]
                if inner_type is int:
                    return int(value)
                if inner_type is float:
                    return float(value)
                if inner_type is str:
                    return str(value)
                if inner_type is bool:
                    return bool(value)
            return value

        # Plain types — TOML already provides native bool/int/float/str
        return value

    def _migrate_legacy_file(self) -> bool:
        """
        Look for a legacy settings file next to the TOML path and migrate it.

        Two legacy formats are supported, tried in order:

        1. **JSON** (``.json`` extension) — used by BoozeBot. Values are
           already native Python types so no string coercion is needed.
        2. **key = value** (``.txt`` extension) — used by MissionAlertBot.
           All values are strings and are coerced via the declared annotations.

        On success, writes the TOML file, deletes the legacy file, and returns
        True. Returns False if neither legacy file exists.
        """
        for legacy_path, parser in (
            (self._file_path.with_suffix(".json"), self._parse_legacy_json),
            (self._file_path.with_suffix(".txt"), self._parse_legacy_txt),
        ):
            if legacy_path.exists():
                logger.info(f"Migrating legacy settings file {legacy_path} -> {self._file_path}")
                data = parser(legacy_path)
                for key, value in data.items():
                    setattr(self, key, value)
                self.write()
                legacy_path.unlink()
                logger.info(f"Migration complete. Legacy file {legacy_path} removed.")
                return True

        return False

    def _parse_legacy_json(self, path: Path) -> dict[str, Any]:
        """Parse a JSON legacy settings file. Values are already native types."""
        try:
            raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Migration: failed to parse JSON file {path}: {e}")
            return {}

        data: dict[str, Any] = {}
        for key, value in raw.items():
            if key not in self._fields:
                logger.debug(f"Migration: ignoring unknown key '{key}'")
                continue
            data[key] = value
            logger.debug(f"Migration: {key} = {value!r}")
        return data

    def _parse_legacy_txt(self, path: Path) -> dict[str, Any]:
        """Parse a key = value legacy settings file. Values are coerced via annotations."""
        data: dict[str, Any] = {}
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                key, _, raw_value = line.partition("=")
                key = key.strip()
                raw_value = raw_value.strip()
                if key not in self._fields:
                    logger.debug(f"Migration: ignoring unknown key '{key}'")
                    continue
                coerced = self._coerce_value(key, raw_value)
                data[key] = coerced
                logger.debug(f"Migration: {key} = {coerced!r}")
        return data


def _default_file_path() -> Path:
    """
    Resolve the default settings file path at call time (not import time), so
    that DATA_DIR reflects any .env already loaded by global_constants.
    Resolution order:
      1. DATA_DIR environment variable
      2. <cwd>/ptn/data  (mirrors the fallback in global_constants)
    """
    data_dir = os.getenv("DATA_DIR", os.path.join(os.getcwd(), "ptn", "data"))
    return Path(data_dir) / "settings" / "settings.toml"
