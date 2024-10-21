import sqlite3


class DBMigration:
    # INFO: create cursor object to interact with db tables e.g in create_tables
    # cur = self.con.cursor()

    def __init__(self, file_path):
        # connect to db
        self.con = sqlite3.connect(file_path)

    def create_tables(self):
        # INFO: traq reference db https://pastebin.com/enCacTuk
        # INFO: sqlite data types https://sqlite.org/datatype3.html

        # INFO: create cursor object to interact with db tables
        # cur = self.con.cursor()
        cur = self.con.cursor()

        # creating all tables needed if not existing
        cur.execute("""
        CREATE TABLE IF NOT EXISTS channels(
            uid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE)
            """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS commands(
            uid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(channel_id, name),
            FOREIGN KEY (`channel_id`) REFERENCES channels(`uid`))
            """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS links(
            uid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            command_id INTEGER NOT NULL UNIQUE,
            linktext TEXT NOT NULL,
            FOREIGN KEY (`command_id`) REFERENCES commands(`uid`))
            """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            uid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            messagetext TEXT NOT NULL,   
            UNIQUE(sender_id, receiver_id)) 
            """)
        # you need something like ADD CONSTRAINT one_msg_per_pair UNIQUE(sender_id, receiver_id)

        # create index links for tables for more performant queries
        # index for channels table
        cur.execute("""CREATE INDEX IF NOT EXISTS idx_channels_name ON channels(name)""")

        # index for the commands table
        cur.execute("""CREATE INDEX IF NOT EXISTS idx_commands_name_channel_id ON commands(name, channel_id)""")

        # index for the links table
        cur.execute("""CREATE INDEX IF NOT EXISTS idx_links_command_id ON links(command_id)""")

        # self.con.commit()

        # cur.execute("INSERT INTO channels (name) VALUES (\"test\")")
        # cur.execute("INSERT INTO commands (channel_id, name) VALUES ((SELECT uid FROM channels WHERE name = \"test\"), \"test command\")")
        # cur.execute("INSERT INTO links (linktext, command_id) VALUES (\"test link\", (SELECT uid FROM commands WHERE name = \"test command\" AND channels_id = (SELECT name from channels WHERE name = \"test\"))")


if __name__ == "__main__":
    DBMigration().create_tables()
