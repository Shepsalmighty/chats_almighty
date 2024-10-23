from twitch_bot.model.sqlite_db import DBMigration
import pytest


# INFO because pytest looks for conftest.py we can implement a temporary DB using tmpdir which only exists during tests

# @pytest.fixture built in part of pytest
@pytest.fixture
def test_db(tmpdir):
    result = tmpdir / "test.db"

    DBMigration(result).create_tables()
    return result
