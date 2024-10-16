# INFO code examples from https://pytwitchapi.dev/en/stable/
from types import NoneType
from urllib.parse import urljoin

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator, UserAuthenticationStorageHelper
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.chat.middleware import StreamerOnly
import asyncio
from dotenv import load_dotenv
from os import getenv
from pathlib import Path
import sqlite3
from contextlib import closing
import requests
import time
from twitch_bot.model.database_interface import DataBaseInterface as DB


# TODO: Add a reply if anyone types "sudo !!" of "nice try"

# INFO in the view class all user interactions are defined, it represents the user interface, commands like !discord or !help are part of it
class TwitchChatView:
    USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

    def __init__(self, client_id, client_secret, path, target_channel):
        self.client_id = client_id
        self.client_secret = client_secret
        self.path = path
        self.channel = target_channel
        # self.user_values = {}
        # self.allowed_user_values = ["youtube", "discord", "github", "today", "schedule"]
        self.lock = asyncio.Lock()
        # self.con = sqlite3.connect("twitch_bot.db")
        # self.cur = self.con.cursor()
        self.users_notified = set()
        # notified_lock = new lock for interacting with self.users_notified dict
        self.notified_lock = asyncio.Lock()
        self.db = DB(self.channel)

    async def on_message(self, msg: ChatMessage):

        if msg.text.startswith("!"):
            args = msg.text.split(" ", 1)
            # database_interface.DataBaseInterface.command_exists(args)

            # # INFO command_exists() -- MODEL
            # con = sqlite3.connect("twitch_bot.db")
            # cur = con.cursor()
            # command_exists = cur.execute('''SELECT LOWER(name) FROM commands WHERE name = ?
            #                                                      AND channel_id = (SELECT uid FROM channels WHERE name = (?))''',
            #                              (args[0].lstrip("!").lower(), self.channel)).fetchone()
            # con.close()
            # # INFO command_exists() -- MODEL

            command_exists = await self.db.command_exists(msg)

            if args[0] == "!set" or args[0] == '!leavemsg' or args[0] == '!getmsg':
                pass
            elif command_exists:
                await self.link_command(msg)
            elif command_exists is None and msg.user.name == self.channel:
                await msg.reply(f"add a link to your {msg.text} using \"!set !{msg.text.lstrip("!")} link\"   ")

            elif command_exists is None and msg.user.name != self.channel:
                await msg.reply(f"no {msg.text} link yet")

        else:
            print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
        await self.get_msg(msg), await self.notify_user(msg)

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

            # creating a lock to avoid multiple cursor objects accessing the table at once causing issues
            # INFO MOVE TO MODEL
            await self.db.set_command(cmd)
            # async with self.lock:
            #     with closing(sqlite3.connect("twitch_bot.db")) as con:
            #         cur = con.cursor()
            #         try:
            #             if cur.execute('SELECT COUNT (`name`) FROM channels').fetchone()[0] == 0:
            #                 cur.execute('INSERT INTO channels (`name`) VALUES (?)', (self.channel,))
            #                 con.commit()
            #
            #             command_id = cur.execute('''
            #             INSERT OR REPLACE INTO commands (`name`, `channel_id`)
            #             VALUES (?, (SELECT uid FROM channels WHERE name = ?))
            #             RETURNING uid''',
            #                                      (args[0].lstrip("!").lower(), self.channel))
            #             cur.execute('''
            #             INSERT OR REPLACE INTO links (`command_id`, `linktext`)
            #             VALUES (?, ?)''',
            #                         (command_id.fetchone()[0], args[1],))
            #             con.commit()
            #         # INFO model
            #         except sqlite3.Error as e:
            #             print(f'An error occurred: {e}')


        else:
            # await cmd.reply("you cannot change bot settings")
            await cmd.reply("set up auth to gain permissions: https://tinyurl.com/twitchauth")

    async def link_command(self, msg: ChatMessage):

        if msg.text.startswith("!"):
            # args = msg.text.split(" ", 1)
            await self.db.get_link(msg)

            # # if (cmd.text.lstrip("!") == command_exists[0]):
            # async with self.lock:
            #     # INFO set_command() in MODEL
            #     with closing(sqlite3.connect("twitch_bot.db")) as con:
            #         # con = sqlite3.connect("twitch_bot.db")
            #         cur = con.cursor()
            #         try:
            #             link_exists = cur.execute('''SELECT l.linktext FROM links l
            #                                             JOIN commands c ON l.command_id = c.uid
            #                                             JOIN channels ch ON c.channel_id = ch.uid
            #                                             WHERE LOWER(c.name) = (?) AND ch.name = (?)
            #                                             ''',
            #                                       (args[0].lstrip("!").lower(), self.channel))
            #
            #             cmd_link = link_exists.fetchone()[0]
            #             # INFO set_command() in MODEL
            #
            #             if cmd_link:
            #                 await msg.reply(cmd_link)
            #
            #         except sqlite3.Error as e:
            #             print(f'An error occurred: {e}')

    async def leavemsg(self, msg: ChatMessage):

        args = msg.text.split(" ", 2)
        if not len(args) == 3:
            return await msg.reply("it looks like you used this command incorrectly, did you forget your message?")

        username, message = args[1], args[2]
        # TODO - implement regex instead of below
        if len(args) == 3 and msg.text.startswith("!") and args[0] == "!leavemsg" and args[1].startswith("@") and args[
            1] != msg.user.name:
            await self.db.leave_message(msg)
            # async with self.lock:
            #     # INFO leave_message() in MODEL
            #     with closing(sqlite3.connect("twitch_bot.db")) as con:
            #         cur = con.cursor()
            #         # url = "https://api.twitch.tv/helix/users?login="+args[1][1]
            #         # url = "http://localhost/users?login="+args[1][1]
            #         # res = requests.get(url)
            #         try:
            #             if cur.execute('SELECT COUNT (`sender_id`) FROM messages WHERE sender_id = ?',
            #                            (msg.user.name,)).fetchone()[0] < 3:
            #
            #                 print(f'{msg.user.name}, {args[1][1:]}, {args[2]}')
            #                 cur.execute(
            #                     'INSERT INTO messages (`sender_id`, `receiver_id`, `messagetext`) VALUES (?,?,?)',
            #                     (msg.user.name, args[1][1:].lower(), args[2]))
            #                 con.commit()
            #                 # INFO leave_message() in MODEL
            #             else:
            #                 await msg.reply("""3 msg limit reached, msgs are deleted after each stream ends or
            #                 once delivered""")
            #         except sqlite3.Error as e:
            #             print(f'An error occurred: {e}')

    # INFO - CHECK USER EXISTS - https://dev.twitch.tv/docs/api/reference/#get-users
    async def notify_user(self, msg: ChatMessage):
        user_msgs_count = await self.db.notify(msg)
        # async with self.lock:
        #     # INFO notify() in MODEL
        #     with closing(sqlite3.connect("twitch_bot.db")) as con:
        #         cur = con.cursor()
        #
        #         user_msgs_count = cur.execute('SELECT COUNT(sender_id), sender_id '
        #                                       'FROM messages '
        #                                       'WHERE receiver_id = ? '
        #                                       'GROUP BY sender_id',
        #                                       (msg.user.name,)).fetchall()
        # INFO notify() in MODEL
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
