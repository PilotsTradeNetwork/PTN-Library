import logging

from discord import Emoji, Guild, GuildSticker, Member, Role, Thread, User
from discord.abc import GuildChannel
from discord.ext import commands


class GetOrFetch:
    def __init__(self, bot: commands.Bot, guild_id: int):
        self.bot = bot
        self.guild_id = guild_id

    async def guild(self, guild: int) -> Guild | None:
        """Return bot guild instance for use in get_member()"""
        try:
            return self.bot.get_guild(guild) or await self.bot.fetch_guild(guild)
        except Exception as e:
            logging.exception(e)
            return None

    async def channel(self, channel_id: int) -> GuildChannel | Thread | None:
        """Fetch a channel or thread from the guild."""
        guild = await self.guild(self.guild_id)
        try:
            return guild.get_channel(channel_id) or await guild.fetch_channel(channel_id)
        except Exception as e:
            logging.exception(e)
            return None

    async def member(self, member_id: int) -> Member | None:
        """Fetch a member from the guild."""
        guild = await self.guild(self.guild_id)
        try:
            return guild.get_member(member_id) or await guild.fetch_member(member_id)
        except Exception as e:
            logging.exception(e)
            return None

    async def user(self, user_id: int) -> User | None:
        """Fetch a user from discord."""
        try:
            return self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
        except Exception as e:
            logging.exception(e)
            return None

    async def role(self, role_id: int) -> Role | None:
        """Fetch a role from the guild."""
        guild = await self.guild(self.guild_id)
        try:
            return guild.get_role(role_id) or await guild.fetch_role(role_id)
        except Exception as e:
            logging.exception(e)
            return None

    async def emoji(self, emoji_id: int) -> Emoji | None:
        """Fetch an emoji from the guild."""
        guild = await self.guild(self.guild_id)
        try:
            return guild.get_emoji(emoji_id) or await guild.fetch_emoji(emoji_id)
        except Exception as e:
            logging.exception(e)
            return None

    async def sticker(self, sticker_id: int) -> GuildSticker | None:
        """Fetch a sticker from the guild."""
        guild = await self.guild(self.guild_id)
        try:
            return self.bot.get_sticker(sticker_id) or await guild.fetch_sticker(sticker_id)
        except Exception as e:
            logging.exception(e)
            return None
