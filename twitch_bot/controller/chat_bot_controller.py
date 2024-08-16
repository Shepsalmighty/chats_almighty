import asyncio
from twitch_bot.view.twitch_chat_view import TwitchChatView

#INFO the controller determiens how the view+model work together
class ChatBotController:

    def __init__(self, client_id, client_secret, path, target_channel):

        #INFO the model defines how we interact with data (like using a db or storing stuff in files)
        self.model = None #TODO <--- DB etc

        #INFO the view defines all the user interactions (via twitch chat in this case)
        self.view = TwitchChatView(client_id, client_secret, path, target_channel)

    def run(self):
        asyncio.run(self.view.run())


