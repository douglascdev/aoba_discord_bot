import discord
from discord import User
from discord.ext import commands
from discord.ext.commands import Context
from sqlalchemy.future import select

from aoba_discord_bot import AobaDiscordBot
from aoba_discord_bot.aoba_checks import author_is_admin
from aoba_discord_bot.db_models import AobaCommand, AobaGuild


class Admin(commands.Cog, name="Admin"):
    """
    Category of commands for administrative tasks like managing commands and banning users.
    """

    def __init__(self, bot: AobaDiscordBot):
        self.bot = bot

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
        """
        Creates a new command that displays text.
        :param ctx: command context
        :param name: name used to invoke the new command
        :param text: text that will be displayed
        """
        async with self.bot.Session() as session:
            q = select(AobaGuild)
            result = await session.execute(q)
            guild_db_record = next(
                iter(
                    filter(lambda g: g.guild_id == ctx.guild.id, result.scalars().all())
                ),
                None,
            )
            if not guild_db_record:
                await ctx.channel.send(
                    "Error trying to get guild id record, check the logs for more information"
                )
                return
            new_cmd = AobaCommand(name=name, text=text, guild=guild_db_record)
            await session.merge(new_cmd)
            await session.commit()

            self.bot.add_command(commands.Command(ctx.bot.custom_command, name=name))
            await ctx.channel.send(f"Command `{name}` was successfully added!")

    @commands.check(author_is_admin)
    @custom_cmd.command(name="del", help="Delete a custom command")
    async def del_command(self, ctx: Context, name: str):
        async with self.bot.Session() as session:
            cmd_records = (await session.execute(select(AobaCommand))).scalars().all()
            cmd_record = next(
                iter(
                    filter(
                        lambda cmd: cmd.guild_id == ctx.guild.id and cmd.name == name,
                        cmd_records,
                    )
                ),
                None,
            )
            if not cmd_record:
                await ctx.channel.send("Command not found!")
                return
            await session.delete(cmd_record)
            await session.commit()
            self.bot.remove_command(name)
            await ctx.channel.send(f"Command `{name}` was successfully deleted!")

    @commands.check(author_is_admin)
    @commands.command(help="Set the default command prefix")
    async def prefix(self, ctx: Context, new_prefix: str):
        async with self.bot.Session() as session:
            q = select(AobaGuild)
            result = await session.execute(q)
            guild_db_record = next(
                iter(
                    filter(lambda g: g.guild_id == ctx.guild.id, result.scalars().all())
                ),
                None,
            )
            if not guild_db_record:
                await ctx.channel.send(
                    "Error trying to get guild id record, check the logs for more information"
                )
                return

            guild_db_record.command_prefix = new_prefix
            await session.merge(guild_db_record)
            await session.commit()
            await ctx.channel.send(f"Command prefix changed to `{new_prefix}`")

    @commands.check(author_is_admin)
    @commands.command(help="Kick a member from this server")
    async def kick(self, ctx: Context, user: User):
        await ctx.guild.kick(user)

    @commands.check(author_is_admin)
    @commands.command(help="Ban a member from this server")
    async def ban(self, ctx: Context, user: User):
        await ctx.guild.ban(user)

    @commands.check(author_is_admin)
    @commands.command(help="Unban a member from this server")
    async def unban(self, ctx: Context, user: User):
        await ctx.guild.unban(user)

    @commands.check(author_is_admin)
    @commands.command(
        help="Deletes 100 or a specified number of messages from this channel"
    )
    async def purge(self, ctx: Context, limit: int = 100):
        await ctx.channel.purge(limit=limit)

    @commands.check(author_is_admin)
    @commands.group(help="Announcement commands", pass_context=True)
    async def announcement(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid announcement command passed.")

    @commands.check(author_is_admin)
    @announcement.command(
        help="Set the default announcement channel for the server"
    )
    async def set_channel(self, ctx: Context, channel: discord.TextChannel):
        async with self.bot.Session() as session:
            query = select(AobaGuild).where(AobaGuild.guild_id == ctx.guild.id)
            guild = (await session.execute(query)).scalars().first()
            guild.announcement_channel_id = channel.id
            await session.merge(guild)
            await session.commit()
            await ctx.send(f"Announcement channel set to {channel.name}!")

    @commands.check(author_is_admin)
    @announcement.command(
        help="Get the default announcement channel for the server"
    )
    async def get_channel(self, ctx: Context):
        async with self.bot.Session() as session:
            query = select(AobaGuild).where(AobaGuild.guild_id == ctx.guild.id)
            guild = (await session.execute(query)).scalars().first()
            channel_name = ctx.guild.get_channel(guild.announcement_channel_id).name
            await ctx.send(f"The announcement channel is {channel_name}!")

    @commands.check(author_is_admin)
    @announcement.command(
        help="Make an announcement using the default announcement channel"
    )
    async def announce(self, ctx: Context, *messages: str):
        async with self.bot.Session() as session:
            query = select(AobaGuild).where(AobaGuild.guild_id == ctx.guild.id)
            guild = (await session.execute(query)).scalars().first()

            if not guild.announcement_channel_id:
                await ctx.send("No announcement channel set!")
                return

            channel = ctx.guild.get_channel(guild.announcement_channel_id)
            await channel.send(" ".join(messages))


def setup(bot: AobaDiscordBot):
    bot.add_cog(Admin(bot))
