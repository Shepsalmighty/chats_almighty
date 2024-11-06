# from twitch_bot.model.database_interface import DataBaseInterface as db
from dataclasses import dataclass
from gettext import textdomain

import pytest
#from sqlalchemy.sql.coercions import expect

from twitch_bot.model.database_interface import DataBaseInterface


# INFO https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/

# INFO - making two data classes to simulate chat users and chat messages with @dataclass decorator
@dataclass
class MyTestChatUser:
    name: str


@dataclass
class Test_ChatMessage:
    text: str
    user: MyTestChatUser

    async def reply(self, txt):
        pass


@dataclass
class Test_Cmd(Test_ChatMessage):
    # parameter: str
    @property
    def parameter(self):
        print(f"\n\n Test_command: {self.text[:], self.text.split(maxsplit=1)[1], self.text}")
        return self.text.split(maxsplit=1)[1]
    # def __init__(self, text, user):
    #     super().__init__(text, user)
    #     # self.parameter = self.text
    #     self.parameter = self.text.split(maxsplit=1)[1]
    #     # self.user.name = user


# INFO @pytest.mark.asyncio lets us use pytest with async
@pytest.mark.asyncio
async def test_getmsg(test_db):
    # Arrange
    sut = DataBaseInterface(target_channel="target_channel", file_path=test_db)

    # creating user: test_user
    test_user = MyTestChatUser("test_user")
    test_message = Test_ChatMessage("!getmsg", test_user)

    # user: test_user leaves a message for sheps
    test_msg = Test_ChatMessage("!leavemsg @sheps test message", test_user)

    # creating user: sheps and their !getmsg call message
    user_to_be_notified = MyTestChatUser("sheps")
    get_message_call = Test_ChatMessage("!getmsg test_user", user_to_be_notified)

    # Action
    # user: test_user leaves a message for user: sheps
    await sut.leave_message(test_msg)
    # a user with no messages calls !getmsg
    no_msg_call = await sut.get_message(test_message)

    # a user with messages calls the wrong stored username
    wrong_name_used = Test_ChatMessage("!getmsg @stderr", user_to_be_notified)

    # a user with messages calls !getmsg using the wrong user name
    getmsg_call_wrong_name = await sut.get_message(wrong_name_used)

    # user: sheps enters chat and calls !getmsg
    getting_message = await sut.get_message(get_message_call)

    # Assert
    assert len(no_msg_call) == 0
    assert len(getmsg_call_wrong_name) == 0
    assert getting_message[0] == 'From test_user: test message'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sender, receiver, msg_text, channel, expect_success",
    [
        ("test_user", "sheps", "!leavemsg @sheps test message", "test_channel", True),
        ("test_user", "sheps", "!leavemsg @SHEPS test message", "test_channel", True),
        ("test_user", "sheps", "!leavemsg @SHEPS test message", "test_channel", True),
        ("new_user", "sheps", "!leavemsg @SHEPS test message", "new_channel", False),
        # test user leaves a fork bomb for user sheps
        ("test_user", "sheps", "!leavemsg @sheps :(){ :|:& };:", "test_channel", True),
        ("test_user", "sheps", "!leavemsg @sheps DROP TABLE users;", "test_channel", True),

    ],
    ids=["test_user, leaves a message for user: sheps",
         "test_user leaves a message for sheps but uses all caps",
         "similar test",
         "a user tries to leave a message on the wrong channel",
         "test_user tries to leave a fork bomb for user sheps",
         "test_user tries to sql inject"]
)
async def test_leavemsg(test_db, sender, receiver, msg_text, channel, expect_success):
    # Arrange
    # sut = DataBaseInterface(target_channel="test_channel", file_path=test_db)
    sut = DataBaseInterface(target_channel=channel, file_path=test_db)

    # user: test_user leaves a message for sheps
    test_user = MyTestChatUser(sender)
    test_msg = Test_ChatMessage(msg_text, test_user)
    # test_user = MyTestChatUser("test_user")
    # test_msg = Test_ChatMessage("!leavemsg @sheps test message", test_user)

    # user: sheps retrieves a message from test_user
    test_receiver = MyTestChatUser(receiver)
    get_message = Test_ChatMessage("!getmsg @test_user", test_receiver)
    # test_receiver = MyTestChatUser("sheps")
    # get_message = Test_ChatMessage("!getmsg @test_user", test_receiver)

    # user: no_msgs tries to retrieve messages when they have none
    user_no_msgs = MyTestChatUser("no_msgs")
    no_msgs_chat = Test_ChatMessage("!getmsg", user_no_msgs)

    # message_actual = " ".join(msg_text.split(" ", maxsplit=2))[2:]
    message_actual = " ".join(msg_text.split(" ", maxsplit=2)[2:])
    # Action
    # send a message
    await sut.leave_message(test_msg)
    message_success = await sut.get_message(get_message)
    no_messages_check = await sut.get_message(no_msgs_chat)

    # Assert
    if expect_success:
        assert (message_success[0] == f"From @test_user: {message_actual}")
    else:
        assert len(message_success) == 0 or (message_success[0] != f"From @test_user: {message_actual}")


@pytest.mark.asyncio
async def test_notify_user(test_db):
    # Arrange
    sut = DataBaseInterface(target_channel="test_channel", file_path=test_db)

    # user: test_user leaves a message for sheps
    test_user = MyTestChatUser("test_user")
    test_msg = Test_ChatMessage("!leavemsg @sheps test message", test_user)
    user_with_no_msgs = MyTestChatUser("user_with_no_msgs")

    # user: sheps enters chat and says hello, this should trigger the notify function
    user_to_be_notified = MyTestChatUser("sheps")
    msg_from_user_to_be_notified = Test_ChatMessage("hello strimmer", user_to_be_notified)

    # a user with no messages, writes in chat
    user_has_no_msgs = Test_ChatMessage("this user has no messages", user_with_no_msgs)

    # Action
    # a message is left for user: sheps
    await sut.leave_message(test_msg)
    # user: sheps writes in chat
    notify_msgs = await sut.notify(msg_from_user_to_be_notified)

    # user with no messages writes in chat
    notify_user_no_msgs = await sut.notify(user_has_no_msgs)

    # Assert
    assert notify_msgs[0] == (1, 'test_user')
    assert len(notify_user_no_msgs) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user, msg, cmd_called, target_channel, expected_status",
    [
        ("test_user", "!set !discord test message", "!discord", "target_channel", True),
        # ("test_user", "!set !discord", "!discord", "target_channel", False)
    ],
    ids=["set discord link to test message"]
    # ,"set command with no args"]
)
async def test_set_command(test_db, user, msg, cmd_called, target_channel, expected_status):
    # Arrange
    sut = DataBaseInterface(target_channel=target_channel, file_path=test_db)

    # user: test_user sets their discord command to return "test message"
    test_user = MyTestChatUser(user)
    test_msg = Test_Cmd(text=msg, user=test_user)

    # someone calls the !cmd in question
    command_call = Test_ChatMessage(text=cmd_called, user=test_user)

    # assigning the returned msg to a var for assertion comparisons
    message_actual = " ".join(msg.split(" ", maxsplit=2)[2:])

    # Action
    # channel user sets discord to be "test message"
    await sut.set_command(test_msg)
    # someone in chat calls !discord
    command_exists = await sut.get_link(command_call)

    # Assert
    if expected_status:
        assert command_exists == message_actual
    else:
        # assert len(command_exists) == 0
        assert len(await sut.get_link(command_call)) == 0

# TODO add tests for link_command
# @pytest.mark.asyncio
# async def test_linkcmd(test_db):
