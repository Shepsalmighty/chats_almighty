# from twitch_bot.model.database_interface import DataBaseInterface as db
from dataclasses import dataclass
from gettext import textdomain

import pytest
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

    def reply(self, txt):
        pass


@dataclass
class Test_Cmd(Test_ChatMessage):
    parameter: str

    def __init__(self, text, user):
        super().__init__(text, user)
        self.parameter = self.text

    # INFO @pytest.mark.asyncio lets us use pytest with async


@pytest.mark.asyncio
async def test_getmsg(test_db):
    # Arrange
    sut = DataBaseInterface(target_channel="test_channel", file_path=test_db)

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
async def test_leavemsg(test_db):
    # Arrange
    sut = DataBaseInterface(target_channel="test_channel", file_path=test_db)

    # user: test_user leaves a message for sheps
    test_user = MyTestChatUser("test_user")
    test_msg = Test_ChatMessage("!leavemsg @sheps test message", test_user)

    # user: sheps retrieves a message from test_user
    test_receiver = MyTestChatUser("sheps")
    get_message = Test_ChatMessage("!getmsg @test_user", test_receiver)

    # user: no_msgs tries to retrieve messages when they have none
    user_no_msgs = MyTestChatUser("no_msgs")
    no_msgs_chat = Test_ChatMessage("!getmsg", user_no_msgs)

    # Action
    # send a message
    await sut.leave_message(test_msg)
    message_success = await sut.get_message(get_message)
    no_messages_check = await sut.get_message(no_msgs_chat)

    # Assert
    assert (message_success[0] == "From @test_user: test message")
    assert len(no_messages_check) == 0


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


# TODO add tests for link_command // set_command

@pytest.mark.asyncio
async def test_set_command(test_db):
    # Arrange
    sut = DataBaseInterface(target_channel="test_channel", file_path=test_db)

    # user: test_user leaves a message for sheps
    test_user = MyTestChatUser("test_channel")
    test_msg = Test_Cmd(text="!set !discord test message", user=test_user)

    command_call = Test_ChatMessage(text="!discord", user=test_user)

    # Action
    await sut.set_command(test_msg)
    command_exists = await sut.get_link(command_call)

    # Assert

    assert command_exists[1] == "test message"
