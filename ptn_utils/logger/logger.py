from __future__ import annotations
import logging
import os
from enum import Enum
from sys import stdout
from typing import List

from discord import Interaction, app_commands
from discord.app_commands import autocomplete
from discord.ext import commands
import loguru

from ptn_utils.global_constants import any_council_role
from ptn_utils.logger.InterceptHandler import InterceptHandler

LOG_SINKS: dict[str, int] = {}

# Global registry of all logger names across all PTN bots
LOGGER_NAMES: set[str] = set()


def get_logger(logger_name: str, **extra_context):
    """
    Get a bound logger and register the name for autocomplete.

    Args:
        logger_name: Hierarchical logger name (e.g., 'boozebot.database')
        **extra_context: Additional context to bind to the logger

    Returns:
        Bound logger instance
    """
    LOGGER_NAMES.add(logger_name)
    return loguru.logger.bind(logger_name=logger_name, **extra_context)


logger = get_logger("ptnlogger")


def clear_logger_registry():
    """Clear the logger registry (useful for testing)."""
    LOGGER_NAMES.clear()


def get_registered_loggers() -> list[str]:
    """Get all registered logger names (useful for debugging)."""
    return sorted(LOGGER_NAMES)


def create_default_logger_sink(level: str) -> None:
    if "_default" in LOG_SINKS:
        logger.remove(LOG_SINKS["_default"])

    def filter_function(record: loguru.Record) -> bool:
        record_logger_name = record["extra"].get("logger_name", []).split(".")
        for logger_name in LOG_SINKS:
            if logger_name == "_default":
                continue
            logger_name_list = logger_name.split(".")
            if len(record_logger_name) >= len(logger_name_list):
                if record_logger_name[: len(logger_name_list)] == logger_name_list:
                    return False
        return True

    sink_id = loguru.logger.add(
        stdout,
        level=level,
        filter=filter_function,
    )
    LOG_SINKS["_default"] = sink_id


def create_logger_sink(logger_name: str, level: str) -> None:
    if logger_name in LOG_SINKS:
        logger.remove(LOG_SINKS[logger_name])

    def filter_function(record: loguru.Record) -> bool:
        record_logger_name = record["extra"].get("logger_name", []).split(".")
        logger_name_list = logger_name.split(".")
        if len(record_logger_name) >= len(logger_name_list):
            return record_logger_name[: len(logger_name_list)] == logger_name_list
        return False

    sink_id = loguru.logger.add(
        stdout,
        level=level,
        filter=filter_function,
    )
    LOG_SINKS[logger_name] = sink_id


def setup_logging() -> None:
    logger.info("Setting up logging configuration.")

    # Send all logging through loguru
    log_handler = InterceptHandler()
    logging.root.handlers = [log_handler]
    logging.root.setLevel(logging.DEBUG)

    # Set default logging level from environment variable or INFO
    loglevel_input = os.getenv("PTN_LOG_LEVEL")
    if not loglevel_input:
        loglevel_input = "INFO"
    try:
        LogLevels(loglevel_input)
    except ValueError:
        loglevel_input = "INFO"
    logger.remove()
    create_default_logger_sink(loglevel_input)

    logger.info(f"Logging level set to {loglevel_input}.")


class LogLevels(Enum):
    Critical = "CRITICAL"
    Error = "ERROR"
    Warning = "WARNING"
    Info = "INFO"
    Debug = "DEBUG"
    Trace = "TRACE"


async def set_logging_level_autocomplete(
    interaction: Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    # Get stdlib loggers, loguru loggers from our registry, sort, and remove duplicates
    all_loggers = sorted({logging.getLogger(name).name for name in logging.root.manager.loggerDict} | LOGGER_NAMES)

    # Extract top-level package names from hierarchical loggers
    if "." not in current.lower():
        # Show top-level packages (e.g., "boozebot", "discord", etc.)
        # Extract first component of each logger name
        top_level = set()
        for logger_name in all_loggers:
            if "." in logger_name:
                top_level.add(logger_name.split(".")[0])
            else:
                top_level.add(logger_name)
        all_loggers = sorted(top_level)
        logger.debug(f"No dot in current input '{current}', showing {len(all_loggers)} top-level packages")
    else:
        # User has typed a dot, show matching hierarchical loggers
        logger.debug(f"Dot found in current input '{current}', showing hierarchical loggers")

    # Filter by current input before truncating
    filtered = [logger_name for logger_name in all_loggers if current.lower() in logger_name.lower()]

    if len(filtered) > 25:
        # Generate a warning and move on. Log the full list in debug if we care to check it out later
        logger.warning("Autocomplete returned more options than Discord can handle. Truncating to 25")
        logger.debug(filtered)

    # Convert to Choice objects
    filtered = [app_commands.Choice(name=logger_name, value=logger_name) for logger_name in filtered[:25]]

    logger.debug(f"Final autocomplete results for '{current}': {len(filtered)} options")
    if filtered:
        logger.debug(f"First few results: {[c.name for c in filtered[:5]]}")

    return filtered


class Logger(commands.Cog):
    @app_commands.command(name="set_logging_level", description="Set logging level for the bot")
    @app_commands.checks.has_any_role(*any_council_role)
    @app_commands.describe(
        log_level="Logging level to set",
        logger_name="Which logger to set the level for (default: all, resets any current overrides)",
    )
    @autocomplete(logger_name=set_logging_level_autocomplete)
    async def set_logging_level(
        self, interaction: Interaction, log_level: LogLevels, logger_name: str | None = None
    ) -> None:
        logger.info(f"Setting logging level to {log_level.name} as requested by {interaction.user.name}")

        if logger_name:
            if logger_name == "_default":
                await interaction.response.send_message("Cannot set logging level for reserved logger name '_default'.")
                return

            create_logger_sink(logger_name, log_level.value)
            logger.info(f"Logging level for {logger_name} set to {log_level.name}")
            await interaction.response.send_message(f"Logging level for {logger_name} set to {log_level.name}")

        else:
            for logger_name, sink_id in list(LOG_SINKS.items()):
                if logger_name != "_default":
                    logger.remove(sink_id)
                    del LOG_SINKS[logger_name]
            create_default_logger_sink(log_level.value)
            logger.info(f"Logging level set to {log_level.name}")
            await interaction.response.send_message(f"Logging level set to {log_level.name}")


# Setup logging when the module is imported
setup_logging()
