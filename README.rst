================
Aoba Discord Bot
================
.. raw:: html

    <embed>
        <p align="center">
            <img src="aoba.png" alt="Aoba"/>
        </p>
    </embed>

.. image:: https://img.shields.io/pypi/v/aoba_discord_bot.svg
        :target: https://pypi.python.org/pypi/aoba_discord_bot

.. image:: https://img.shields.io/pypi/pyversions/aoba_discord_bot?color=
        :target: https://pypi.org/project/aoba-discord-bot/

.. image:: https://img.shields.io/travis/douglascdev/aoba_discord_bot.svg
        :target: https://travis-ci.com/douglascdev/aoba_discord_bot

.. image:: https://readthedocs.org/projects/aoba-discord-bot/badge/?version=latest
        :target: https://aoba-discord-bot.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image :: https://github.com/douglascdev/aoba_discord_bot/actions/workflows/codeql-analysis.yml/badge.svg?branch=main
        :target: https://github.com/douglascdev/aoba_discord_bot/actions/workflows/codeql-analysis.yml
        :alt: CodeQL

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

|
.. raw:: html

    <embed>
        <p align="center">
            <img src="aoba.gif" alt="Aoba"/>
        </p>
    </embed>
|


Aoba, the cutest Python Discord bot in all of GitHub! Click `here <https://discord.com/api/oauth2/authorize?client_id=525711332591271948&permissions=8&scope=bot>`__ to add her to your server.

* Free software: MIT license
* Documentation: https://aoba-discord-bot.readthedocs.io.

Please be aware that until version 1.0.0 is released the bot should not be considered stable.
It's still very early in development and could have bugs that would cause problems to your server.


Features
--------

Here's the full list of Discord commands:

.. code-block::

    Admin:
     !ban             Ban a member from this server
     !custom_cmd      Manage custom commands
     !kick            Kick a member from this server
     !prefix          Set the default command prefix
     !purge           Deletes 100 or a specified number of messages from this channel
     !unban           Unban a member from this server

    BotAdmin:
     !announce        (UNTESTED)Make an announcement in every server
     !guilds          List of servers running Aoba
     !shutdown        Shutdown the bot
     !status          Change Aoba's status text

    Osu:
     !beatmaps_backup Generates a backup with download links to your beatmaps by reading an attachment with your osu!.db file
     !score_pp        Performance points obtained by the user in this map

    User:
     !escape_markdown Escapes all Markdown in the message
     !help            Shows this message


    Type !help command for more info on a command.
    You can also type !help category for more info on a category.

Usage
--------
To self host the bot you'll need to:

- Install Python 3.6, 3.7, 3.8 or 3.9
- Get an application token from Discord `here <https://discord.com/developers/applications>`__.
- Install the bot with :code:`pip install aoba_discord_bot`
- Run the bot passing your token: :code:`aoba_discord_bot --token <YOUR_TOKEN>`

The full list of cli commands:

.. code-block::

    aoba_discord_bot --help
    Usage: aoba_discord_bot [OPTIONS]

      Console script for aoba_discord_bot.

    Options:
      --db TEXT                 Path for SQLite database file
      --token TEXT              Discord API token
      --osu_client_id TEXT      OAuth client Id for the osu! Cog
      --osu_client_secret TEXT  OAuth client secret for the osu! Cog
      --help                    Show this message and exit.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
