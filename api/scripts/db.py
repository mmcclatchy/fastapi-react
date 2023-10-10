import argparse
import os

from alembic import command
from alembic.config import Config


app_root_path = os.getcwd().replace("/scripts", "")
alembic_cfg = Config(f"{app_root_path}/db/alembic.ini")
alembic_cfg.set_main_option("script_location", f"{os.getcwd()}/db/migrations")


def get_script_args():
    parser = argparse.ArgumentParser(description="Alembic upgrade or rebuild")
    subparsers = parser.add_subparsers(dest="command", help="upgrade or rebuild")

    upgrade_parser = subparsers.add_parser("upgrade", help="upgrade alembic revision")
    upgrade_parser.add_argument(
        "--revision", default="head", help="revision hash -- default value: 'head'"
    )

    downgrade_parser = subparsers.add_parser("downgrade", help="downgrade alembic revision")
    downgrade_parser.add_argument(
        "--revision", default="base", help="revision hash -- default value: 'base'"
    )

    subparsers.add_parser(
        "rebuild", help="Tear down and rebuild database in 'dev' environment only"
    )

    revision_parser = subparsers.add_parser("revision", help="create new alembic revision")
    revision_parser.add_argument("revision_message", help="alembic revision description message")

    return parser.parse_args()


def rebuild():
    if os.getenv.get("ENV") == "dev":
        command.downgrade(alembic_cfg, "base")
        command.upgrade(alembic_cfg, "head")
    else:
        raise EnvironmentError("The 'rebuild' command can only be run in the 'dev' environment.")


def main():
    """
    Run Alembic commands to upgrade or rebuild the database.

    This function uses the Alembic library to perform database migrations and revisions.
    It supports the following commands:

    - 'upgrade': Upgrade the database to a specific revision        (Default: latest revision).
    - 'downgrade': Downgrade the database to a specific revision    (Default: base revision).
    - 'rebuild': Tear down and rebuild the database in the 'dev' environment only.
    - 'revision': Create a new Alembic revision with the specified revision message.

    Usage:
        docker-compose [exec | run --rm] api poetry run db upgrade [--revision REVISION_HASH]
        docker-compose [exec | run --rm] api poetry run db downgrade [--revision REVISION_HASH]
        docker-compose [exec | run --rm] api poetry run db rebuild
        docker-compose [exec | run --rm] api poetry run db revision REVISION_MESSAGE
    """

    args = get_script_args()

    match args.command:
        case "upgrade":
            command.upgrade(alembic_cfg, args.revision)

        case "downgrade":
            command.downgrade(alembic_cfg, args.revision)

        case "rebuild":
            rebuild()

        case "revision":
            command.revision(alembic_cfg, args.revision_message, autogenerate=True)

        case _:
            raise ValueError("Invalid command")
