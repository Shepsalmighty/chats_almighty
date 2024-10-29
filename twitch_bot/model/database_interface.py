import asyncio
import sqlite3
from contextlib import closing


# TODO: use the engine (created in __init___) to implement the class methods below
# TODO look at sqlalchemy sessions/session objects
#
class DataBaseInterface:

    def __init__(self, target_channel, file_path):
        self.lock = asyncio.Lock()
        self.channel = target_channel
        self.db_path = file_path

    async def command_exists(self, msg):
        args = msg.text.split(" ", 1)

        async with self.lock:
            with closing(sqlite3.connect(self.db_path)) as con:
                # if msg.text.startswith("!"):
                #     args = msg.text.split(" ", 1)

                con = sqlite3.connect(self.db_path)
                cur = con.cursor()
                command_exists = cur.execute('''SELECT LOWER(name) FROM commands WHERE name = ?
                                                        AND channel_id = (SELECT uid FROM channels WHERE name = (?))''',
                                             (args[0].lstrip("!").lower(), self.channel)).fetchone()
                return command_exists

    async def set_command(self, cmd):
        args = cmd.parameter.split(" ", 1)

        async with self.lock:
            with closing(sqlite3.connect(self.db_path)) as con:
                cur = con.cursor()
                try:
                    if cur.execute('SELECT COUNT (`name`) FROM channels').fetchone()[0] == 0:
                        cur.execute('INSERT INTO channels (`name`) VALUES (?)', (self.channel,))
                        con.commit()

                    command_id = cur.execute('''
                    INSERT OR REPLACE INTO commands (`name`, `channel_id`)
                    VALUES (?, (SELECT uid FROM channels WHERE name = ?))
                    RETURNING uid''',
                                             (args[0].lstrip("!").lower(), self.channel))
                    cur.execute('''
                    INSERT OR REPLACE INTO links (`command_id`, `linktext`)
                    VALUES (?, ?)''', (command_id.fetchone()[0], args[1],))

                    con.commit()

                except sqlite3.Error as e:
                    print(f'An error occurred: {e}')

    async def get_link(self, msg):
        args = msg.text.split(" ", 1)
        if len(args) < 2:
            await msg.reply("command set incorrectly, did you forget to add the link?")
        else:
            async with self.lock:
                with closing(sqlite3.connect(self.db_path)) as con:
                    cur = con.cursor()
                    try:
                        link_exists = cur.execute('''SELECT l.linktext FROM links l
                                                                    JOIN commands c ON l.command_id = c.uid
                                                                    JOIN channels ch ON c.channel_id = ch.uid
                                                                    WHERE LOWER(c.name) = (?) AND ch.name = (?)
                                                                    ''',
                                                  (args[0].lstrip("!").lower(), self.channel))

                        cmd_link = link_exists.fetchone()[0]
                        # INFO set_command() in MODEL

                        await msg.reply(cmd_link)
                        return cmd_link

                    except sqlite3.Error as e:
                        print(f'An error occurred: {e}')

    async def leave_message(self, msg):
        args = msg.text.split(" ", 2)
        async with self.lock:
            with closing(sqlite3.connect(self.db_path)) as con:
                cur = con.cursor()
                # url = "https://api.twitch.tv/helix/users?login="+args[1][1]
                # url = "http://localhost/users?login="+args[1][1]
                # res = requests.get(url)
                try:
                    if cur.execute('SELECT COUNT (`sender_id`) FROM messages WHERE sender_id = ?',
                                   (msg.user.name,)).fetchone()[0] < 20:
                        # print(f'{msg.user.name}, {args[1][1:]}, {args[2]}')
                        cur.execute(
                            'INSERT INTO messages (`sender_id`, `receiver_id`, `messagetext`) VALUES (?,?,?)',
                            (msg.user.name, args[1][1:].lower(), args[2]))
                        con.commit()

                except sqlite3.Error as e:
                    print(f'An error occurred: {e}')

    async def notify(self, msg):
        async with self.lock:
            with closing(sqlite3.connect(self.db_path)) as con:
                cur = con.cursor()

                user_msgs_count = cur.execute('SELECT COUNT(sender_id), sender_id '
                                              'FROM messages '
                                              'WHERE receiver_id = ? '
                                              'GROUP BY sender_id',
                                              (msg.user.name,)).fetchall()
                return user_msgs_count

    async def get_message(self, msg):
        # if msg.text.startswith("!getmsg")
        async with self.lock:
            with closing(sqlite3.connect(self.db_path)) as con:
                cur = con.cursor()
                target = cur.execute('SELECT receiver_id FROM messages')
                users_with_msgs = set()
                for name in target:
                    users_with_msgs.add(name[0])

                sender_names = set()
                sender_id = cur.execute('SELECT sender_id FROM messages WHERE receiver_id = ?', (msg.user.name,))

                for name in sender_id:
                    sender_names.add(name[0])

                args = msg.text.split(" ", 1)
                msg_list = []

                if len(args) > 1 and args[1].lstrip("@").lower() in sender_names:
                    user_name = str(msg.user.name)
                    messages = cur.execute(
                        'SELECT messagetext, uid FROM messages WHERE receiver_id = ? AND sender_id = ? ORDER BY uid ASC',
                        (user_name.lower(), args[1].lstrip("@").lower())).fetchall()

                    for msgs in messages:
                        #
                        msg_list.append(f"From {args[1]}: {msgs[0]}")
                        # await msg.reply(f"From {args[1]}: {msgs[0]}")
                        cur.execute('DELETE FROM messages WHERE uid = ?', (msgs[1],))  # (messages[1],)
                    sender_names.remove(args[1].lstrip("@").lower())
                    con.commit()
                return msg_list
