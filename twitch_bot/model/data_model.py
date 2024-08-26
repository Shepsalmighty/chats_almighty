class Channel:
    # this models an entry in the data table
    def __init__(self, uid, channel_name):
        #INFO Instance variables make up our columns, primary key = uid and on and on next column being channel_name
        self.uid = uid
        self.channel_name = channel_name

#INFO channel ojbects (row1) represent a row in the database table
row1 = Channel(69, "Sea_of_Tranquility")

class LinkCommand:
    def __init__(self, uid, channel_id, command_id, link):
        self.uid = uid
        self.channel_id = channel_id
        self.command_name = command_id
        self.link = link

#no longer needed as Command can reference the command name and which channel it belongs to  
# class AllowedCommands:
#     def __init__(self, uid, command_id, channel_id):
#         self.uid = uid
#         self.channel_id = channel_id
#         self.command_name = command_id

class Command:
    def __init__(self, uid, channel_id, command_name):
        self.uid = uid
        self.channel_id = channel_id
        self.command_name = command_name



print(dir(row1))