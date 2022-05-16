import asyncio
import logging

import discord
from discord import Message, Emoji, Reaction, User
from discord.ext import commands
from discord.ext.commands import Context
from sqlalchemy import select

from aoba_discord_bot import AobaDiscordBot, AobaUser, author_is_admin


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

        if (
            not ctx.author.guild_permissions.administrator
            or not discord_user == ctx.author
        ):
            await ctx.send(
                f"You are not allowed to check {discord_user.display_name}'s balance!"
            )
            return

        async with self.bot.Session() as session:
            query = select(AobaUser).where(AobaUser.discord_id == discord_user.id)
            aoba_user = (await session.execute(query)).scalars().first()

        if aoba_user:
            await ctx.send(
                f"Balance for {discord_user.display_name} is {aoba_user.bank_balance}!"
            )
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
                logging.debug(
                    f"Deposit receiver {receiver.name} not in database, created user {vars(user)}"
                )
            else:
                user.bank_balance = user.bank_balance + value if user else value
                logging.debug(
                    f"Deposit receiver {receiver.name} in database, increased balance by {value}"
                )

            await session.commit()
            await ctx.send(
                f"Deposited {value} for {receiver.display_name}. New balance: {user.bank_balance}"
            )

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
                logging.debug(
                    f"Withdraw receiver {receiver.name} not in database, created user {vars(user)}"
                )
            else:
                user.bank_balance = user.bank_balance - value if user else value
                logging.debug(
                    f"Withdraw receiver {receiver.name} in database, decreased balance by {value}"
                )

            await session.commit()
            await ctx.send(
                f"Withdrew {value} from {receiver.display_name}. New balance: {user.bank_balance}"
            )

    @commands.check(author_is_admin)
    @commands.command(help="Allows an admin to create a bet for users")
    async def bet(
        self,
        ctx: Context,
        name: str,
        comma_separated_options: str,
        timeout_minutes: float = 5.0,
    ) -> object:
        comma_separated_options = list(comma_separated_options.split(","))
        numeric_emojis_unicode = [
            "0️⃣",
            "1️⃣",
            "2️⃣",
            "3⃣",
            "4⃣",
            "5⃣",
            "6⃣",
            "7⃣",
            "8⃣",
            "9⃣",
            "🔟",
        ]

        if timeout_minutes > 60:
            await ctx.send("Can't create a bet with a timeout bigger than 60 minutes!")
            return

        if len(comma_separated_options) < 2:
            await ctx.send("Can't create a bet with a single option!")
            return

        if len(comma_separated_options) > len(numeric_emojis_unicode):
            await ctx.send(
                f"The maximum number of options is {len(numeric_emojis_unicode)}!"
            )
            return

        new_line_char = "\n"
        formatted_options = new_line_char.join(
            [
                f" - {option}: {emoji}"
                for option, emoji in zip(
                    comma_separated_options, numeric_emojis_unicode
                )
            ]
        )
        message: Message = await ctx.send(
            f"Bet created: {name}.\nOptions: {new_line_char}{formatted_options}"
        )

        for r, _ in zip(numeric_emojis_unicode, comma_separated_options):
            await message.add_reaction(r)

        result_msg = await ctx.send(
            f"React to this message with the winner reaction within {int(timeout_minutes)}m to close the bet, or with 0 to cancel it."
        )

        valid_emojis = [
            e for e in numeric_emojis_unicode[: len(comma_separated_options)]
        ]

        author = ctx.message.author

        def check(reaction: Reaction, user: User):
            return (
                user == author
                and reaction.message == result_msg
                and str(reaction.emoji) in valid_emojis
            )

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=timeout_minutes * 60, check=check
            )

            if str(reaction.emoji) == "0️⃣":
                await ctx.send(f"Bet '{name}' was cancelled.")
                return

            winners, losers = [], []

            await ctx.send(f"Bet '{name}' finished, distributing rewards...")
            message = await ctx.fetch_message(message.id)

            for r in message.reactions:
                if str(r.emoji) == reaction.emoji:
                    async for user in r.users():
                        if not user.bot:
                            winners.append(user)
                else:
                    async for user in r.users():
                        if not user.bot:
                            losers.append(user)

            points_per_bet = 100
            total_lost = points_per_bet * len(losers)
            reward_per_winner = total_lost // len(winners)

            for winner in winners:
                await ctx.invoke(self.deposit, value=reward_per_winner, receiver=winner)

            for loser in losers:
                await ctx.invoke(self.withdraw, value=points_per_bet, receiver=loser)

        except asyncio.TimeoutError:
            await ctx.send("Bet timed out!")


def setup(bot: AobaDiscordBot):
    bot.add_cog(Economy(bot))
