CREATE TABLE IF NOT EXISTS channel(
            uid INTEGER NOT NULL,
            channel_name TEXT NOT NULL,
            PRIMARY KEY (`uid`));
			
CREATE TABLE IF NOT EXISTS command_name(
            uid INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            command_name TEXT NOT NULL,
            PRIMARY KEY (`uid`),
            FOREIGN KEY (`channel_id`) REFERENCES channel(`uid`));
			
CREATE TABLE IF NOT EXISTS command_links(
            uid INTEGER NOT NULL,
            command_id INTEGER NOT NULL,
            link TEXT NOT NULL,
            PRIMARY KEY (`uid`),
            FOREIGN KEY (`command_id`) REFERENCES command_name(`uid`));

'SELECT uid FROM channel WHERE channel_name = "test";
INSERT INTO command_name (channel_uid, command_name) VALUES (?,?) RETURNING (uid);

