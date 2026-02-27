import discord
from discord import DMChannel, DiscordException, Interaction
from discord.abc import Messageable
from discord.app_commands import AppCommandError
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

    async def on_generic_error(
        self, interaction: Interaction, error: Exception
    ):  # an error handler for our custom errors
        try:
            if isinstance(error, SilentError):
                emoji = "🤫 SilentError"
            elif isinstance(error, AsyncioTimeoutError):
                emoji = "⏲ TimeoutError"
            else:
                emoji = "❌ Error"

            spamchannel = await self.get_or_fetch.channel(CHANNEL_BOTSPAM)

            assert isinstance(spamchannel, Messageable)
            assert interaction is not None
            assert interaction.command is not None
            assert interaction.channel is not None

            spam_embed = discord.Embed(
                description=f"{emoji} from `{interaction.command.name}` in <#{interaction.channel.id}> called by <@{interaction.user.id}>: ```{error}```",
                color=EMBED_COLOUR_ERROR,
            )
            await spamchannel.send(embed=spam_embed)

        except Exception as e:
            logger.error(e)

        if isinstance(error, GenericError):
            logger.error(f"❌ Generic error raised: {error}")
            embed = discord.Embed(description=f"❌ {error}", color=EMBED_COLOUR_ERROR)
            try:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception:
                await interaction.followup.send(embed=embed, ephemeral=True)

        elif isinstance(
            error, CustomError
        ):  # this class receives custom error messages and displays either privately or publicly
            message = error.message
            isprivate = error.isprivate
            logger.error(f"❌ Raised CustomError from {error} with message {message}")
            embed = discord.Embed(description=f"❌ {message}", color=EMBED_COLOUR_ERROR)
            if isprivate:  # message should be ephemeral
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except Exception:
                    await interaction.followup.send(embed=embed, ephemeral=True)
            else:  # message should be public - use for CCO commands
                try:
                    await interaction.response.send_message(embed=embed)
                except Exception:
                    await interaction.followup.send(embed=embed)

        elif isinstance(error, AsyncioTimeoutError):
            message = error.message
            logger.error(f"⏲ TimeoutError raised: {error}")
            embed = discord.Embed(
                description=f"❌⏲ {message}", color=EMBED_COLOUR_ERROR
            )
            try:
                await interaction.response.send_message(
                    embed=embed, ephemeral=error.isprivate
                )
            except Exception:
                await interaction.followup.send(embed=embed, ephemeral=error.isprivate)

        elif isinstance(error, SilentError):
            logger.info("🤫 SilentError called - error was not reported to user.")

        else:
            logger.error(f"❌ Error {error} was not caught by on_generic_error")

    async def on_app_command_error(
        self, interaction: Interaction, error: AppCommandError
    ):  # an error handler for discord.py errors

        assert interaction is not None
        assert interaction.command is not None
        assert isinstance(interaction.channel, Messageable)
        assert not isinstance(interaction.channel, DMChannel)

        logger.error(
            f"❌ Error from {interaction.command.name} in {interaction.channel.name} called by {interaction.user.display_name}: {error}"
        )

        try:
            if isinstance(error, CommandChannelError):
                logger.debug("Channel check error raised")
                formatted_channel_list = error.formatted_channel_list

                embed = discord.Embed(
                    description=f"Sorry, you can only run this command out of: {formatted_channel_list}",
                    color=EMBED_COLOUR_ERROR,
                )
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except DiscordException:
                    await interaction.followup.send(embed=embed, ephemeral=True)

            elif isinstance(error, CommandRoleError):
                logger.debug("Role check error raised")
                permitted_roles = error.permitted_role_id
                formatted_role_list = error.formatted_role_list
                if len(permitted_roles) > 1:
                    embed = discord.Embed(
                        description=f"**Permission denied**: You need one of the following roles to use this command:\n{formatted_role_list}",
                        color=EMBED_COLOUR_ERROR,
                    )
                else:
                    embed = discord.Embed(
                        description=f"**Permission denied**: You need the following role to use this command:\n{formatted_role_list}",
                        color=EMBED_COLOUR_ERROR,
                    )
                logger.debug("notify user")
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except DiscordException:
                    await interaction.followup.send(embed=embed, ephemeral=True)

            elif isinstance(error, CustomError):
                message = error.message
                isprivate = error.isprivate
                logger.error(f"Raised CustomError from {error} with message {message}")
                embed = discord.Embed(
                    description=f"❌ {message}", color=EMBED_COLOUR_ERROR
                )
                if isprivate:  # message should be ephemeral
                    try:
                        await interaction.response.send_message(
                            embed=embed, ephemeral=True
                        )
                    except Exception:
                        await interaction.followup.send(embed=embed, ephemeral=True)
                else:  # message should be public - use for CCO commands
                    try:
                        await interaction.response.send_message(embed=embed)
                    except Exception:
                        await interaction.followup.send(embed=embed)

            elif isinstance(error, GenericError):
                logger.error(f"Generic error raised: {error}")
                embed = discord.Embed(
                    description=f"❌ {error}", color=EMBED_COLOUR_ERROR
                )
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except Exception:
                    await interaction.followup.send(embed=embed, ephemeral=True)

            else:
                logger.error("Othertype error message raised")
                embed = discord.Embed(
                    description=f"❌ Unhandled Error: {error}", color=EMBED_COLOUR_ERROR
                )
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except Exception:
                    await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"An error occurred in the error handler (lol): {e}")

    async def on_background_error(
        self, error: BackgroundError
    ):  # an error handler for interactionless errors
        logger.error(f"⚠ Handler received background error: {error}")

        try:
            spamchannel = await self.get_or_fetch.channel(CHANNEL_BOTSPAM)
            assert isinstance(spamchannel, Messageable)
            spam_embed = discord.Embed(
                description=f":warning: {error.message}", color=EMBED_COLOUR_WARNING
            )
            await spamchannel.send(embed=spam_embed)

        except Exception as e:
            logger.error(e)
