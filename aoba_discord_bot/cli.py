"""Console script for aoba_discord_bot."""
import logging
import sys

import click

from aoba_discord_bot import AobaDiscordBot


@click.command()
@click.option(
    "--database_url",
    "-db_url",
    default="postgres://postgres:postgres@localhost/aoba",
    envvar="DATABASE_URL",
    help="Database url in the format postgres://user:pass@host/dbname",
)
@click.option("--token", prompt="Token", envvar="TOKEN", help="Discord API token")
@click.option(
    "--osu_client_id", envvar="OSU_CLIENT_ID", help="OAuth client Id for the osu! Cog"
)
@click.option(
    "--osu_client_secret",
    envvar="OSU_CLIENT_SECRET",
    help="OAuth client secret for the osu! Cog",
)
def main(database_url, token, osu_client_id, osu_client_secret):
    """Console script for aoba_discord_bot."""
    logging.basicConfig(level=logging.DEBUG)

    logging.info("Hey this is Aoba, thanks for running me :)")

    api_tokens = {
        "discord": token,
        "osu_client_id": osu_client_id,
        "osu_client_secret": osu_client_secret,
    }

    logging.info("Running discord.py now")

    aoba = AobaDiscordBot(api_tokens, database_url, command_prefix="!")
    aoba.run(token)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
