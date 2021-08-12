"""Main module."""
import discord
from discord.ext.commands import Bot, Context, check, Command
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import Session

from aoba_discord_bot.cogs.osu import Osu
from aoba_discord_bot.db_models import AobaGuild, AobaCommand
from aoba_discord_bot import aoba_checks


class AobaDiscordBot(Bot):
    async def custom_command(self, ctx: Context):
        try:
            custom_cmd = (
                self.db_session.query(AobaCommand)
                .filter(AobaCommand.name == ctx.command.name)
                .one()
            )
            await ctx.channel.send(custom_cmd.text)
        except (NoResultFound, MultipleResultsFound) as e:
            await ctx.channel.send(
                "Error trying to get command record, check the logs for more information"
            )
            print(e)

    def __init__(self, aoba_params: dict, **options):
        super().__init__(**options)
        self.db_session: Session = aoba_params.get("db_session")
        self.add_cog(
            Osu(
                client_id=aoba_params.get("osu_client_id"),
                client_secret=aoba_params.get("osu_client_secret"),
            )
        )

        @self.command(
            name="guilds", aliases=["servers"], help="List of servers running Aoba"
        )
        @check(aoba_checks.author_is_admin)
        async def get_guilds(ctx):
            guilds_list_str = ", ".join([guild.name for guild in self.guilds])
            await ctx.channel.send(f"**Guilds:**\n > {guilds_list_str}")

        @self.command(help="Set the default command prefix for the current server")
        @check(aoba_checks.author_is_admin)
        async def set_cmd_prefix(ctx: Context, new_prefix: str):
            try:
                guild_db_record = (
                    self.db_session.query(AobaGuild)
                    .filter(AobaGuild.guild_id == ctx.guild.id)
                    .one()
                )
                guild_db_record.command_prefix = new_prefix
                self.db_session.merge(guild_db_record)
                self.db_session.commit()
                await ctx.channel.send(f"Command prefix changed to `{new_prefix}`")
            except (NoResultFound, MultipleResultsFound) as e:
                await ctx.channel.send(
                    "Error trying to get guild id record, check the logs for more information"
                )
                print(e)

        @self.command(
            name="add_cmd",
            help="Adds command in the first argument that displays the text in the second argument",
        )
        @check(aoba_checks.author_is_admin)
        async def new_command(ctx: Context, name: str, text: str):
            try:
                guild_db_record = (
                    self.db_session.query(AobaGuild)
                    .filter(AobaGuild.guild_id == ctx.guild.id)
                    .one()
                )
                new_cmd = AobaCommand(name=name, text=text, guild=guild_db_record)
                self.db_session.merge(new_cmd)
                self.db_session.commit()
                self.add_command(Command(self.custom_command, name=name))
                await ctx.channel.send(f"Command `{name}` was successfully added!")
            except (NoResultFound, MultipleResultsFound) as e:
                await ctx.channel.send(
                    "Error trying to get guild id record, check the logs for more information"
                )
                print(e)

        @self.command(
            name="del_cmd", help="Remove a custom command added with `add_cmd`"
        )
        @check(aoba_checks.author_is_admin)
        async def del_cmd(ctx: Context, name: str):
            try:
                cmd_record = (
                    self.db_session.query(AobaCommand)
                    .filter(AobaCommand.guild_id == ctx.guild.id)
                    .filter(AobaCommand.name == name)
                    .one()
                )
                self.db_session.delete(cmd_record)
                self.db_session.commit()
                self.remove_command(name)
                await ctx.channel.send(f"Command `{name}` was successfully deleted!")
            except (NoResultFound, MultipleResultsFound) as e:
                await ctx.channel.send(
                    "Error trying to get command record, check the logs for more information"
                )
                print(e)

        @self.command(help="Shutdown the bot")
        @check(aoba_checks.author_is_admin)
        async def shutdown(ctx: Context):
            await ctx.channel.send("Shutting down, bye admin!")
            await self.change_presence(status=discord.Status.offline)
            await self.close()

        @self.check
        async def globally_block_dms(ctx: Context):
            return ctx.guild is not None

        @self.event
        async def on_ready():
            async def insert_new_guilds_in_db():
                bot_guild_ids = {guild.id for guild in self.guilds}
                persisted_guild_ids = {
                    guild.guild_id for guild in self.db_session.query(AobaGuild)
                }
                new_guilds = bot_guild_ids.difference(persisted_guild_ids)
                for new_guild_id in new_guilds:
                    new_guild = AobaGuild(guild_id=new_guild_id, command_prefix="!")
                    print(f" - Added database record for guild `{new_guild_id}`")
                    self.db_session.add(new_guild)
                if len(new_guilds) > 0:
                    self.db_session.commit()
                    print(f"{len(new_guilds)} guilds added the bot since the last run")

            async def add_persisted_custom_commands():
                for command in self.db_session.query(AobaCommand):
                    self.add_command(Command(self.custom_command, name=command.name))

            print(f"Logged on as {self.user}")
            await insert_new_guilds_in_db()
            await add_persisted_custom_commands()
            await self.change_presence(
                status=discord.Status.online, activity=discord.Game("in the cloud")
            )
