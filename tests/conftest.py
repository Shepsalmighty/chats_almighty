from twitch_bot.model.sqlite_db import DBMigration
import pytest


@pytest.fixture
def test_db(tmpdir):
    result = tmpdir / "test.db"

    DBMigration(result).create_tables()
    return result
