from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from twitch_bot.model.data_model import Channel

#TODO: use the engine (created in __init___) to implement the class methods below
#TODO look at sqlalchemy sessions/session objects

class DataBase:

    def __init__(self, session):
        self.session = session



    def add_link(self, channel, command_name, link):
        pass
        # with session:
        # pass

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

