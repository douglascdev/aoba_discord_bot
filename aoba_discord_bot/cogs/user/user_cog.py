from discord.ext import commands
from discord.ext.commands import Context, DefaultHelpCommand, Bot

from aoba_discord_bot.formatting import mention_author


class AobaHelp(DefaultHelpCommand):
    pass


class User(commands.Cog, name="User"):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = AobaHelp()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    @commands.command(aliases=["em"], help="Escapes all Markdown in the message")
    async def escape_markdown(self, ctx: Context, *messages: str):
        chars_to_escape = "*", "_", "`", ">"
        escaped_messages = list()
        for message in messages:
            escaped_messages.append("".join(f"\\{ch}" if ch in chars_to_escape else ch for ch in message))
        await ctx.send(f"{mention_author(ctx)}:\n{' '.join(escaped_messages)}")
