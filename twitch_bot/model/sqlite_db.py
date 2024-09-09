import sqlite3




class DBMigration:
    # INFO: create cursor object to interact with db tables e.g in create_tables
    # cur = self.con.cursor()

    def __init__(self):
        # connect to db
        self.con = sqlite3.connect("twitch_bot.db")



    def create_tables(self):
        #INFO: traq reference db https://pastebin.com/enCacTuk
        #INFO: sqlite data types https://sqlite.org/datatype3.html

        # INFO: create cursor object to interact with db tables
        # cur = self.con.cursor()
        cur = self.con.cursor()

        # creating all tables needed if not existing
        cur.execute("""
        CREATE TABLE IF NOT EXISTS channels(
            uid INTEGER NOT NULL,
            name TEXT NOT NULL UNIQUE,
            PRIMARY KEY (`uid`))
            """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS commands(
            uid INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            UNIQUE (channel_id, name)
            PRIMARY KEY (`uid`),
            FOREIGN KEY (`channel_id`) REFERENCES channels(`uid`))
            """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS links(
            uid INTEGER NOT NULL,
            command_id INTEGER NOT NULL UNIQUE,
            linktext TEXT NOT NULL,
            PRIMARY KEY (`uid`),
            FOREIGN KEY (`command_id`) REFERENCES commands(`uid`))
            """)
        # self.con.commit()



if __name__ == "__main__":
    print("we got here")
    DBMigration().create_tables()
    print("here too")




