from discord.ext import commands
from discord.ext.commands import Context, Bot
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import Session

from aoba_discord_bot.aoba_checks import author_is_admin
from aoba_discord_bot.db_models import AobaGuild, AobaCommand


class Admin(commands.Cog, name="Admin"):
    def __init__(self, bot: Bot, db_session: Session):
        self.bot = bot
        self.db_session = db_session
        self.bot_check(author_is_admin)

    @commands.check(author_is_admin)
    @commands.group(help="Manage custom commands", pass_context=True)
    async def custom_cmd(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid custom command passed.")

    @commands.check(author_is_admin)
    @custom_cmd.command(
        name="add",
        help="Add a custom command",
    )
    async def new_command(self, ctx: Context, name: str, text: str):
        try:
            guild_db_record = (
                self.db_session.query(AobaGuild)
                .filter(AobaGuild.guild_id == ctx.guild.id)
                .one()
            )
            new_cmd = AobaCommand(name=name, text=text, guild=guild_db_record)
            self.db_session.merge(new_cmd)
            self.db_session.commit()

            async def custom_command(ctx: Context):
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

            self.bot.add_command(commands.Command(custom_command, name=name))
            await ctx.channel.send(f"Command `{name}` was successfully added!")
        except (NoResultFound, MultipleResultsFound) as e:
            await ctx.channel.send(
                "Error trying to get guild id record, check the logs for more information"
            )
            print(e)

    @commands.check(author_is_admin)
    @custom_cmd.command(name="del", help="Delete a custom command")
    async def del_command(self, ctx: Context, name: str):
        try:
            cmd_record = (
                self.db_session.query(AobaCommand)
                .filter(AobaCommand.guild_id == ctx.guild.id)
                .filter(AobaCommand.name == name)
                .one()
            )
            self.db_session.delete(cmd_record)
            self.db_session.commit()
            self.bot.remove_command(name)
            await ctx.channel.send(f"Command `{name}` was successfully deleted!")
        except (NoResultFound, MultipleResultsFound) as e:
            await ctx.channel.send(
                "Error trying to get command record, check the logs for more information"
            )
            print(e)

    @commands.check(author_is_admin)
    @commands.command(help="Set the default command prefix")
    async def prefix(self, ctx: Context, new_prefix: str):
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

    @commands.check(author_is_admin)
    @commands.command(
        help="Deletes 100 or a specified number of messages from this channel"
    )
    async def purge(self, ctx: Context, limit: int = 100):
        await ctx.channel.purge(limit=limit)
