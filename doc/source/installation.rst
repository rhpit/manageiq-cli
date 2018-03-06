Installation
============

Install the `virtualenv <https://virtualenv.pypa.io/en/stable/>`_ package
on your system if its not already installed.

.. code-block:: bash
    :linenos:

    $ pip install virtualenv

Create a new Python virtual environment for :program:`ManageIQ client`. This
will eliminate any package version issues between the client and system level
Python packages.

.. code-block:: bash
    :linenos:

    $ virtualenv ~/miq-client && source ~/miq-client/bin/activate

Install the client.

.. code-block:: bash
    :linenos:

    (miq-client) $ pip install git+https://github.com/rhpit/manageiq-cli.git

Please visit the :doc:`quickstart </quickstart>` guide to get started!
