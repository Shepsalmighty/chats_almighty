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

    async def on_message(self, msg: ChatMessage):
        # print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')

        if msg.text.startswith("!"):
            args = msg.text.split(" ", 1)

            # print(args[0])
            con = sqlite3.connect("twitch_bot.db")
            cur = con.cursor()
            command_exists = cur.execute('''SELECT LOWER(name) FROM commands WHERE name = ? 
                                                                 AND channel_id = (SELECT uid FROM channels WHERE name = (?))''',
                                         (args[0].lstrip("!").lower(), self.channel)).fetchone()

            if args[0] == "!set" or args[0] == '!leavemsg' or args[0] == '!getmsg':
                pass
            elif command_exists:
                await self.link_command(msg)
            elif command_exists is None and msg.user.name == self.channel:
                await msg.reply(f"add a link to your {msg.text} using \"!set !{msg.text.lstrip("!")} link\"   ")

            elif command_exists is None and msg.user.name != self.channel:
                await msg.reply(f"no {msg.text} link yet")

            con.close()
        else:
            print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
        await self.get_msg(msg)

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
            # await self.lock.acquire()
            async with self.lock:

                # creating connection to db and cursor objects
                with closing(sqlite3.connect("twitch_bot.db")) as con:
                    cur = con.cursor()
                    try:
                        if cur.execute('SELECT COUNT (`name`) FROM channels').fetchone()[0] == 0:
                            cur.execute('INSERT INTO channels (`name`) VALUES (?)', (self.channel,))
                            con.commit()

                        command_id = cur.execute('''
                        INSERT OR REPLACE INTO commands (`name`, `channel_id`) 
                        VALUES (?, (SELECT uid FROM channels WHERE name = ?)) 
                        RETURNING uid''',
                                                 (args[0].lstrip("!").lower(), self.channel))
                        cur.execute('''
                        INSERT OR REPLACE INTO links (`command_id`, `linktext`) 
                        VALUES (?, ?)''',
                                    (command_id.fetchone()[0], args[1],))
                        con.commit()

                    except sqlite3.Error as e:
                        print(f'An error occurred: {e}')


        else:
            await cmd.reply("you cannot change bot settings")

    async def link_command(self, msg: ChatMessage):
        # if cmd.user.name == self.channel:
        # self.allowed_user_values.append(cmd.parameter[1])

        if msg.text.startswith("!"):
            args = msg.text.split(" ", 1)

            # if (cmd.text.lstrip("!") == command_exists[0]):
            async with self.lock:
                with closing(sqlite3.connect("twitch_bot.db")) as con:
                    # con = sqlite3.connect("twitch_bot.db")
                    cur = con.cursor()
                    try:
                        link_exists = cur.execute('''SELECT l.linktext FROM links l
                                                        JOIN commands c ON l.command_id = c.uid
                                                        JOIN channels ch ON c.channel_id = ch.uid
                                                        WHERE LOWER(c.name) = (?) AND ch.name = (?)
                                                        ''',
                                                  (args[0].lstrip("!").lower(), self.channel))

                        cmd_link = link_exists.fetchone()[0]

                        if cmd_link:
                            await msg.reply(cmd_link)

                    except sqlite3.Error as e:
                        print(f'An error occurred: {e}')

    async def leavemsg(self, msg: ChatMessage):

        args = msg.text.split(" ", 2)
        if not len(args) == 3:
            return await msg.reply("it looks like you used this command incorrectly, did you forget your message?")

        username, message = args[1], args[2]
        # TODO - implement regex instead of below
        if len(args) == 3 and msg.text.startswith("!") and args[0] == "!leavemsg" and args[1].startswith("@"):
            async with self.lock:
                with closing(sqlite3.connect("twitch_bot.db")) as con:
                    cur = con.cursor()
                    # url = "https://api.twitch.tv/helix/users?login="+args[1][1]
                    # url = "http://localhost/users?login="+args[1][1]
                    # res = requests.get(url)
                    try:
                        if cur.execute('SELECT COUNT (`sender_id`) FROM messages WHERE sender_id = ?',
                                       (msg.user.name,)).fetchone()[0] < 20:

                            print(f'{msg.user.name}, {args[1][1:]}, {args[2]}')
                            cur.execute(
                                'INSERT INTO messages (`sender_id`, `receiver_id`, `messagetext`) VALUES (?,?,?)',
                                (msg.user.name, args[1][1:].lower(), args[2]))
                            con.commit()
                        else:
                            await msg.reply("""3 msg limit reached, msgs are deleted after each stream ends or
                            once delivered""")
                    except sqlite3.Error as e:
                        print(f'An error occurred: {e}')

    # INFO - CHECK USER EXISTS - https://dev.twitch.tv/docs/api/reference/#get-users

    async def get_msg(self, msg: ChatMessage):

        async with self.lock:
            with closing(sqlite3.connect("twitch_bot.db")) as con:
                cur = con.cursor()
                # message_count = cur.execute('SELECT COUNT(*) FROM messages WHERE receiver_id = ?', (msg.user.name,))
                target = cur.execute('SELECT receiver_id FROM messages')
                users_with_msgs = set()
                for name in target:
                    users_with_msgs.add(name[0])

                sender_names = set()
                sender_id = cur.execute('SELECT sender_id FROM messages WHERE receiver_id = ?', (msg.user.name,))

                for name in sender_id:
                    sender_names.add(name[0])

        args = msg.text.split(" ", 1)
        # print(users_with_msgs, self.users_notified)
        if msg.user.name in users_with_msgs and msg.user.name not in self.users_notified and not msg.text.startswith(
                "!getmsg"):
            await msg.reply(
                f'you have {len(sender_names)} messages stored from {sender_names}, to get a message use !getmsg @username')
            async with self.notified_lock:
                self.users_notified.add(msg.user.name)


        elif msg.user.name in users_with_msgs and len(args) == 1 and args[1].lstrip(
                "@") not in sender_names:  and msg.user.name not in self.users_notified:
            await msg.reply(
                f'To get a message use !getmsg @username. You have {len(sender_names)} messages stored from: {sender_names}')

        elif len(args) > 1 and args[1].lstrip("@").lower() in sender_names:
            user_name = str(msg.user.name)
            async with self.lock:
                with closing(sqlite3.connect("twitch_bot.db")) as con:
                    cur = con.cursor()
                    messages = cur.execute(
                        'SELECT messagetext, uid FROM messages WHERE receiver_id = ? AND sender_id = ? ORDER BY uid ASC',
                        (user_name.lower(), args[1].lstrip("@").lower())).fetchall()
                    for msgs in messages:
                        await msg.reply(f"From {args[1]}: {msgs[0]}")
                        cur.execute('DELETE FROM messages WHERE uid = ?', (msgs[1],))  # (messages[1],)
                    sender_names.remove(args[1].lstrip("@").lower())
                    con.commit()

                # for row in messages:

            # await msg.reply(f'{row[1]} left you a message: {row[0]}')
            # cur.execute('DELETE FROM messages WHERE uid = ?', (row[2],))
            # con.commit()
            # else: pass

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
