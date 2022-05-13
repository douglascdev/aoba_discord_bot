from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AobaGuild(Base):
    __tablename__ = "guild"
    guild_id = Column(BigInteger, primary_key=True)
    command_prefix = Column(String)
    commands = relationship("AobaCommand", back_populates="guild")
    announcement_channel_id = Column(BigInteger)


class AobaCommand(Base):
    """
    Custom commands added by server admins
    """

    __tablename__ = "command"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String)
    guild_id = Column(BigInteger, ForeignKey("guild.guild_id"))
    guild = relationship("AobaGuild", back_populates="commands")


class AobaUser(Base):
    """
    User data associated with the bot, not a server
    """

    __tablename__ = "aobauser"
    discord_id = Column(BigInteger, primary_key=True, autoincrement=False)
    bank_balance = Column(Integer)
