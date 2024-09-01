from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine



#TODO: error handling e.g. if no uid given or strings empty/NULL
#TODO: consider adding 'relationships' where appropriate to classes/for tables examples in example code here: https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
#NOTE: if storing date/time or timestamps do as 'seconds since Epoch' -stderr (thank later)
#NOTE: we're using pysqlite - IF speed or db blocking the bot becomes an issue we'll need aiosqlite for async shtuffs

class Base(DeclarativeBase):
    pass

class Channel(Base):
    # this models an entry in the data table
    # def __init__(self, uid, channel_name):
    #     #INFO Instance variables make up our columns, primary key = uid and on and on next column being channel_name
    #     self.uid = uid
    #     self.channel_name = channel_name
    __tablename__ = "channel"
    uid: Mapped[int] = mapped_column(primary_key=True)
    channel_name: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"User(uid={self.uid!r}, channel_name={self.channel_name!r})"

# #INFO channel ojbects (row1) represent a row in the database table (this applied as to the classes BEFORE we added SQLalchemy, may be different now - ask Tranq
# row1 = Channel(69, "Sea_of_Tranquility")

class LinkCommand(Base):
    # def __init__(self, uid, channel_id, command_id, link):
    #     self.uid = uid
    #     self.channel_id = channel_id
    #     self.command_name = command_id
    #     self.link = link
    ##############################################################
    __tablename__ = "link_command"

    uid: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channel.uid"))
    command_name: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"User(uid={self.uid!r}, channel_id={self.channel_id!r}, command_name={self.command_name!r})"


class Command(Base):
    # def __init__(self, uid, channel_id, command_name):
    #     self.uid = uid
    #     self.channel_id = channel_id
    #     self.command_name = command_name
    __tablename__ = "command_name"
    uid: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channel.uid"))
    command_name: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"User(uid={self.uid!r}, channel_id={self.channel_id!r}, command_name={self.command_name!r})"





#INFO some examples working with tranq below

# if __name__ == "__main__":
#     # relative path to db file:
#     engine = create_engine("sqlite:///twitch_bot.db", echo=True)

#     #below generates our SCHEMA at once in our target sqlite DB
#     # Base.metadata.create_all(engine)
# if __name__ == "__main__":
#     engine = create_engine("sqlite:///twitch_bot.db", echo=True)
#     c1 = Channel(uid=69, channel_name="shepsalmighty")
#
#     with Session(engine) as session:
#         session.add(c1)
#         # NOTE: in this example below we set uid=69 from sheps to tranq and uid69 would be tranq when committed
#         # c1.channel_name = "Sea_of_Tranquility"
#         session.commit()
