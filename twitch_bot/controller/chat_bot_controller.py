import asyncio
from twitch_bot.view.twitch_chat_view import TwitchChatView
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from twitch_bot.model.database_interface import DataBase


#INFO the controller determiens how the view+model work together
class ChatBotController:

    def __init__(self, client_id, client_secret, path, target_channel):

        #INFO the model defines how we interact with data (like using a db or storing stuff in files)
        self.model = None #TODO <--- DB etc

        #INFO the view defines all the user interactions (via twitch chat in this case)
        self.view = TwitchChatView(client_id, client_secret, path, target_channel)

        #INFO create a relative path to DB for SQLalchemy
        self.engine = create_engine("sqlite:///twitch_bot.db", echo=True)



    def run(self):
        # NOTE every transaction with the DataBase runs inside this, so in db_interface, everything is executed within this session
        with Session(self.engine) as session:
            # self.model = DataBase(session)
            # self.model.add_channel("Sea_of_Tranquility")
            # self.model.add_link("Sea_of_Tranquility", "discord", "foo")

            asyncio.run(self.view.run())
            session.commit()

