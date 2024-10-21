# from twitch_bot.model.database_interface import DataBaseInterface as db
from dataclasses import dataclass
import pytest
from twitch_bot.model.database_interface import DataBaseInterface


# INFO https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/

@dataclass
class MyTestChatUser:
    name: str


@dataclass
class Test_ChatMessage:
    text: str
    user: MyTestChatUser


@pytest.mark.asyncio
async def test_getmsg(test_db):
    # Arrange
    sut = DataBaseInterface(target_channel="test_channel", file_path=test_db)

    test_user = MyTestChatUser("test_user")

    test_message = Test_ChatMessage("!getmsg", test_user)

    # Action
    message_success = await sut.get_message(test_message)

    # Assert
    assert len(message_success) == 0


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

    # Action
    # send a message
    await sut.leave_message(test_msg)
    message_success = await sut.get_message(get_message)

    # Assert
    assert len(message_success) > 0
