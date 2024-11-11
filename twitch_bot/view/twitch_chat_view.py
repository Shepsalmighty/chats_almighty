# INFO code examples from https://pytwitchapi.dev/en/stable/

import asyncio
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatCommand
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope, ChatEvent
from twitch_bot.model.database_interface import DataBaseInterface as DB
import requests
from twitch_bot.view.Twitch_API import TwitchAPI_call


# TODO: Add a reply if anyone types "sudo !!" of "nice try"

# INFO in the view class all user interactions are defined, it represents the user interface, commands like !discord or !help are part of it
class TwitchChatView:
    USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

    def __init__(self, client_id, client_secret, path, target_channel):
        self.client_id = client_id
        self.client_secret = client_secret
        self.path = path
        self.channel = target_channel
        self.lock = asyncio.Lock()
        self.users_notified = set()
        self.notified_lock = asyncio.Lock()
        self.db = DB(self.channel, "db/twitch_bot.db")
        self.twitch_client = TwitchAPI_call(client_id, client_secret)
        self.user_exists_check = self.twitch_client.get_users

    async def on_message(self, msg: ChatMessage):

        if msg.text.startswith("!"):
            args = msg.text.split(" ", 1)

            command_exists = await self.db.command_exists(msg)

            if args[0] == "!set" or args[0] == '!leavemsg':
                pass
            elif args[0] == "!getmsg":
                await self.get_msg(msg)
            elif command_exists:
                await self.link_command(msg)
            elif command_exists is None and msg.user.name == self.channel:
                await msg.reply(f"add a link to your {msg.text} using \"!set !{msg.text.lstrip("!")} link\"   ")

            elif command_exists is None and msg.user.name != self.channel:
                await msg.reply(f"no {msg.text} link yet")

        else:
            print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
        await self.notify_user(msg)

    async def on_ready(self, ready_event: EventData):
        print('Bot is ready for work, joining channels')
        # join our target channel, if you want to join multiple, either call join for each individually
        # or even better pass a list of channels as the argument
        await ready_event.chat.join_room(self.channel)
        # you can do other bot initialization things in here

    # TODO: add "!stupid" and "!smrt" incremental counters for chat
    # TODO" add "!hug" command
    # TODO add !lurk

    # TODO: add !help
    # !set(!example) over writes existing command with channel owners input links etc
    async def set_command(self, cmd: ChatCommand):
        if cmd.user.name == self.channel:
            args = cmd.parameter.split(" ", 1)
            if len(args) < 2:
                await cmd.reply("command set incorrectly, did you forget to add the link?")

            await self.db.set_command(cmd)


        else:
            # await cmd.reply("you cannot change bot settings")
            await cmd.reply("set up auth to gain permissions: https://tinyurl.com/twitchauth")

    async def link_command(self, msg: ChatMessage):

        if msg.text.startswith("!"):
            # args = msg.text.split(" ", 1)
            await self.db.get_link(msg)

    async def leavemsg(self, msg: ChatMessage):
        args = msg.text.split(" ", 2)
        # twitch api call to check if a user exists before accessing db to leave a msg
        # if len(args) >= 2 and self.user_exists_check(args[1].lstrip("@")):
        if len(args) != 3:
            return await msg.reply("it looks like you used this command incorrectly, did you forget your message?")

        username, message = args[1], args[2]
        # TODO - implement regex instead of below --- lol ok
        if (msg.text.startswith("!") and
                args[0] == "!leavemsg" and
                self.user_exists_check(args[1].lstrip("@")) and
                args[1] != msg.user.name):
            await self.db.leave_message(msg)
        # else:
        #     await msg.reply("this user doesn't exist")

    # INFO - CHECK USER EXISTS - https://dev.twitch.tv/docs/api/reference/#get-users
    async def notify_user(self, msg: ChatMessage):
        user_msgs_count = await self.db.notify(msg)

        args = msg.text.split(" ", 1)

        if len(user_msgs_count) > 0 and not msg.text.startswith("!getmsg") and msg.user.name not in self.users_notified:
            await msg.reply(
                "you have messages stored from: " +
                ", ".join(f"@{user} ({count})" for count, user in user_msgs_count) +
                " to get a message use !getmsg @username")

            async with self.notified_lock:
                self.users_notified.add(msg.user.name)

        elif len(user_msgs_count) > 0 and len(args) == 1 and args[0] == "!getmsg":
            await msg.reply(
                "To get a message use !getmsg @username. You have messages stored from: " +
                ", ".join(f"@{user} ({count})" for count, user in user_msgs_count))

    async def get_msg(self, msg: ChatMessage):
        """send msg to db.get_message function
                    check database for sender and reciever
                    if message(s) exists we send that back here
                    and msg.reply with the message from the sender
                    then delete the entry from the database """
        args = msg.text.split(" ", 1)
        for msgs in await self.db.get_message(msg):
            await msg.reply(msgs)

    # TODO: add some tests

    # this is where we set up the bot
    async def run(self):
        # set up twitch api instance and add user authentication with some scopes
        twitch = await Twitch(self.client_id, self.client_secret)
        # auth = UserAuthenticator(twitch, USER_SCOPE)
        # token, refresh_token = await auth.authenticate()
        # await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)
        helper = UserAuthenticationStorageHelper(twitch, TwitchChatView.USER_SCOPE, storage_path=self.path)
        await helper.bind()

        # create chat instance
        chat = await Chat(twitch)

        # register the handlers for the events you want

        # listen to when the bot is done starting up and ready to join channels
        chat.register_event(ChatEvent.READY, self.on_ready)
        # listen to chat messages
        chat.register_event(ChatEvent.MESSAGE, self.on_message)
        # # listen to channel subscriptions
        # chat.register_event(ChatEvent.SUB, on_sub)
        # # there are more events, you can view them all in this documentation
        #
        # # INFO you must directly register commands and their handlers, this will register the 1st command !reply
        # chat.register_command('reply', test_command)
        chat.register_command('set', self.set_command)
        chat.register_command('leavemsg', self.leavemsg)
        chat.register_command('getmsg', self.get_msg)
        # TODO make !help command

        # we are done with our setup, lets start this bot up!
        chat.start()

        # lets run till we press enter in the console
        try:
            input('press ENTER to stop\n')
        finally:
            # now we can close the chat bot and the twitch api client
            chat.stop()
            await twitch.close()
# chat_view_instance = TwitchChatView()
