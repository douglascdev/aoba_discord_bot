import logging

import discord
from discord.ext import commands
from discord.ext.commands import Context
from sqlalchemy import select

from aoba_discord_bot import AobaDiscordBot, AobaUser


class Economy(commands.Cog, name="Economy"):
    """
    Category of commands that manage the server economy
    """

    def __init__(self, bot: AobaDiscordBot):
        self.bot = bot

    @commands.command(help="Get the bank balance of an user", pass_context=True)
    async def balance(self, ctx: Context, discord_user: discord.User = None):
        if not discord_user:
            discord_user = ctx.author

        if not ctx.author.guild_permissions.administrator or not discord_user == ctx.author:
            await ctx.send(f"You are not allowed to check {discord_user.display_name}'s balance!")
            return

        async with self.bot.Session() as session:
            query = select(AobaUser).where(AobaUser.discord_id == discord_user.id)
            aoba_user = (await session.execute(query)).scalars().first()

        if aoba_user:
            await ctx.send(f"Balance for {discord_user.display_name} is {aoba_user.bank_balance}!")
        else:
            await ctx.send(f"No balance found for {discord_user.display_name}!")

    @commands.is_owner()
    @commands.command(help="Deposit value to an user's balance", pass_context=True)
    async def deposit(self, ctx: Context, value: int, receiver: discord.User = None):
        if not receiver:
            receiver = ctx.author

        logging.info(f"Depositing {value} to {receiver.name}'s bank balance")

        async with self.bot.Session() as session:
            query = select(AobaUser).where(AobaUser.discord_id == receiver.id)
            user = (await session.execute(query)).scalars().first()

            if not user:
                user = AobaUser(discord_id=receiver.id, bank_balance=value)
                session.add(user)
                logging.debug(f"Deposit receiver {receiver.name} not in database, created user {vars(user)}")
            else:
                user.bank_balance = user.bank_balance + value if user else value
                logging.debug(f"Deposit receiver {receiver.name} in database, increased balance by {value}")

            await session.commit()
            await ctx.send(f"Deposited {value} for {receiver.display_name}. New balance: {user.bank_balance}")

    @commands.is_owner()
    @commands.command(help="Withdraw a value from an user's account", pass_context=True)
    async def withdraw(self, ctx: Context, value: int, receiver: discord.User = None):
        if not receiver:
            receiver = ctx.author

        logging.info(f"Withdrawing {value} from {receiver.name}'s bank balance")

        async with self.bot.Session() as session:
            query = select(AobaUser).where(AobaUser.discord_id == receiver.id)
            user = (await session.execute(query)).scalars().first()

            if not user:
                user = AobaUser(discord_id=receiver.id, bank_balance=value)
                session.add(user)
                logging.debug(f"Withdraw receiver {receiver.name} not in database, created user {vars(user)}")
            else:
                user.bank_balance = user.bank_balance - value if user else value
                logging.debug(f"Withdraw receiver {receiver.name} in database, decreased balance by {value}")

            await session.commit()
            await ctx.send(f"Withdrew {value} from {receiver.display_name}. New balance: {user.bank_balance}")


def setup(bot: AobaDiscordBot):
    bot.add_cog(Economy(bot))
