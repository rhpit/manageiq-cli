OpenStack
=========

.. important::

    All client examples below are using the default configuration settings.
    You can override this in your environment if you wish.

Create Provider
---------------

This section will guide you through how you can use the client to create a
new OpenStack cloud provider in ManageIQ. It assumes you already know your
OpenStack authentication details.

Below are two ways you can use the client to create a provider.

Command Line
++++++++++++

Command used to create a provider:

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli providers create

You can view the available options by passing the **help** option.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli providers create --help

This command when run will send a request to ManageIQ for a new transaction to
create a new provider. Before running the command, replace the **<value>**
with your OpenStack authentication details.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli providers create \
    --hostname <hostname>
    --port <port>
    --username <username>
    --password <password>

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: Successfully submitted request to create provider: OpenStack.
    INFO: Create provider request ID: <ID>.

Python Code
+++++++++++

This code example will demonstrate how you can use the client in a Python
module to create a new provider. Before running the Python code, replace the
**<value>** with your OpenStack authentication details.

.. code-block:: python
    :linenos:

    from miqcli import Client
    from miqcli.constants import DEFAULT_CONFIG

    client = Client(DEFAULT_CONFIG)
    client.collection = 'providers'

    client.collection.create(
        'OpenStack',
        hostname=<hostname>,
        port=<port>,
        username=<username>,
        password=<password>
    )

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: Successfully submitted request to create provider: OpenStack.
    INFO: Create provider request ID: <ID>.

Delete Provider
---------------

This section will guide you through how you can use the client to delete a
OpenStack cloud provider in ManageIQ.

Below are two ways you can use the client to create a provider.

Command Line
++++++++++++

Command used to delete a provider:

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli providers delete

You can view the available options by passing the **help** option.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli providers delete --help

This command when run will send a request to ManageIQ for a new transaction to
delete the provider.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli providers delete OpenStack

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: Successfully submitted request to delete provider: OpenStack.
    Request ID: <ID>.

Python Code
+++++++++++

This code example will demonstrate how you can use the client in a Python
module to delete a provider.

.. code-block:: python
    :linenos:

    from miqcli import Client
    from miqcli.constants import DEFAULT_CONFIG

    client = Client(DEFAULT_CONFIG)
    client.collection = 'providers'

    client.collection.delete('OpenStack')

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: Successfully submitted request to delete provider: OpenStack.
    Request ID: <ID>.

Create Virtual Machine
----------------------

Delete Virtual Machine
----------------------
