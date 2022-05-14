"""Main module."""
import logging
import pathlib
import re

import discord
from discord.ext.commands import Bot, Command, Context
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import scoped_session, sessionmaker

from aoba_discord_bot.db_models import AobaCommand, AobaGuild, Base


class AobaDiscordBot(Bot):
    def __init__(self, api_keys: dict, db_url: str, **options):
        super().__init__(**options)
        self.Session: scoped_session = None
        self.db_url = db_url
        self.api_keys = api_keys
        self.command_prefix = self.get_guild_command_prefix

        self._load_cogs()

        @self.check
        async def globally_block_dms(ctx: Context):
            return ctx.guild is not None

        @self.event
        async def on_ready():
            bot_invite_url = f"https://discord.com/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot"
            logging.info(f"Please allow me to join your server: {bot_invite_url}")

            # Since Heroku's environment variable DATABASE_URL is set in the format postgres:// instead of
            # postgresql+asyncpg:// this replaces Heroku's URL to contain the dialect. For this reason, the
            # format postgres:// is always replaced to postgresql+asyncpg:// even when running locally
            self.db_url = re.sub(r"\w+:", "postgresql+asyncpg:", db_url, count=1)

            db_engine = create_async_engine(self.db_url)

            async with db_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            self.Session = scoped_session(
                sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
            )

            async def insert_new_guilds_in_db():
                async with self.Session() as session:
                    bot_guild_ids = {guild.id for guild in self.guilds}
                    persisted_guilds = (
                        (await session.execute(select(AobaGuild))).scalars().all()
                    )
                    persisted_guild_ids = {guild.guild_id for guild in persisted_guilds}
                    new_guilds = bot_guild_ids.difference(persisted_guild_ids)
                    for new_guild_id in new_guilds:
                        new_guild = AobaGuild(guild_id=new_guild_id, command_prefix="!")
                        logging.info(f" - Added database record for guild `{new_guild_id}`")
                        session.add(new_guild)
                    if len(new_guilds) > 0:
                        await session.commit()
                        logging.info(
                            f"{len(new_guilds)} guilds added the bot since the last run"
                        )

            async def add_persisted_custom_commands():
                async with self.Session() as session:
                    custom_cmds = (
                        (await session.execute(select(AobaCommand))).scalars().all()
                    )

                    for command in custom_cmds:
                        self.add_command(
                            Command(self.custom_command, name=command.name)
                        )

            logging.info(f"Logged on as {self.user}")
            await insert_new_guilds_in_db()
            await add_persisted_custom_commands()
            await self.change_presence(
                status=discord.Status.online, activity=discord.Game("on the cloud")
            )

    async def _load_cogs(self) -> None:
        for cog_folder in (pathlib.Path(__file__).parent / "cogs").iterdir():
            # Exclude __pychache__ and __init__
            if "__" in str(cog_folder):
                continue

            cog_name = cog_folder.stem
            self.load_extension(f"aoba_discord_bot.cogs.{cog_name}.{cog_name + '_cog'}")

    async def custom_command(self, ctx: Context):
        custom_cmds = (
            (await self.Session().execute(select(AobaCommand))).scalars().all()
        )
        called_command: AobaCommand = next(
            iter(filter(lambda cmd: cmd.name == ctx.command.name, custom_cmds)), None
        )
        if not called_command:
            await ctx.channel.send("Custom command not found!")
            return

        await ctx.channel.send(called_command.text)

    async def get_guild_command_prefix(self, _: Bot, msg: discord.Message):
        async with self.Session() as session:
            q = select(AobaGuild)
            result = await session.execute(q)
            guild = next(
                iter(
                    filter(lambda g: g.guild_id == msg.guild.id, result.scalars().all())
                ),
                None,
            )
            return guild.command_prefix if guild else "!"
