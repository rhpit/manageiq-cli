================
Hacking Guidance
================

This document is intended for anyone who wants to contribute code to the
project.

Fork The Repository
-------------------

Follow the instructions provided by GitHub on `how to fork a repository
<https://help.github.com/articles/fork-a-repo/>`_.

Clone Your Fork
---------------

Once you have forked the main repository. Go ahead and clone your fork to your
local machine:

.. code-block:: bash

    $ git clone git@github.com:username/manageiq-cli.git

Virtual Environment Setup
-------------------------

Now that we have our local copy cloned, lets create a python virtual
environment.

.. code-block:: bash

    $ cd manageiq-cli-clone
    $ virtualenv venv
    $ source venv/bin/activate

Great! The virtual environment is setup. Default it will be created with
Python 2 interpreter. We are compatible with Python 3. You can define the
interpreter that you wish to use when creating your virtual environment.

.. code-block:: bash

    $ virtualenv venv -e /usr/bin/python3.6

Install Development Requirements
--------------------------------

Install the required packages for development. They are defined in
**test-requirements.txt**.

.. code-block:: bash

    (venv) $ pip install -r test-requirements.txt

Install ManageIQ CLI
--------------------

Install the CLI using the editable mode by pip. This will allow any code
changes to be reflected right away. It eliminates the need to keep
reinstalling the package each time a code change is made.

.. code-block:: bash

    (venv) $ pip install -e .

Running Tox
-----------

We use `tox <https://tox.readthedocs.io/en/latest>`_ to run our unit tests.
Tox provides the ability to run unit tests with different python interpreters
in isolated virtual environments. You will need to install tox in your
python virtual environment.

.. code-block:: bash

    (venv) $ pip install tox

Running tox will run all unit tests on the supported python interpreters,
verify pep8 standards are met and build the documentation.

.. code-block:: bash

    (venv) $ tox

You can also run a certain tox environment directly instead of running all
environments.

.. code-block:: bash

    (venv) $ tox -e py27
    (venv) $ tox -e py36
    (venv) $ tox -e pep8
    (venv) $ tox -e docs

General Advise
--------------

* "Simplicity is alway better than functionality." - P. Hintjens
* "Beautiful is better than ugly." - PEP20
* "Always code as if the person who ends up maintaining your code is a violent
  psychopath who knows where you live." -
  http://wiki.c2.com/?CodeForTheMaintainer
