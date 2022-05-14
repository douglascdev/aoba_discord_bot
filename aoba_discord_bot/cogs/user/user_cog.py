import itertools

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context, DefaultHelpCommand

from aoba_discord_bot import AobaDiscordBot
from aoba_discord_bot.formatting import mention_author


class AobaHelp(DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.max_width = 80

    async def add_indented_commands(self, commands, *, heading, max_size=None):
        if not commands:
            return

        self.paginator.add_line(heading)
        max_size = max_size or self.get_max_size(commands)

        get_width = discord.utils._string_width
        for command in commands:
            name = command.name
            width = max_size - (get_width(name) - len(name))
            ctx: Context = self.context
            bot: Bot = ctx.bot
            prefix = await bot.command_prefix(None, ctx.message)
            entry = "{0}{1:<{width}} {2}".format(
                (self.indent - 1) * " " + prefix, name, command.short_doc, width=width
            )
            self.paginator.add_line(self.shorten_text(entry))
        self.paginator.add_line(self.max_width * "_")

    def shorten_text(self, text):
        if len(text) > self.max_width:
            start, rest = text[: self.max_width], text[self.max_width :]
            max_cmd_name_size = self.get_max_size(self.context.bot.commands)
            step = self.max_width - max_cmd_name_size - 3
            split_rest = [rest[i : i + step] for i in range(0, len(rest), step)]

            margin_left = " " * (max_cmd_name_size + 3)
            for i in range(len(split_rest)):
                split_rest[i] = f"{margin_left}{split_rest[i].strip()}"

            split_rest.insert(0, start)

            return "\n".join(split_rest)
        return text

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        if bot.description:
            # <description> portion
            self.paginator.add_line(bot.description, empty=True)

        no_category = "\u200b{0.no_category}:".format(self)

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return cog.qualified_name + ":" if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        max_size = self.get_max_size(filtered)
        to_iterate = itertools.groupby(filtered, key=get_category)

        # Now we can add the commands to the page.
        for category, commands in to_iterate:
            commands = (
                sorted(commands, key=lambda c: c.name)
                if self.sort_commands
                else list(commands)
            )
            await self.add_indented_commands(
                commands, heading=category, max_size=max_size
            )

        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()

    async def send_group_help(self, group):
        self.add_command_formatting(group)

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        await self.add_indented_commands(filtered, heading=self.commands_heading)

        if filtered:
            note = self.get_ending_note()
            if note:
                self.paginator.add_line()
                self.paginator.add_line(note)

        await self.send_pages()

    async def send_cog_help(self, cog):
        if cog.description:
            self.paginator.add_line(cog.description, empty=True)

        filtered = await self.filter_commands(
            cog.get_commands(), sort=self.sort_commands
        )
        await self.add_indented_commands(filtered, heading=self.commands_heading)

        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()


class User(commands.Cog, name="User"):
    def __init__(self, bot: AobaDiscordBot):
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
            escaped_messages.append(
                "".join(f"\\{ch}" if ch in chars_to_escape else ch for ch in message)
            )
        await ctx.send(f"{mention_author(ctx)}:\n{' '.join(escaped_messages)}")


def setup(bot: AobaDiscordBot):
    bot.add_cog(User(bot))
