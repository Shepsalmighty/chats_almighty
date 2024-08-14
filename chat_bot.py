# INFO code examples from https://pytwitchapi.dev/en/stable/
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator, UserAuthenticationStorageHelper
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import asyncio
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
TARGET_CHANNEL = 'shepsalmighty'


# this will be called when the event READY is triggered, which will be on bot start
async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    # join our target channel, if you want to join multiple, either call join for each individually
    # or even better pass a list of channels as the argument
    await ready_event.chat.join_room(TARGET_CHANNEL)
    # you can do other bot initialization things in here


# this will be called whenever a message in a channel was sent by either the bot OR another user
async def on_message(msg: ChatMessage):
    print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')


# this will be called whenever someone subscribes to a channel
async def on_sub(sub: ChatSub):
    print(f'New subscription in {sub.room.name}:\\n'
          f'  Type: {sub.sub_plan}\\n'
          f'  Message: {sub.sub_message}')


# this will be called whenever the !reply command is issued
async def test_command(cmd: ChatCommand):
    if len(cmd.parameter) == 0:
        await asyncio.sleep(1.5)
        await cmd.reply('you did not tell me what to reply with')
    else:
        await asyncio.sleep(1.5)
        await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')

async def help_command(cmd: ChatCommand):
    if len(cmd.parameter) == 0:
        await cmd.reply("you can !set the following commands: !today, !discord, !socials, !vimbad, !noArch, !Archbad "
                        "for more information about each command type !help !command "
                        "e.g. \"!help !discord \""
                        "IMPORTANT - !set overwrites previous entries")
    elif cmd.parameter == "!discord":
        await cmd.reply("you can add your discord link by using \"!set !discord >link<\". IMPORTANT !set will overwrite previous links")
    elif cmd.parameter == "!today":
        await cmd.reply("you can tell your community what you're upto today with \"!set !today \"description\". IMPORTANT !set will overwrite previous entries.")
    elif cmd.parameter == "!vimbad":
        await cmd.reply("it's true. vim = bad")

#TODO: write a !set function/cmd that overwrites previous entries

#TODO: add discord link

async def discord_link(cmd: ChatCommand):
    #TODO: TARGET_CHANNEL won't work when the bot has it's own acc as that acc will never be setting params in other peoples chats
    if len(cmd.parameter) == 0 and cmd.user.name == TARGET_CHANNEL:
        user_discord = input("add a link to your discord using !add >your link here<")
    return user_discord
# this is where we set up the bot
async def run():
    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(getenv("TWITCH_CLIENT_ID"), getenv("TWITCH_CLIENT_SECRET"))
    # auth = UserAuthenticator(twitch, USER_SCOPE)
    # token, refresh_token = await auth.authenticate()
    # await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)
    helper = UserAuthenticationStorageHelper(twitch, USER_SCOPE, storage_path=Path("dont_show_on_stream.json"))
    await helper.bind()

    # create chat instance
    chat = await Chat(twitch)

    # register the handlers for the events you want

    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)
    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, on_message)
    # listen to channel subscriptions
    chat.register_event(ChatEvent.SUB, on_sub)
    # there are more events, you can view them all in this documentation

#INFO you must directly register commands and their handlers, this will register the !reply command
    chat.register_command('reply', test_command)
    chat.register_command('help', help_command)
    chat.register_command('discord', discord_link)


    # we are done with our setup, lets start this bot up!
    chat.start()

    # lets run till we press enter in the console
    try:
        input('press ENTER to stop\n')
    finally:
        # now we can close the chat bot and the twitch api client
        chat.stop()
        await twitch.close()

# pulls client_id and client_secret from .env to be used by ansyncio.run
load_dotenv()
# lets run our setup
asyncio.run(run())