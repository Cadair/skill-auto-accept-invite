from textwrap import dedent
import logging

from opsdroid.connector.matrix import ConnectorMatrix
from opsdroid.connector.matrix.events import GenericMatrixRoomEvent
from opsdroid.events import Message, UserInvite, JoinRoom
from opsdroid.matchers import match_regex, match_event
from opsdroid.skill import Skill

_LOGGER = logging.getLogger(__name__)

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



class AcceptInvite(Skill):
    """
    An opsdroid skill to accept invites
    """
    def __init__(self, opsdroid, config):
        super().__init__(opsdroid, config)
        self._auto_invite = True
        self._admin_room = None

    @property
    def matrix_connector(self):
        matrix_connector = [c for c in self.opsdroid.connectors if isinstance(c, ConnectorMatrix)]
        if not matrix_connector:
            raise ValueError("The auto-accept-invite skill only works with the matrix connector")
        return matrix_connector[0]

    async def auto_invite(self):
        if self._auto_invite is not None:
            return self._auto_invite

        # TODO: Get from database in admin room

    async def admin_room_id(self):
        """
        Get the room_id of the admin room.
        """
        if self._admin_room is not None:
            return self._admin_room

        admin_room = self.matrix_connector.config["rooms"].get("auto-accept-invite")
        if admin_room is not None and not admin_room.startswith("!"):
            response = await self.connection.room_resolve_alias(admin_room)
            if isinstance(response, nio.RoomResolveAliasError):
                _LOGGER.error(
                    f"Error resolving room id for {self.admin_room}: {response.message} (status code {response.status_code})"
                )
            else:
                admin_room = response.room_id
        self._admin_room = admin_room

    @regex_command("rooms", "print a list of all rooms this bot is in.")
    async def bands(self, message):
        if message.target != await self.admin_room_id():
            return
        await message.respond("Not Implemented yet")

    @regex_command("stop", "stop accepting invites")
    async def stop(self, message):
        if message.target != await self.admin_room_id():
            return
        await message.respond("Not Implemented yet.")

    @regex_command("start", "start accepting invites")
    async def start(self, message):
        if message.target != await self.admin_room_id():
            return
        await message.respond("Not Implemented yet.")

    @regex_command("help", "print this help message")
    async def help(self, message):
        if message.target != await self.admin_room_id():
            return
        commands = "\n".join([f"{INVITEBOT_COMMAND_PREFIX}{command} - {description}" for command, description in INVITEBOT_COMMANDS.items()])
        help_text = dedent("""\
        This bot understands the following commands:

        {commands}
        """).format(commands=commands)
        await message.respond(help_text)

    @match_event(UserInvite)
    async def on_invite_to_room(self, invite):
        """
        Join all rooms on invite.
        """
        _LOGGER.info("Got room invite.")
        if await self.auto_invite():
            await invite.respond(JoinRoom())
            _LOGGER.info("Accepted room invite.")
        else:
            _LOGGER.info("Rejected room invite because auto invite is off.")
