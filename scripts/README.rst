Test Environment Scripts
========================

These scripts prepare the test environment.

Requirements
------------

Prior to run these scripts, you must have:

* docker
* python docker library
* phantomjs, set in your PATH
* internet access because the datastore will be installed from the project's github repository.

Scripts
-------

* testinstance - start/stop a ManageIQ container
* change_configuration.js - configure the local ManageIQ instance
* install_datastore.js - install the datastore from the manageiq-cli project


How to execute
--------------

.. code-block:: bash

    $ ./testinstance -c start
    $ phantomjs --config phantomjs-config.json change_configuration.js
    $ phantomjs --config phantomjs-config.json install_datastore.js


How to stop
-----------

.. code-block:: bash

    $ ./testinstance -c stop

You could have given another name for the docker container. If that is what you've done, then you
have to give the container name when calling stop otherwise it will try to delete a container named
'miqcli_test'.
