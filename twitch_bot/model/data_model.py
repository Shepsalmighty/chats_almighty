from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

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
    channel_name: Mapped[str] = mapped_column(String(30))

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
    command_name: Mapped[str] = mapped_column(String(30))

    def __repr__(self) -> str:
        return f"User(uid={self.uid!r}, channel_id={self.channel_id!r}, command_name={self.command_name!r})"


class Command(Base):
    # def __init__(self, uid, channel_id, command_name):
    #     self.uid = uid
    #     self.channel_id = channel_id
    #     self.command_name = command_name
    __tablename__ = "command_name"
    uid: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[str] = mapped_column(String(30), ForeignKey("channel.uid"))
    command_name: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"User(uid={self.uid!r}, channel_id={self.channel_id!r}, command_name={self.command_name!r})"


print(dir(row1))