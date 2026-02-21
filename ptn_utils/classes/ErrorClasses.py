from discord.app_commands import CheckFailure


class CommandChannelError(CheckFailure):  # channel check error
    formatted_channel_list: str
    permitted_channel_id: list[int]

    def __init__(self, permitted_channel_id: list[int], formatted_channel_list: str):
        self.permitted_channel_id = permitted_channel_id
        self.formatted_channel_list = formatted_channel_list
        super().__init__(
            permitted_channel_id, formatted_channel_list, "Channel check error raised"
        )


class CommandRoleError(CheckFailure):  # role check error
    formatted_role_list: str
    permitted_role_id: list[int]

    def __init__(self, permitted_role_id: list[int], formatted_role_list: str):
        self.permitted_role_id = permitted_role_id
        self.formatted_role_list = formatted_role_list
        super().__init__(
            permitted_role_id, formatted_role_list, "Role check error raised"
        )


class AsyncioTimeoutError(Exception):
    isprivate: bool
    message: str

    def __init__(self, message: str, isprivate: bool = True):
        super().__init__(message)
        self.message = message
        self.isprivate = isprivate


class SilentError(Exception):  # generic error
    pass


class GenericError(Exception):  # generic error
    pass


class CustomError(
    Exception
):  # an error handler that hides the Exception text from the user, but shows custom text sent from the source instead
    isprivate: bool
    message: str

    def __init__(self, message: str, isprivate: bool = True):
        self.message = message
        self.isprivate = isprivate
        super().__init__(self.message, "CustomError raised")


class BackgroundError(Exception):  # an error handler for interaction-less errors
    message: str | None

    def __init__(self, message: str | None = None):
        self.message = message or "BackgroundError raised"
        super().__init__(self.message)
