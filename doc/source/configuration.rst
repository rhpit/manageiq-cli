Configuration
=============

The client requires authentication settings for the ManageIQ server you wish
to establish a connection to. The client provides you with the ability to
define your server configuration settings in multiple ways.

Before we jump into how you can define your configuration settings, lets go
over the settings that you can set.

.. list-table:: Server Settings
    :widths: auto
    :header-rows: 1

    * - Setting
      - Description

    * - url
      - ManageIQ server URL

    * - username
      - ManageIQ username used for authentication

    * - password
      - ManageIQ password used for authentication

    * - token
      - ManageIQ token used for authentication

    * - enable/disable ssl verification
      - Enable/disable SSL verification

.. note::

    The clients `default settings <http://manageiq.org/docs/get-started/
    basic-configuration>`_ are a replica of what ManageIQ sets by default.

Command Line
------------

You can define your server configuration settings each time you run the client.
These can be passed as runtime options.

To view the available options, run the following command:

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli --help | grep -i 'options' -A 12

Below are some examples defining configuration settings by client options:

.. code-block:: bash
    :linenos:

    # configuration by username/password with ssl verification disabled
    (miq-client) $ miqcli --username <username> \
    --password <password> \
    --url <url> \
    --disable-ssl-verify \
    <command> <command-action> <options>

    # configuration by username/password with ssl verification enabled
    (miq-client) $ miqcli --username <username> \
    --password <password> \
    --url <url> \
    --enable-ssl-verify \
    <command> <command-action> <options>

    # configuration by token (token was generated outside scope of the client)
    (miq-client) $ miqcli --token <token> <command> <command-action> <options>

File
----

If you would like to have your configuration settings be persistent, then you
can define these settings within a file. This eliminates the need to define
the settings each time running the client.

The client configuration file needs to be formatted in YAML syntax.

Below are some examples on how you can setup your configuration file:

Username/password auth
~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../example/config/config_userpasswd.yml

Token auth
~~~~~~~~~~

.. literalinclude:: ../../example/config/config_token.yml

The configuration file can be stored in the following directories. The ones
listed below are the order which the file is loaded into memory. If you have
both directories with configuration files, the last one loaded into memory will
be used. If you run into issues with authentication failures, please review
the location of the configuration file.

.. code-block:: bash
    :linenos:

    /etc/miqcli/miqcli.<yml|yaml>
    ./miqcli.<yml|yaml>

Environment Variable
--------------------

You can set an environment variable which has a dictionary value containing
all configuration settings.

Below is an example on how you can set your configuration settings by
environment variables:

.. code-block:: bash
    :linenos:

    (miq-client) $ export MIQ_CFG=\
        "{'url':'<url>', 'username': '<username>', 'password': '<password>',\
        'enable_ssl_verify': False}"

.. attention::

    As you just saw there are multiple ways you can set your own configuration
    settings. Below is the order in which configuration settings will be
    loaded into memory.

    .. code-block:: bash
        :linenos:

        Client default configuration settings
        Client options
        Configuration file /etc/miqcli/miqcli.<yml|yaml>
        Configuration file ./miqcli.<yml|yaml>
        Environment variable

    E.g. If you set settings from the command line options and have settings
    defined in a file. The settings from the command line will be overridden
    by the ones defined in the file.

Validating Configuration Settings
---------------------------------

Once your settings have been created, run the following command against
your ManageIQ server to verify your settings are valid.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli --verbose zones query

If your settings are correct to a remote ManageIQ server, your output should
look like the following (the following has the configuration set in a local
miqcli.yaml file):

.. code-block:: bash
    :linenos:

    WARNING: Config file at /etc/miqcli is undefined.
    WARNING: Config environment variable is undefined.
    INFO: --------------------------------------------------
    INFO:                       Zones                       
    INFO: --------------------------------------------------
    INFO:  * ID: 2018000000000001
    INFO:  * Description: Default Zone
    INFO: --------------------------------------------------

If your settings are incorrect, you will see an error such as:

.. code-block:: bash
    :linenos:

     WARNING: Config file at /etc/miqcli is undefined.
     WARNING: Config environment variable is undefined.
     ERROR: Unsuccessful attempt to authenticate: 401

If you see an error, please update your settings, and try again until
this command succeeds before proceeding.
