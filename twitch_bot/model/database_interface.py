from html.parser import commentclose

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from twitch_bot.model.data_model import Channel, LinkCommand
# from twitch_bot.view.twitch_chat_view import TwitchChatView
# from twitch_bot.view.twitch_chat_view import chat_view_instance
from twitch_bot.controller.chat_bot_controller import TwitchChatView

#TODO: use the engine (created in __init___) to implement the class methods below
#TODO look at sqlalchemy sessions/session objects

class DataBase:

    def __init__(self, session):
        self.session = session

    def add_link(self, channel, command_name, link):
        # self.session.add(LinkCommand(command_name=command_name))
        # link = TwitchChatView.user_values.get(command_name)

        # Konrad example using global var to get the dict into this module
        # link = chat_view_instance.user_values.get(command_name)
        # self.session.add(LinkCommand(channel=channel))
        self.session.add(LinkCommand(link=link))
        self.session.commit()

    def get_link(self, command_name):
        q = self.session.query(LinkCommand).select_from(LinkCommand).filter(LinkCommand.command_name==command_name)
        return q.all()


    def add_channel(self, channel_name):
        self.session.add(Channel(channel_name=channel_name))
        self.session.commit()

    def get_channel(self, channel_name):
        q = self.session.query(Channel).select_from(Channel).filter(Channel.channel_name == channel_name)
        return q.all()

    def allowed_command(self, channel, command_name):
        pass

#TODO: add later
    # def add_message(self, channel, message):
    #     pass

    def add_command(self, channel, command_name):
        pass

