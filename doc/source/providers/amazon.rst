Amazon
======

.. important::

    All client examples below are using the default configuration settings.
    You can override this in your environment if you wish.

Create Provider
---------------

This section will guide you through how you can use the client to create a
new Amazon cloud provider in ManageIQ. It assumes you already know your
Amazon authentication details.

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
create a new provider. Before running the command, replace the **<<value>>**
with your Amazon authentication details.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli providers create \
    --region <region>
    --username <username>
    --password <password>

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: Successfully submitted request to create provider: Amazon.
    INFO: Create provider request ID: <ID>.

Python Code
+++++++++++

This code example will demonstrate how you can use the client in a Python
module to create a new provider. Before running the Python code, replace the
**<value>** with your Amazon authentication details.

.. code-block:: python
    :linenos:

    from miqcli import Client
    from miqcli.constants import DEFAULT_CONFIG

    client = Client(DEFAULT_CONFIG)
    client.collection = 'providers'

    client.collection.create(
        'Amazon',
        region=<region>,
        username=<username>,
        password=<password>
    )

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: Successfully submitted request to create provider: Amazon.
    INFO: Create provider request ID: <ID>.


Delete Provider
---------------

This section will guide you through how you can use the client to delete a
Amazon cloud provider in ManageIQ.

Below are two ways you can use the client to delete a provider.

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

    (miq-client) $ miqcli providers delete Amazon

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: Successfully submitted request to delete provider: Amazon.
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

    client.collection.delete('Amazon')

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: Successfully submitted request to delete provider: Amazon.
    Request ID: <ID>.

Create Virtual Machine
----------------------

This section will guide you through the use of the client to create a
new Amazon cloud virtual machine in ManageIQ. It assumes you already
know your Amazon details.

Below are two ways you can use the client to create a virtual machine.

Command Line
++++++++++++

Command used to create a virtual machine:

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli provision_requests create

You can view the available options by passing the **help** option.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli provision_requests create --help

This command when run will send a request to ManageIQ for a new transaction to
create a new virtual machine. Before running the command, replace the **<<value>>**
with your Amazon Instance details in the json payload file or payload string.

Example Payloads:

JSON Payload file Auto-placement::

    {
      "email": "<email_address>",
      "image": "<image_name>",
      "flavor": "<instance_type>",
      "key_pair": "<key_pair>",
      "vm_name": "<instance_name>",
      "provider": "<provider_name>",
      "auto_placement": "true"
    }

JSON Payload file specifying placement::

    {
      "email": "<email_address>",
      "image": "<image_name>",
      "flavor": "<instance_type>",
      "key_pair": "<key_pair>",
      "vm_name": "<instance_name>",
      "security_group": "<security_group>",
      "network": "<virtual_private_cloud>",
      "subnet": "<cloud_subnet>"
    }

Command with payload given as file

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli provision_requests create \
    --provider Amazon
    --payload_file <json-payload-file>

Command with payload given as string

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli provision_requests create \
    --provider Amazon
    --payload "{'email':'<email_address>','image':'<image_name>',
    'flavor':'<instance_type>','key_pair':'<key_pair>',
    'vm_name':'<instance_name>','security_group':'<security_group>',
    'network':'<virtual_private_cloud>','subnet':'<cloud_subnet>'}"

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: Attempt to create a provision request
    INFO: Provisioning request created: 566

Use 'miqcli request_tasks status <ID>' to check status of transaction completion.
Once complete you can use "instances query" to obtain information about the
instance created.

Python Code
+++++++++++

This code example will demonstrate how you can use the client in a Python
module to create a virtual machine. Before running the Python code, replace the
**<value>** with your Amazon Instance details in a json payload file. See
command line section above for payload file content examples.

