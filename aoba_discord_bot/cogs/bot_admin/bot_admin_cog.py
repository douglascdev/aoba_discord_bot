import discord
from discord import Member
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
    async def get_guilds(self, ctx: Context):
        guilds_list_str = ", ".join([guild.name for guild in self.bot.guilds])
        await ctx.channel.send(f"**Guilds:**\n > {guilds_list_str}")

    @commands.is_owner()
    @commands.command(help="Change Aoba's status text")
    async def status(self, ctx: Context, text: str = None):
        if text:
            await self.bot.change_presence(activity=discord.Game(text))
            await ctx.send(f"My status was changed to `{text}`!")
        else:
            member: Member = None
            for guild in self.bot.guilds:
                member = guild.get_member(self.bot.user.id)
                if member:
                    break
            if member:
                await ctx.send(member.activity)
