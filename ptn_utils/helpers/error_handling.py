from typing import Any

from discord import DiscordException, Embed, Interaction, TextChannel, Thread
from discord.app_commands import AppCommandError
from discord.app_commands.errors import CommandInvokeError as app_CommandInvokeError
from discord.ext.commands.errors import CommandInvokeError as ext_CommandInvokeError
from discord.ext.commands import Context, CommandError
from ptn_utils.get_or_fetch import GetOrFetch
from ptn_utils.global_constants import (
    CHANNEL_BOTSPAM,
    EMBED_COLOUR_ERROR,
    EMBED_COLOUR_WARNING,
)
from ptn_utils.logger.logger import get_logger
from ptn_utils.classes.ErrorClasses import (
    BackgroundError,
    CommandChannelError,
    CommandRoleError,
    SilentError,
    AsyncioTimeoutError,
    GenericError,
    CustomError,
)

logger = get_logger("ptn_utils.helpers.ErrorHandler")


"""
A primitive global error handler for all app commands (slash & ctx menus)

returns: the error message to the user and log
"""


class ErrorHandler:
    get_or_fetch: GetOrFetch

    def __init__(self, get_or_fetch: GetOrFetch):
        self.get_or_fetch = get_or_fetch

    async def on_generic_error(self, ctx: Interaction | Context[Any], error: CommandError):
        """An error handler for our custom errors"""

        async def send_reply(ctx: Interaction | Context[Any], embed: Embed, isprivate: bool):
            is_interaction = isinstance(ctx, Interaction)
            try:
                if is_interaction:
                    try:
                        await ctx.response.send_message(embed=embed, ephemeral=isprivate)
                    except DiscordException:
                        await ctx.followup.send(embed=embed, ephemeral=isprivate)
                else:
                    await ctx.channel.send(embed=embed)
            except DiscordException as e:
                logger.exception(e)

        if isinstance(error, ext_CommandInvokeError):
            err = error.original
        else:
            err = error

        try:
            if isinstance(err, SilentError):
                emoji = "🤫 SilentError"
            elif isinstance(err, AsyncioTimeoutError):
                emoji = "⏲ TimeoutError"
            else:
                emoji = "❌ Error"

            spamchannel = await self.get_or_fetch.channel(CHANNEL_BOTSPAM)

            assert isinstance(spamchannel, (TextChannel, Thread))
            assert ctx.command is not None
            assert ctx.channel is not None

            user_id = ctx.user.id if isinstance(ctx, Interaction) else ctx.author.id
            spam_embed = Embed(
                description=f"{emoji} from `{ctx.command.name}` in <#{ctx.channel.id}> called by <@{user_id}>: ```{err}```",
                color=EMBED_COLOUR_ERROR,
            )
            await spamchannel.send(embed=spam_embed)

        except DiscordException as e:
            logger.error(e)

        if isinstance(err, GenericError):
            logger.error(f"❌ Generic error raised: {err}")
            embed = Embed(description=f"❌ {err}", color=EMBED_COLOUR_ERROR)

            await send_reply(ctx, embed, False)

        # this class receives custom error messages and displays either privately or publicly
        elif isinstance(err, CustomError):
            message = err.message
            logger.error(f"❌ Raised CustomError from {err} with message {message}")
            embed = Embed(description=f"❌ {message}", color=EMBED_COLOUR_ERROR)

            await send_reply(ctx, embed, err.isprivate)

        elif isinstance(err, AsyncioTimeoutError):
            message = err.message
            logger.error(f"⏲ TimeoutError raised: {err}")
            embed = Embed(description=f"❌⏲ {message}", color=EMBED_COLOUR_ERROR)
            await send_reply(ctx, embed, err.isprivate)

        elif isinstance(err, SilentError):
            logger.info("🤫 SilentError called - error was not reported to user.")

        else:
            logger.error(f"❌ Error {err} was not caught by on_generic_error")

    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        """An error handler for discord.py errors"""
        assert interaction.command is not None
        assert isinstance(interaction.channel, (TextChannel, Thread))

        if isinstance(error, app_CommandInvokeError):
            err = error.original
        else:
            err = error

        logger.error(
            f"❌ Error from {interaction.command.name} in {interaction.channel.name} called by {interaction.user.display_name}: {err}"
        )

        try:
            if isinstance(err, CommandChannelError):
                logger.debug("Channel check error raised")
                formatted_channel_list = err.formatted_channel_list

                embed = Embed(
                    description=f"Sorry, you can only run this command out of: {formatted_channel_list}",
                    color=EMBED_COLOUR_ERROR,
                )
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except DiscordException:
                    await interaction.followup.send(embed=embed, ephemeral=True)

            elif isinstance(err, CommandRoleError):
                logger.debug("Role check error raised")
                permitted_roles = err.permitted_role_id
                formatted_role_list = err.formatted_role_list
                if len(permitted_roles) > 1:
                    embed = Embed(
                        description=f"**Permission denied**: You need one of the following roles to use this command:\n{formatted_role_list}",
                        color=EMBED_COLOUR_ERROR,
                    )
                else:
                    embed = Embed(
                        description=f"**Permission denied**: You need the following role to use this command:\n{formatted_role_list}",
                        color=EMBED_COLOUR_ERROR,
                    )
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except DiscordException:
                    await interaction.followup.send(embed=embed, ephemeral=True)

            elif isinstance(err, CustomError):
                message = err.message
                isprivate = err.isprivate
                logger.error(f"Raised CustomError from {err} with message {message}")
                embed = Embed(description=f"❌ {message}", color=EMBED_COLOUR_ERROR)
                if isprivate:  # message should be ephemeral
                    try:
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                    except DiscordException:
                        await interaction.followup.send(embed=embed, ephemeral=True)
                else:  # message should be public - use for CCO commands
                    try:
                        await interaction.response.send_message(embed=embed)
                    except DiscordException:
                        await interaction.followup.send(embed=embed)

            elif isinstance(err, GenericError):
                logger.error(f"Generic error raised: {err}")
                embed = Embed(description=f"❌ {err}", color=EMBED_COLOUR_ERROR)
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except DiscordException:
                    await interaction.followup.send(embed=embed, ephemeral=True)

            else:
                logger.error("Othertype error message raised")
                embed = Embed(description=f"❌ Unhandled Error: {err}", color=EMBED_COLOUR_ERROR)
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except DiscordException:
                    await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"An error occurred in the error handler (lol): {e}")

    async def on_background_error(self, error: BackgroundError):
        """An error handler for interactionless errors"""
        logger.error(f"⚠ Handler received background error: {error}")
        try:
            spamchannel = await self.get_or_fetch.channel(CHANNEL_BOTSPAM)
            assert isinstance(spamchannel, (TextChannel, Thread))
            spam_embed = Embed(description=f":warning: {error.message}", color=EMBED_COLOUR_WARNING)
            await spamchannel.send(embed=spam_embed)
        except DiscordException as e:
            logger.error(e)