.. code-block:: python
    :linenos:

    import json
    from miqcli import Client
    from miqcli.constants import DEFAULT_CONFIG
    from time import sleep

    # create a client object
    # use the default credentials
    client = Client(DEFAULT_CONFIG)

    # 1. Gather the input payload data
    # Uncomment desired example
    # Auto Placement or Specifying Placement (Network and Subnet)

    # Auto Placement Example Payload File
    # payload_file = "aws_provision_ex_auto_placement.json"

    # Not Auto Placement - Specify Placement and cloud_subnet
    payload_file = "aws_provision_ex_cloud_subnet.json"

    with open(payload_file) as f:
        try:
            payload_data = json.load(f)
        except ValueError as e:
            print("Error loading json data: {0}".format(e))
            raise SystemExit(1)

    # 2. call the provision request to create this vm (cli call to
    #  provision_request create --provider Amazon this will return an id
    client.collection = "provision_requests"
    req_id = client.collection.create('Amazon', str(payload_data), "")
    print("ID of the request: {0}".format(req_id))

    # Query the provision request until it is active, then query
    # the spawned request task
    done = False
    while not done:
        result = client.collection.status(req_id)
        if result.request_state == 'active' or result.request_state == 'finished':
            done = True
        sleep(5)

    # 3. the script will query the request task until the state is finished
    #  once finished, it will return information about the provisioned machine
    #  or display the error message
    client.collection = "request_tasks"
    done = False
    while not done:
        result = client.collection.status(req_id)
        if result.state == "finished":
            done = True
        sleep(5)

    # 4. Report the floating ip address back to the user if there are no errors
    if result.status == "Error":
        req_state = result.state
        req_status = result.status
        print("State: {0} and Status: {1}".format(req_state, req_status))
        print("Message: {0}".format(result.message))
    else:
        # Get the data back from the provision_request
        client.collection = "provision_requests"
        result = client.collection.status(req_id)
        vm_name = payload_data["vm_name"]

        # Set key attributes if provided
        vm_provider = None
        vm_network = None
        vm_tenant = None
        vm_subnet = None
        if "provider" in payload_data and payload_data["provider"]:
            vm_provider = payload_data["provider"]
        if "network" in payload_data and payload_data["network"]:
            vm_network = payload_data["network"]
        if "subnet" in payload_data and payload_data["subnet"]:
            vm_subnet = payload_data["subnet"]
        if "tenant" in payload_data and payload_data["tenant"]:
            vm_tenant = payload_data["tenant"]

        try:
            client.collection = "instances"
            instances = client.collection.query(inst_name=vm_name,
                                                provider=vm_provider,
                                                network=vm_network,
                                                tenant=vm_tenant,
                                                subnet=vm_subnet,
                                                attr=("floating_ip",))
            if instances and type(instances) is list:
                print("Multiple instances found.")
                print("Unable to specify specific floating ip for created vm")
                raise SystemExit(1)
            elif not instances:
                print("Issues creating vm. No vm found to obtain floating ip")
                raise SystemExit(1)
            else:
                try:
                    fip_id = instances["floating_ip"]["address"]
                    print("Floating ip for {0}: {1}".format(vm_name, fip_id))
                except AttributeError as e:
                    print('No associated floating ips for vm: {0}'.format(
                        instances["name"]))
        except SystemExit as e:
            print(e.message)
            raise SystemExit(1)

On completion, you should receive Success with instance information or
an Error message.

Ending output of a successful run.

.. code-block:: bash

   INFO: --------------------------------------------------
   INFO:                 Provision request
   INFO: --------------------------------------------------
   INFO:  * ID: 568
   INFO:  * VM: aws_miq_test_machine_2
   INFO:  * STATE: finished
   INFO:  * STATUS: Ok
   INFO:  * MESSAGE: [EVM] VM [aws_miq_test_machine_2] IP [172.31.10.243] Provisioned Successfully
   INFO: --------------------------------------------------
   INFO: --------------------------------------------------
   INFO:                   Instance Info
   INFO: --------------------------------------------------
   INFO:  * ID: 2250
   INFO:  * NAME: aws_miq_test_machine_2
   INFO:  * FLOATING_IP: {u'network_port_id': 1288, u'type': u'ManageIQ::Providers::Amazon::NetworkManager::FloatingIp', u'fixed_ip_address': u'172.31.10.243', u'address': u'18.221.148.25', u'ems_ref': u'18.221.148.25', u'ems_id': 6, u'vm_id': 2250, u'id': 1185, u'cloud_network_only': True}
   INFO: --------------------------------------------------
   Floating ip for aws_miq_test_machine_2: 18.221.148.25

Delete Virtual Machine
----------------------

This section will guide you through the use of the client to delete an
Amazon cloud virtual machine in ManageIQ. It assumes you already
know the Name of the instance to delete, the Amazon provider name and
the Amazon details of Network and Subnet if needed.

Below are two ways you can use the client to delete a virtual machine.

Command Line
++++++++++++

Three commands will be needed to delete a virtual machine:

1. Query Instances for Instance ID.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli instances query

You can view the available options by passing the **help** option.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli instances query --help

This command when run will query ManageIQ for Instance information for the
instance name and provider given. Before running the command, replace the **<<value>>**
with your Amazon virtual machine details.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli instances query \
    <instance_name>
    --provider <provider>

