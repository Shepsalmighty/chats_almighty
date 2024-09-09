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
			
			
			
INSERT INTO channels (name) VALUES ("test");
INSERT INTO commands (channel_id, name) VALUES ((SELECT uid FROM channels WHERE name = "test"), "test command");
INSERT INTO links (linktext, command_id) VALUES ("test link", (SELECT uid FROM commands WHERE name = "test command"));

-- get uid from channel
SELECT uid FROM channels WHERE name = "test";

-- get uid from commmand_name 
SELECT uid from commands WHERE name = "test command"




