from textwrap import dedent

from opsdroid.connector.matrix import ConnectorMatrix
from opsdroid.connector.matrix.events import GenericMatrixRoomEvent
from opsdroid.events import Message, UserInvite, JoinRoom
from opsdroid.matchers import match_regex, match_event
from opsdroid.skill import Skill

INVITEBOT_COMMAND_PREFIX = "!"
INVITEBOT_COMMANDS = {}


def regex_command(command, description="", **kwargs):
    """
    A decorator which wraps opsdroid's match_regex to register a command with the !help command.
    """
    INVITEBOT_COMMANDS[command] = description
    def decorator(func):
        return match_regex(f"^{INVITEBOT_COMMAND_PREFIX}{command}", **kwargs)(func)
    return decorator


@regex_command("help", "print this help message")
async def help(opsdroid, config, message):
    commands = "\n".join([f"{INVITEBOT_COMMAND_PREFIX}{command} - {description}" for command, description in INVITEBOT_COMMANDS.items()])
    help_text = dedent("""\
    This bot understands the following commands:

    {commands}
    """).format(commands=commands)
    await message.respond(help_text)

class AcceptInvite(Skill):
    """
    An opsdroid skill to accept invites
    """
    @regex_command("rooms", "print a list of all rooms this bot is in.")
    async def bands(self, message):
        await message.respond("Not Implemented yet")

    @regex_command("stop", "stop accepting invites")
    async def stop(self, message):
        await message.respond("Not Implemented yet.")

    @regex_command("start", "start accepting invites")
    async def start(self, message):
        await message.respond("Not Implemented yet.")

    @match_event(UserInvite)
    async def on_invite_to_room(self, invite):
        """
        Join all rooms on invite.
        """
        _LOGGER.info("Got room invite.")
        await invite.respond(JoinRoom())
