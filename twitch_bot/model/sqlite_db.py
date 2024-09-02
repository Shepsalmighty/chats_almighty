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
        CREATE TABLE IF NOT EXISTS channel(
            uid INTEGER NOT NULL,
            channel_name TEXT NOT NULL,
            PRIMARY KEY (`uid`),
            FOREIGN KEY (`channel_name`)) 
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS command_links(
            uid INTEGER NOT NULL, 
            channel_id INTEGER NOT NULL,
            command_id INTEGER NOT NULL,
            link TEXT NOT NULL,
            PRIMARY KEY (`uid`),
            FOREIGN KEY channel_id REFERENCES channel(`uid`),
            FOREIGN KEY command_id REFERENCES command_name(`uid`))
            """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS command_name(
            uid INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            command_name TEXT NOT NULL,
            PRIMARY KEY (`uid`),
            FOREIGN KEY channel_id REFERENCES channel(`uid`))
        """)

if __name__ == "__main__":
    DBMigration().create_tables()