On completion, you should receive Instance information containing ID and Name
for your Instance. If multiples are returned, use the **network** and **subnet**
options of the command to narrow the selection.

.. code-block:: bash

    INFO: --------------------------------------------------
    INFO:                   Instance Info
    INFO: --------------------------------------------------
    INFO:  * ID: 2189
    INFO:  * NAME: aws_vm_1
    INFO: --------------------------------------------------

2. Delete/Terminate the Instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli instances terminate

You can view the available options by passing the **help** option.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli instances terminate --help

This command when run will send a request to ManageIQ for a new transaction to
delete the instance. Before running the command, replace the **<<value>>**
with your Amazon virtual machine details. For <instance_name> provide the ID returned
by the query command above and set the option **by_id** to True.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli instances terminate \
    <instance_name>
    --by_id True

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: --------------------------------------------------
    INFO:                   Instance Info
    INFO: --------------------------------------------------
    INFO:  * ID: 2189
    INFO:  * NAME: aws_vm_1
    INFO: --------------------------------------------------
    INFO: Task to terminate 2189 created: 1324

Use 'miqcli tasks status <ID>' to check status of transaction completion.

3. Remove the VM reference in Cloudforms/MIQ
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli vms delete

You can view the available options by passing the **help** option.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli vms delete --help

This command when run will send a request to ManageIQ for a new transaction to
delete the vms reference. Before running the command, replace the **<<value>>**
with your Amazon virtual machine details. For <instance_name> provide the ID returned
by the query command above and set the option **by_id** to True.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli vms delete \
    <instance_name>
    --by_id True

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: --------------------------------------------------
    INFO:                   Vm Info
    INFO: --------------------------------------------------
    INFO:  * ID: 2189
    INFO:  * NAME: aws_vm_1
    INFO: --------------------------------------------------
    INFO: Task to delete 2189 created: 1324

Use 'miqcli tasks status <ID>' to check status of transaction completion.

Python Code
+++++++++++

This code example will demonstrate how you can use the client in a Python
module to delete a virtual machine. Before running the Python code, replace the
**<value>** with your Amazon virtual machine details.

.. code-block:: python
    :linenos:

    import ast
    from miqcli import Client
    from miqcli.constants import DEFAULT_CONFIG
    from time import sleep

    # Required Input Parameters
    INPUT_VM_NAME = <instance_name>
    INPUT_PROVIDER_NAME = <provider_name>

    # Optional Input Parameter
    INPUT_NETWORK = <network>
    INPUT_SUBNET = <subnet>

    client = Client(DEFAULT_CONFIG)

    # 1. Query the instance to obtain ID
    client.collection = "instances"

    try:
        instances = client.collection.query(inst_name=INPUT_VM_NAME,
                                            provider=INPUT_PROVIDER_NAME,
                                            network=INPUT_NETWORK,
                                            subnet=INPUT_SUBNET)
        if instances and type(instances) is list:
            print("Multiple instances found.")
            print("Supply more options to narrow selection")
            raise SystemExit(1)
        elif not instances:
            print("No Instance found to delete")
            raise SystemExit(1)
    except SystemExit as e:
        print(e.message)
        raise SystemExit(1)

    # 2. attempt to delete the instance
    client.collection = "instances"
    id = instances['id']
    task_id = client.collection.terminate(inst_name=id,
                                          by_id=True)
    print("INFO: Task ID of terminate instance: {0}".format(task_id))

    # check the deletion task, and wait for it to be finished
    client.collection = "tasks"
    done = False
    while not done:
        result = client.collection.status(task_id)
        if result.state == "Finished":
            done = True
        sleep(5)

    if result.status == "Error":
        print("Deleting the instance: {0} failed: {1}".format(INPUT_VM_NAME,
                                                              result.message))
        raise SystemExit(1)

    # 3. remove the vm reference in MIQ/Cloudforms, if deletion is successful
    client.collection = "vms"
    task_id = client.collection.delete(vm_name=id,
                                       by_id=True)
    print("INFO: Task ID for attempt to delete vm: {0}".format(task_id))

    # check the task and make sure the vm reference is removed successfully
    client.collection = "tasks"
    done = False
    while not done:
        result = client.collection.status(task_id)
        if result.state == "Finished":
            done = True
        sleep(5)

    if result.status == "Error":
        print("Deleting the VM reference: {0} failed: "
              "{1}".format(INPUT_VM_NAME, result.message))
        raise SystemExit(1)

    print("Deletion successfully completed")

On completion, you should receive a Success or Error message.

.. code-block:: bash

    Deletion successfully completed
