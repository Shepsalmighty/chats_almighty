from argparse import Action

import pytest
import twitch_bot.model.database_interface
from model.database_interface import DataBaseInterface


# INFO https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/

def test_get_msg_returns_a_message():
    # Arrange
    sut = DataBaseInterface(target_channel="test_channel")

    # Action

    # Assert
    pass
