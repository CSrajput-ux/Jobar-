from alembic.config import Config
from alembic.script import ScriptDirectory


def test_migration_chain_has_a_single_head() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    heads = script.get_heads()
    assert heads == ["202610070001"]
