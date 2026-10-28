from pathlib import Path
from alembic.config import Config
from alembic.script import ScriptDirectory


def test_migration_chain_has_a_single_head() -> None:
    api_dir = Path(__file__).resolve().parents[1]
    ini_path = api_dir / "alembic.ini"
    config = Config(str(ini_path))
    config.set_main_option("script_location", str(api_dir / "migrations"))
    script = ScriptDirectory.from_config(config)

    heads = script.get_heads()
    assert heads == ["202610260003"]

