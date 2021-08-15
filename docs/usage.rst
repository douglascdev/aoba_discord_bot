=====
Usage
=====

Discord Commands
----------------


The bot's commands are separated in groups.

- :ref:`admin-cog`
- :ref:`bot-admin-cog`
- :ref:`osu-cog`
- :ref:`user-cog`

Command-line interface
----------------------

Running an instance requires you to `create a bot account <https://discordpy.readthedocs.io/en/latest/discord.html?highlight=token#creating-a-bot-account>`__ to obtain a token.
After following the :ref:`install`. you'll be able to use the command-line interface:

.. code-block:: console

    $ aoba_discord_bot --help
    Usage: aoba_discord_bot [OPTIONS]

      Console script for aoba_discord_bot.

    Options:
      --db TEXT                 Path for SQLite database file
      --token TEXT              Discord API token
      --osu_client_id TEXT      OAuth client Id for the osu! Cog
      --osu_client_secret TEXT  OAuth client secret for the osu! Cog
      --help                    Show this message and exit.

To run an instance, pass the token as an argument to the command-line interface:

.. code-block:: console

    $ aoba_discord_bot --token <YOUR_TOKEN>

The other arguments are optional.


Modules
-------

To use Aoba Discord Bot in a project::

    import aoba_discord_bot

