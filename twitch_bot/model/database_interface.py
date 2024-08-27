from sqlalchemy import create_engine

#TODO: use the engine (created in __init___) to implement the class methods below
#TODO look at sqlalchemy sessions/session objects

class DataBase:

    def __init__(self, engine):
        self.engine = create_engine("sqlite:///twitch_bot.db", echo=True)

    def add_link(self, channel, command_name, link):
        pass

    def allowed_command(self, channel, command_name):
        pass

#TODO: add later
    # def add_message(self, channel, message):
    #     pass

    def add_command(self, channel, command_name):
        pass