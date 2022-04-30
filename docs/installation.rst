.. highlight:: shell

============

.. _install:

Installation
============

Add to your server
------------------

Click `here <https://discord.com/api/oauth2/authorize?client_id=525711332591271948&permissions=8&scope=bot>`__ to add our instance of Aoba to your server.


Host instance
-------------

Stable release
~~~~~~~~~~~~~~

To install Aoba Discord Bot, run this command in your terminal:

.. code-block:: console

    $ pip install aoba_discord_bot

This is the preferred method to install Aoba Discord Bot, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process. The installation requires Python 3.6, 3.7, 3.8 or 3.9.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From source
~~~~~~~~~~~


The sources for Aoba Discord Bot can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/douglascdev/aoba_discord_bot

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/douglascdev/aoba_discord_bot/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/douglascdev/aoba_discord_bot
.. _tarball: https://github.com/douglascdev/aoba_discord_bot/tarball/master


Database setup
~~~~~~~~~~~~~~


To self-host the bot you need to make sure you have Postgresql running properly on you computer. Try to use your operating system's default package manager if it has one, or follow the `download <https://www.postgresql.org/download/>`_ page in the official Postgresql website.

After installing and configuring Postgresql, you have to create a database called `aoba`, that is used by the bot. If necessary, check the `official instructions for creating a database <https://www.postgresql.org/docs/current/tutorial-createdb.html>`_.


