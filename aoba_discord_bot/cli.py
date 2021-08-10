"""Console script for aoba_discord_bot."""
import sys

import click
import discord
from discord.ext.commands import Bot

from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import Session

from aoba_discord_bot import AobaDiscordBot
from aoba_discord_bot.mapped_classes import Base, AobaGuild


@click.command()
@click.option("--db", default="aoba.db", help="Path for SQLite database file")
@click.option("--token", prompt="Token", envvar="TOKEN", help="Discord API token")
def main(db, token):
    """Console script for aoba_discord_bot."""
    bot_invite_url = "https://discord.com/oauth2/authorize?client_id=525711332591271948&permissions=8&scope=bot"
    click.echo("Hey this is Aoba, thanks for running me :)")
    click.echo(f"Please allow me to join your server: {bot_invite_url}")
    click.echo(f"Creating database engine using file ´{db}´")
    engine = create_engine(f"sqlite:///{db}")
    Base.metadata.create_all(engine)

    with Session(engine) as db_session:

        def get_guild_command_prefix(_: Bot, msg: discord.Message):
            try:
                guild = (
                    db_session.query(AobaGuild)
                    .filter(AobaGuild.guild_id == msg.guild.id)
                    .one()
                )
                return guild.command_prefix
            except (NoResultFound, MultipleResultsFound) as e:
                click.echo(f"Error finding guild id. Exception: {e}")
                return None

        aoba = AobaDiscordBot(db_session, command_prefix=get_guild_command_prefix)
        click.echo("Running discord.py now")
        aoba.run(token)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
