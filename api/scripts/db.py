import argparse
import os

from alembic import command
from alembic.config import Config


app_root_path = os.getcwd().replace("/scripts", "")
alembic_cfg = Config(f"{app_root_path}/db/alembic.ini")
alembic_cfg.set_main_option("script_location", f"{os.getcwd()}/db/migrations")


def upgrade(revision="head"):
    command.upgrade(alembic_cfg, revision)


def rebuild():
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")


def main():
    parser = argparse.ArgumentParser(description="Alembic upgrade or rebuild")
    subparsers = parser.add_subparsers(dest="command", help="upgrade or rebuild")
    upgrade_parser = subparsers.add_parser("upgrade")
    upgrade_parser.add_argument(
        "--revision", default="head", help="default value: 'head'"
    )
    subparsers.add_parser("rebuild")
    args = parser.parse_args()

    if args.command == "upgrade":
        upgrade(args.revision)
    elif args.command == "rebuild":
        if os.getenv.get("ENV") == "dev":
            rebuild()
    else:
        raise ValueError("Invalid command")
