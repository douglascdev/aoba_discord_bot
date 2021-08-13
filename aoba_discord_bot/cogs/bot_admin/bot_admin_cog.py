import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot
from sqlalchemy.orm import Session


class BotAdmin(
    commands.Cog,
    name="BotAdmin",
):
    def __init__(self, bot: Bot, db_session: Session):
        self.bot = bot
        self.db_session = db_session

    @commands.is_owner()
    @commands.command(help="Shutdown the bot")
    async def shutdown(self, ctx: Context):
        await ctx.channel.send("Shutting down, bye admin!")
        await self.bot.change_presence(status=discord.Status.offline)
        await self.bot.close()

    @commands.is_owner()
    @commands.command(
        name="guilds", aliases=["servers"], help="List of servers running Aoba"
    )
    async def get_guilds(self, ctx):
        guilds_list_str = ", ".join([guild.name for guild in self.bot.guilds])
        await ctx.channel.send(f"**Guilds:**\n > {guilds_list_str}")
