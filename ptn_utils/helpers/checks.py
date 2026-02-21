from discord import CategoryChannel, Interaction, Role
from discord.abc import GuildChannel
from discord.ext.commands import NoPrivateMessage
from discord.app_commands import check
from ptn_utils.get_or_fetch import GetOrFetch
from ptn_utils.global_constants import (
    any_moderation_role,
    CAT_CC,
    CAT_SC,
    CAT_SOMM,
    CAT_FACTION,
    ROLE_CM,
    ROLE_PATH,
    ROLE_FO,
    ROLE_SOMM,
)
from ptn_utils.logger.logger import get_logger
from ptn_utils.classes.ErrorClasses import CommandRoleError, CommandChannelError

logger = get_logger("ptn_utils.helpers.decorators")


class Checks:
    get_or_fetch: GetOrFetch

    def __init__(self, get_or_fetch: GetOrFetch):
        self.get_or_fetch = get_or_fetch

    # decorator for interaction channel checks
    def command_channel(self, permitted_channel_id: list[int] | int):
        """
        Decorator used on a command to limit it to specified channels
        """

        if not permitted_channel_id:
            raise ValueError("No Channels specified!")

        permitted_channel_id = (
            permitted_channel_id
            if isinstance(permitted_channel_id, list)
            else [permitted_channel_id]
        )

        async def check_channel(interaction: Interaction) -> bool:
            """
            Check if the channel the command was run from matches any permitted channels for that command
            """

            if interaction.guild is None:
                raise NoPrivateMessage()

            assert isinstance(interaction.channel, GuildChannel)
            logger.debug(
                f"check_command_channel called: {interaction.user.name} in {interaction.channel.name} ({interaction.channel.id}). Permitted Channel IDs: {permitted_channel_id}"
            )

            permission = interaction.channel_id in permitted_channel_id

            if not permission:
                # check has failed, now assemble data for error message
                permitted_channels: list[str] = []
                for channel_id in permitted_channel_id:
                    channel = await self.get_or_fetch.channel(channel_id)
                    if not channel:
                        logger.error(f"Unknown Channel: {channel_id}")
                        continue
                    permitted_channels.append(channel.mention)
                formatted_channel_list = " • ".join(permitted_channels)
                raise CommandChannelError(permitted_channel_id, formatted_channel_list)

            return True

        return check(check_channel)

    def roles(self, permitted_role_id: list[int] | int):
        """
        Decorator used on a command to limit it to specified roles
        """

        if not permitted_role_id:
            raise ValueError("No Roles specified!")

        permitted_role_id = (
            permitted_role_id
            if isinstance(permitted_role_id, list)
            else [permitted_role_id]
        )

        async def check_role(interaction: Interaction) -> bool:
            """
            Check if the user has at least one of the permitted roles to run a command
            """

            user_role_ids: list[int] = [role.id for role in interaction.user.roles]  # pyright: ignore[reportAttributeAccessIssue]
            logger.debug(
                f"check_role called on {interaction.user.name}. Roles: {user_role_ids}. Permitted role IDs: {permitted_role_id}"
            )

            permission = set(permitted_role_id) & set(user_role_ids)
            logger.debug(
                f"User {'has' if permission else 'does not have'} permission.",
            )
            if not permission:
                permitted_roles: list[Role | None] = []
                for role_id in permitted_role_id:
                    role = await self.get_or_fetch.role(role_id)
                    if not role:
                        logger.error(f"Unknown Role: {role_id}")
                    permitted_roles.append(role)
                logger.debug(f"permitted_roles: {permitted_roles}")
                formatted_role_list = " • ".join(
                    [f"{role.mention} " for role in permitted_roles]  # pyright: ignore[reportOptionalMemberAccess]
                )
                raise CommandRoleError(permitted_role_id, formatted_role_list)

            return True

        return check(check_role)

    def category_perms(self):
        """
        Decorator used on a command to limit it to endgame roles in their specific category

        NOTE: This will NOT function as a category-specific override for check.roles. If this decorator and check.roles are used on the same command, BOTH must be satisfied for the command to proceed.
        """

        async def check_category_perms_aux(interaction: Interaction):
            """
            Check if the user has at least one of the permitted roles to run a command, adding in special powers depending on category
            """
            assert interaction.channel is not None
            assert isinstance(interaction.channel, GuildChannel)
            assert isinstance(interaction.channel.category, CategoryChannel)

            category = interaction.channel.category

            assert interaction.command is not None
            logger.info(
                f"{interaction.user.name} used /{interaction.command.name} in {interaction.channel.mention}"
            )

            permitted_role_ids = any_moderation_role.copy()
            if category.id == CAT_CC:
                permitted_role_ids.append(ROLE_CM)
            elif category.id == CAT_SOMM:
                permitted_role_ids.append(ROLE_SOMM)
            elif category.id == CAT_FACTION:
                permitted_role_ids.append(ROLE_FO)
            elif category.id == CAT_SC:
                permitted_role_ids.append(ROLE_PATH)

            # Debug logging of user/permitted roles will come from check_roles. No need to repeat here.
            try:
                _unused = self.roles(permitted_role_ids)
            except CommandRoleError:
                logger.error(
                    f"❌ {interaction.user.name} does not have permission to run this command in this category"
                )
                raise

            logger.debug(
                f"✅ {interaction.user.name} is allowed to run command /{interaction.command.name} in {category.name} channels."
            )
            return True

        return check(check_category_perms_aux)
