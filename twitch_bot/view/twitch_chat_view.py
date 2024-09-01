# INFO code examples from https://pytwitchapi.dev/en/stable/
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator, UserAuthenticationStorageHelper
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.chat.middleware import StreamerOnly
import asyncio
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

#INFO in the view class all user interactions are defined, it represents the user interface, commands like !discord or !help are part of it
class TwitchChatView:

    USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]


    def __init__(self, client_id, client_secret, path, target_channel):
        self.client_id = client_id
        self.client_secret = client_secret
        self.path = path
        self.channel = target_channel
        self.user_values = {}
        self.allowed_user_values = ["youtube", "discord", "github", "today", "schedule"]

    async def on_message(self, msg: ChatMessage):
        print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')

    async def on_ready(self, ready_event: EventData):
        print('Bot is ready for work, joining channels')
        # join our target channel, if you want to join multiple, either call join for each individually
        # or even better pass a list of channels as the argument
        await ready_event.chat.join_room(self.channel)
        # you can do other bot initialization things in here


    #TODO: add !functions !reply !discord !set etc
    #!set(!example) over writes existing command with channel owners input links etc
    async def set_command(self, cmd: ChatCommand):
        if cmd.user.name == self.channel:
            args = cmd.parameter.split(" ",1)
            if len(args) < 2:
                await cmd.reply("command set incorrectly, did you forget to add the link?")
            elif args[0][1:] in self.allowed_user_values:
                self.user_values[args[0][1:]] = args[1]
            # elif args[0] == "!discord":
            #     self.user_values["discord"] = args[1]
            # elif args[0] == "!youtube":
            #     self.user_values["youtube"] = args[1]
            # elif args[0] == "!today":
            #     self.user_values["today"] = args[1]
            # elif args[0] == "!github":
            #     self.user_values["github"] = args[1]
            # elif args[0] == "!schedule":
            #     self.user_values["schedule"] = args[1]

        else:
           await cmd.reply("you cannot change bot settings")

    async def link_command(self, cmd: ChatCommand):
        if cmd.name in self.user_values:
            await cmd.reply(self.user_values.get(cmd.name))
        elif len(cmd.parameter) == 0 and cmd.user.name == self.channel:
            await cmd.reply(f"add a link to your {cmd.name} using \"!set !{cmd.name} link\"   ")
        elif len(cmd.parameter) >= 0 and cmd.user.name != self.channel:
            await cmd.reply(f"no {cmd.name} link yet")


    # async def discord_command(self, cmd: ChatCommand):
    #     # TODO: TARGET_CHANNEL won't work when the bot has it's own acc as that acc will never be setting params in other peoples chats
    #     print(cmd.name)
    #     if "discord" in self.user_values:
    #         await cmd.reply(self.user_values.get("discord"))
    #     elif len(cmd.parameter) == 0 and cmd.user.name == self.channel:
    #         await cmd.reply("add a link to your discord using \"!set !discord link\"   ")
    #     elif len(cmd.parameter) >= 0 and cmd.user.name != self.channel:
    #         await cmd.reply("no discord link yet")
    #
    # async def youtube_command(self, cmd: ChatCommand):
    #     # TODO: TARGET_CHANNEL won't work when the bot has it's own acc as that acc will never be setting params in other peoples chats
    #     if "youtube" in self.user_values:
    #         await cmd.reply(self.user_values.get("youtube"))
    #     elif len(cmd.parameter) == 0 and cmd.user.name == self.channel:
    #         await cmd.reply("add a link to your youtube using \"!set !discord - paste link here:\"   ")
    #     elif len(cmd.parameter) >= 0 and cmd.user.name != self.channel:
    #         await cmd.reply("no youtube link yet")


#TODO: add some tests

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
        for link in self.allowed_user_values:
            chat.register_command(link, self.link_command)
        # chat.register_command('discord', self.link_command)
        # chat.register_command('youtube', self.link_command)

        # we are done with our setup, lets start this bot up!
        chat.start()

        # lets run till we press enter in the console
        try:
            input('press ENTER to stop\n')
        finally:
            # now we can close the chat bot and the twitch api client
            chat.stop()
            await twitch.close()