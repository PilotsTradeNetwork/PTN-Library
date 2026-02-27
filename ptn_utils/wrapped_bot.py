from typing import Any

from discord import AllowedMentions, Intents
from discord.ext.commands import Bot

from .get_or_fetch import GetOrFetch
from .global_constants import DISCORD_GUILD, PRODUCTION
from .helpers.checks import Checks
from .helpers.error_handling import ErrorHandler


# Added for type hints
class WrappedBot(Bot):
    get_or_fetch: GetOrFetch
    checks: Checks
    error_handler: ErrorHandler

    def __init__(self, command_prefix: Any, *, intents: Intents, **options: Any):
        allowed_mentions = options.pop("allowed_mentions", None)
        if not PRODUCTION:
            allowed_mentions = allowed_mentions or AllowedMentions.none()
        options["allowed_mentions"] = allowed_mentions

        super().__init__(command_prefix, intents=intents, **options)
        self.get_or_fetch = GetOrFetch(self, DISCORD_GUILD)
        self.checks = Checks(self.get_or_fetch)
        self.error_handler = ErrorHandler(self.get_or_fetch)

        self.tree.on_error = self.error_handler.on_app_command_error  # type: ignore[assignment]
        self.add_listener(self.error_handler.on_generic_error, "on_command_error")
