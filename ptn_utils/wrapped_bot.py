from discord import AllowedMentions
from typing import Any
from discord.ext.commands import Bot
from .get_or_fetch import GetOrFetch
from .helpers.checks import Checks
from .global_constants import DISCORD_GUILD, _production
from .helpers.error_handling import ErrorHandler


# Added for type hints
class WrappedBot(Bot):
    get_or_fetch: GetOrFetch
    checks: Checks
    error_handler: ErrorHandler

    def __init__(self, **kwargs: Any):
        allowed_mentions = kwargs.pop("allowed_mentions", None)
        if not _production:
            allowed_mentions = allowed_mentions or AllowedMentions.none()
        kwargs["allowed_mentions"] = allowed_mentions

        super().__init__(**kwargs)
        self.get_or_fetch = GetOrFetch(self, DISCORD_GUILD)
        self.checks = Checks(self.get_or_fetch)
        self.error_handler = ErrorHandler(self.get_or_fetch)

        self.tree.on_error = self.error_handler.on_app_command_error
        self.add_listener(self.error_handler.on_generic_error, "on_command_error")
