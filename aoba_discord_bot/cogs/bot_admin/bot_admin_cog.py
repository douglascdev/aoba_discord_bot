from typing import List

import discord
from discord import Guild, Member, TextChannel
from discord.ext import commands
from discord.ext.commands import Context
from sqlalchemy import select

from aoba_discord_bot import AobaDiscordBot, AobaGuild


class BotAdmin(
    commands.Cog,
    name="BotAdmin",
):
    def __init__(self, bot: AobaDiscordBot):
        self.bot = bot

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
    async def status(self, ctx: Context, *texts: str):
        if not texts:
            msg = "Status is empty" if not self.bot.activity else self.bot.activity
            await ctx.send(msg)
            return

        status = " ".join(texts)
        self.bot.activity = discord.Game(status)
        await self.bot.change_presence(activity=self.bot.activity)
        await ctx.send(f"My status was changed to `{status}`!")

    @commands.is_owner()
    @commands.command(
        help="Make an announcement in every server with an announcement server set"
    )
    async def aoba_announce(self, ctx: Context, *texts: str):
        text = " ".join(texts)

        async with self.bot.Session() as session:
            query = select(AobaGuild).where(AobaGuild.announcement_channel_id != None)
            aoba_guilds = (await session.execute(query)).scalars().all()
            channels: List[TextChannel] = [
                ctx.guild.get_channel(guild.announcement_channel_id)
                for guild in aoba_guilds
            ]

            await ctx.send(f"Announcing `{text}` in {len(channels)} servers.")

            for channel in channels:
                await channel.send(text)


def setup(bot: AobaDiscordBot):
    bot.add_cog(BotAdmin(bot))
