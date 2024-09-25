CREATE TABLE IF NOT EXISTS channels(
            uid INTEGER NOT NULL,
            name TEXT NOT NULL UNIQUE,
            PRIMARY KEY (`uid`));
			
CREATE TABLE IF NOT EXISTS commands(
            uid INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            name TEXT NOT NULL,
			UNIQUE (channel_id, name),
            PRIMARY KEY (`uid`),
            FOREIGN KEY (`channel_id`) REFERENCES channels(`uid`));
			
CREATE TABLE IF NOT EXISTS links(
            uid INTEGER NOT NULL,
            command_id INTEGER NOT NULL UNIQUE,
            linktext TEXT NOT NULL,
            PRIMARY KEY (`uid`),
			FOREIGN KEY (`command_id`) REFERENCES commands(`uid`));


CREATE TABLE IF NOT EXISTS messages(
            uid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            messagetext TEXT NOT NULL,
            UNIQUE(sender_id, receiver_id));

			
			
			
--INSERT INTO channels (name) VALUES ("test");
--INSERT INTO commands (channel_id, name) VALUES ((SELECT uid FROM channels WHERE name = "test"), "test command");
--INSERT INTO links (linktext, command_id) VALUES ("test link", (SELECT uid FROM commands WHERE name = "test command"));

--------------------------------------------------------------------------------------------------
--create indexes for performance on often queried fields:

-- Index for the channels table
CREATE INDEX IF NOT EXISTS idx_channels_name ON channels(name);

-- Index for the commands table
CREATE INDEX IF NOT EXISTS idx_commands_name_channel_id ON commands(name, channel_id);

-- Index for the links table
CREATE INDEX IF NOT EXISTS idx_links_command_id ON links(command_id);
---------------------------------------------------------------------------------------------------

-- get uid from channel
--SELECT uid FROM channels WHERE name = "test";

-- get uid from commmand_name // CHECK COMMAND EXISTS FOR CHANNEL
--SELECT uid FROM commands WHERE name = "test command" AND channel_id  = (SELECT uid FROM channels WHERE name = "test")

-- get link from links table where the command id/uid relates 
--SELECT linktext FROM links WHERE command_id = (SELECT uid from commands WHERE name = "test command" AND channel_id  = (SELECT uid FROM channels WHERE name = "test"))

--RETRIEVES LINK 
--SELECT l.linktext FROM links l JOIN commands c ON l.command_id = c.uid JOIN channels ch ON c.channel_id = ch.uid
--WHERE c.name = 'test command' AND ch.name = 'test';

--INSERT LINK INTO TABLE (FOR !SET)
--INSERT INTO links (linktext, command_id) VALUES ("test link", (SELECT uid FROM commands WHERE name = "test command"));

--INSERT INTO links VALUES "example link text"; INSERT INTO commands VALUES "command name"; SELECT
