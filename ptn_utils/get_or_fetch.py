import logging

from discord import Guild, Thread, Role, Member, Emoji, GuildSticker
from discord.ext import commands
from discord.abc import GuildChannel
from typing import Optional


class GetOrFetch:
    def __init__(self, bot: commands.Bot, guild_id: int):
        self.bot = bot
        self.guild_id = guild_id

    async def guild(self, guild: int) -> Optional[Guild]:
        """Return bot guild instance for use in get_member()"""
        try:
            return self.bot.get_guild(guild) or await self.bot.fetch_guild(guild)
        except Exception as e:
            logging.exception(e)
            return None

    async def channel(self, channel_id: int) -> Optional[GuildChannel | Thread]:
        """Fetch a channel or thread from the guild."""
        guild = await self.guild(self.guild_id)
        try:
            return guild.get_channel(channel_id) or await guild.fetch_channel(channel_id)
        except Exception as e:
            logging.exception(e)
            return None

    async def member(self, member_id: int) -> Optional[Member]:
        """Fetch a member from the guild."""
        guild = await self.guild(self.guild_id)
        try:
            return guild.get_member(member_id) or await guild.fetch_member(member_id)
        except Exception as e:
            logging.exception(e)
            return None

    async def role(self, role_id: int) -> Optional[Role]:
        """Fetch a role from the guild."""
        guild = await self.guild(self.guild_id)
        try:
            return guild.get_role(role_id) or await guild.fetch_role(role_id)
        except Exception as e:
            logging.exception(e)
            return None

    async def emoji(self, emoji_id: int) -> Optional[Emoji]:
        """Fetch an emoji from the guild."""
        guild = await self.guild(self.guild_id)
        try:
            return guild.get_emoji(emoji_id) or await guild.fetch_emoji(emoji_id)
        except Exception as e:
            logging.exception(e)
            return None

    async def sticker(self, sticker_id: int) -> Optional[GuildSticker]:
        """Fetch a sticker from the guild."""
        guild = await self.guild(self.guild_id)
        try:
            return self.bot.get_sticker(sticker_id) or await guild.fetch_sticker(sticker_id)
        except Exception as e:
            logging.exception(e)
            return None
