from os import getenv
from dotenv import load_dotenv
#from controller.chat_bot_controller import ChatBotController
from twitch_bot.controller.chat_bot_controller import ChatBotController
from pathlib import Path
from twitch_headless_auth import twitch_setup
import asyncio

# INFO this is the starting point of our program, it creates the controller which glues the model+view components together
if __name__ == '__main__':
    load_dotenv()
    asyncio.run(twitch_setup())
    chat_bot = ChatBotController(getenv("TWITCH_CLIENT_ID"), getenv("TWITCH_CLIENT_SECRET"),
                                 Path("dont_show_on_stream.json"),
                                 "shepsalmighty")

    chat_bot.run()
