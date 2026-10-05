from typing import TypeVar, overload

from discord import Emoji, Guild, GuildSticker, Member, Role, Thread, User
from discord.abc import GuildChannel
from discord.ext import commands

from ptn_utils.logger.logger import get_logger

logger = get_logger("ptn_utils.get_or_fetch")

ChannelType = TypeVar("ChannelType", bound=GuildChannel | Thread)

class GetOrFetch:
    def __init__(self, bot: commands.Bot, guild_id: int):
        self.bot = bot
        self.guild_id = guild_id

    async def guild(self, guild: int) -> Guild | None:
        """Return bot guild instance for use in get_member()"""
        try:
            return self.bot.get_guild(guild) or await self.bot.fetch_guild(guild)
        except Exception:
            logger.exception(f"Failed to get or fetch guild with ID {guild}")
            return None

    @overload
    async def channel(self, channel_id: int) -> GuildChannel | Thread | None:
        ...

    @overload
    async def channel(self, channel_id: int, *, channel_type: type[ChannelType]) -> ChannelType | None:
        ...

    async def channel(
        self, channel_id: int, *, channel_type: type[ChannelType] | None = None
    ) -> GuildChannel | Thread | None:
        """Fetch a channel or thread from the guild.

        If ``channel_type`` is given, the result is checked against it and
        ``None`` is returned on a mismatch (the type checker also narrows the
        return type to that class).
        """
        guild = await self.guild(self.guild_id)
        if not guild:
            logger.error(f"Guild with ID {self.guild_id} not found when trying to fetch channel with ID {channel_id}")
            return None
        try:
            channel = guild.get_channel(channel_id) or await guild.fetch_channel(channel_id)
        except Exception:
            logger.exception(f"Failed to get or fetch channel with ID {channel_id} in guild {self.guild_id}")
            return None
        if channel_type is not None and not isinstance(channel, channel_type):
            logger.error(
                f"Channel with ID {channel_id} is {type(channel).__name__}, expected {channel_type.__name__}"
            )
            return None
        return channel

    async def member(self, member_id: int) -> Member | None:
        """Fetch a member from the guild."""
        guild = await self.guild(self.guild_id)
        if not guild:
            logger.error(f"Guild with ID {self.guild_id} not found when trying to fetch member with ID {member_id}")
            return None
        try:
            return guild.get_member(member_id) or await guild.fetch_member(member_id)
        except Exception:
            logger.exception(f"Failed to get or fetch member with ID {member_id} in guild {self.guild_id}")
            return None

    async def user(self, user_id: int) -> User | None:
        """Fetch a user from discord."""
        try:
            return self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
        except Exception:
            logger.exception(f"Failed to get or fetch user with ID {user_id}")
            return None

    async def role(self, role_id: int) -> Role | None:
        """Fetch a role from the guild."""
        guild = await self.guild(self.guild_id)
        if not guild:
            logger.error(f"Guild with ID {self.guild_id} not found when trying to fetch role with ID {role_id}")
            return None
        try:
            return guild.get_role(role_id) or await guild.fetch_role(role_id)
        except Exception:
            logger.exception(f"Failed to get or fetch role with ID {role_id} in guild {self.guild_id}")
            return None

    async def emoji(self, emoji_id: int) -> Emoji | None:
        """Fetch an emoji from the guild."""
        guild = await self.guild(self.guild_id)
        if not guild:
            logger.error(f"Guild with ID {self.guild_id} not found when trying to fetch emoji with ID {emoji_id}")
            return None
        try:
            return guild.get_emoji(emoji_id) or await guild.fetch_emoji(emoji_id)
        except Exception:
            logger.exception(f"Failed to get or fetch emoji with ID {emoji_id} in guild {self.guild_id}")
            return None

    async def sticker(self, sticker_id: int) -> GuildSticker | None:
        """Fetch a sticker from the guild."""
        guild = await self.guild(self.guild_id)
        if not guild:
            logger.error(f"Guild with ID {self.guild_id} not found when trying to fetch sticker with ID {sticker_id}")
            return None
        try:
            return self.bot.get_sticker(sticker_id) or await guild.fetch_sticker(sticker_id)
        except Exception:
            logger.exception(f"Failed to get or fetch sticker with ID {sticker_id} in guild {self.guild_id}")
            return None
