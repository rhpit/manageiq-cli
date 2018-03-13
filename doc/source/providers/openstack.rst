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
module to create a new provider.

.. literalinclude:: ../../../example/providers/openstack/create.py
    :linenos:
    :lines: 32-

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

.. literalinclude:: ../../../example/providers/openstack/delete.py
    :linenos:
    :lines: 27-

On completion, you should receive an ID for your transaction.

.. code-block:: bash

    INFO: Successfully submitted request to delete provider: OpenStack.
    Request ID: <ID>.

Create Virtual Machine
----------------------

This section will guide you through creating a virtual machine on an
OpenStack system.  You will need to create a payload file in json format
with the details of the virtual machine and submit that request.

.. _osp_payload:

OpenStack Payload
+++++++++++++++++

In order to create a virtual machine, you need to create a payload in json
format.  The required and optional keys are shown after the example. The
following is an example of the payload for OpenStack with all options:

.. literalinclude:: ../../../example/openstack_provision_ex.json
    :language: JSON
    :linenos:

.. list-table::
    :widths: auto
    :header-rows: 1

    *   - Required Keys

    *   - email

    *   - tenant

    *   - image

    *   - network

    *   - flavor

    *   - vm_name


.. list-table::
    :widths: auto
    :header-rows: 1

    *   - Optional Keys

    *   - fip_pool

    *   - security_group

    *   - key_pair

    *   - floating_ip_id


Command Line
++++++++++++

There are multiple steps to provisioning.  If you wish to have an associated
floating ip with your virtual machine, start with :ref:`osp_cmd_step1`, else
start with :ref:`osp_cmd_step2`

.. _osp_cmd_step1:

1. Get a floating ip address
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will need to create an automation request to create a floating ip
address.  In order to create a floating ip address, you need to pass a
payload with a value for the floating ip pool and tenant name.

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli automation_requests create --method gen_floating_ip \
     --payload {\"fip_pool\":\"<floating_ip_pool>\"\,\"tenant\":\"<tenant>\"}

The output should look like the following:

.. code-block:: bash
    :linenos:

    INFO: Attempt to create an automation request
    INFO: Automation request created: 138.

Now, you will query the request task that it creates until it is complete:

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli request_tasks status 138

The output will look like the following, when it is complete

.. code-block:: bash
    :linenos:

    INFO: --------------------------------------------------
    INFO:                      Request                      
    INFO: --------------------------------------------------
    INFO:  * ID: 138
    INFO:  * Description: Automation Task
    INFO:  * STATE: finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Automation Request completed
    INFO: --------------------------------------------------

.. warning:: If you get an error running this command that states the
    following: "WARNING: Request id: <id> not found!", this is most likely
    because the automation request has not created the request task yet.
    The automation request executes in stages. In the states of being queued or
    pending, the request task will not be created yet.  Once, the automation
    request task becomes active, the request task gets created.

Once the request to create a floating ip is complete, query the automation
request to get the id of the floating ip, which will be included in the
provision request.


.. code-block:: bash
    :linenos:

    (miq-client)$ miqcli --verbose automation_requests status 138

.. note:: make sure \- \-verbose is used to get the floating ip, or else it will
       not be displayed


.. code-block:: bash
    :linenos:

    INFO: --------------------------------------------------
    INFO:                 Automation request                
    INFO: --------------------------------------------------
    INFO:  * ID: 138
    INFO:  * STATE: finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Automation Request completed
    DEBUG: 
    {   u'attrs': {   u'cloud_network_id': 2,
                      u'cloud_tenant_id': 1,
                      u'userid': u'admin'},
        u'class_name': u'Methods',
        u'delivered_on': u'2018-03-12T12:27:22.667Z',
        u'instance_name': u'get_floating_ip',
        u'namespace': u'CF_MIQ_CLI/General',
        u'return': u'{"status":"success",
                      "return":{"<floating_ip_address>":<floating_ip_address_id>}}',
        u'user_id': 1}

.. _osp_cmd_step2:

2. Create a provision request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a payload as specified in :ref:`osp_payload` Then create a provision
request.  The following example shows a payload created with the name 
**openstack_provision_ex.json**:

.. code-block:: bash
    :linenos:

     (miq-client) $ miqcli --verbose provision_requests create \
     --provider OpenStack --payload_file openstack_provision_ex.json

The output should look like the following:

.. code-block:: bash
    :linenos:

    INFO: Attempt to create a provision request
    DEBUG: Payload for the provisioning request: {'requester': {'owner_email': u'<email_address>'},
    'template_fields': {'guid': u'15a9aea0-0b75-11e8-b5a8-0242ac110002'},
    'vm_fields': {'cloud_network': 1,
                  'cloud_tenant': 1,
                  'floating_ip_address': <floating_ip_address_id>,
                  'guest_access_key_pair': 2,
                  'instance_type': 2,
                  'placement_auto': 'false',
                  'security_groups': 1,
                  'vm_name': u'<vm_instance_name>'}}
    INFO: Provisioning request created: 141

.. note:: The example above shows a payload, which is differs from the input.
   The payload the client uses is a simplified format, and the format that
   cloudforms accepts is generated by the CLI, the verbose mode is a good way
   to verify your input has been set properly.

Now, you want to watch the request task until the provisioning request is
finished.


.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli request_tasks status 141

The output will look like the following, the output shown below is an exmample
of checking the request_tasks status multiple times:

.. code-block:: bash
    :linenos:

    INFO: --------------------------------------------------
    INFO:                      Request                      
    INFO: --------------------------------------------------
    INFO:  * ID: 141
    INFO:  * Description: Provision from [rhel-7.3-server-x86_64-latest] to [<vm_instance_name>]
    INFO:  * STATE: active
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: VM Provisioning initiated
    INFO: --------------------------------------------------

    INFO: --------------------------------------------------
    INFO:                      Request                      
    INFO: --------------------------------------------------
    INFO:  * ID: 141
    INFO:  * Description: Provision from [rhel-7.3-server-x86_64-latest] to [<vm_instance_name>]
    INFO:  * STATE: finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: [EVM] VM [<vm_instance_name>] IP [172.16.5.48] Provisioned Successfully
    INFO: --------------------------------------------------

Now that your machine is successfully provisioned, you may want to get
additional data, like the ip address, of the instance. You can accomplish
this task by querying the instance:

.. code-block:: bash
    :linenos:

     (miq-client) $ miqcli instances query <vm_instance_name> \
     --provider OpenStack --attr floating_ip

The output will look like the following:

.. code-block:: bash
    :linenos:

    INFO: --------------------------------------------------
    INFO:                   Instance Info                   
    INFO: --------------------------------------------------
    INFO:  * ID: 1520
    INFO:  * NAME: <vm_instance_name>
    INFO:  * FLOATING_IP: {u'status': u'ACTIVE', u'cloud_tenant_id': 1,
    u'network_port_id': 778, u'type': u'ManageIQ::Providers::Openstack::
    NetworkManager::FloatingIp', u'cloud_network_id': 2, u'fixed_ip_address':
    u'172.16.5.48', u'address': u'10.8.249.238', u'ems_ref': u'234b16d6-f022-
    4cb4-adc2-7a9037fc4985', u'ems_id': 4, u'vm_id': 1520, u'id': 781}


To see all options for querying your instance, check the **help** option:

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli instances query <vm_instance_name> --help

Python Code
+++++++++++

This code example will demonstrate how you can use the client in a Python
module to create a virtual machine. Create the payload file(as specified
in :ref:`osp_payload`), and **update the code below with the name of your
payload_file** or call your payload file  "openstack_provision_ex.json", 
and execute the code below. If you want a floating ip, you only need to
add a value for the optional **fip_pool** key (you do not need to set the
floating_ip_id, the code will create a floating ip, get the id and add it
to the provisioning request), else just set the Required keys. The code
accomplishes the following tasks:

* Checks if the user wants a floating ip, if so call a Cloudforms automate
  request to create the floating ip and get its id.  It will wait for the
  request to be complete.

* Next it will call the provision request with the payload date and create
  a provision request.  It will wait for the request to be complete, and if
  there is an associated floating ip, it will print out the ip address that
  gets attached.


.. literalinclude:: ../../../example/osp_provision_example.py
    :lines: 17-
    :linenos:

The output from the OpenStack provisioning example will look like the
following:

.. code-block:: bash
    :linenos:

    INFO: Attempt to create an automation request
    INFO: Automation request created: 136.
    INFO: --------------------------------------------------
    INFO:                 Automation request                
    INFO: --------------------------------------------------
    INFO:  * ID: 136
    INFO:  * STATE: pending
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Automation Request - Request Created
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                 Automation request                
    INFO: --------------------------------------------------
    INFO:  * ID: 136
    INFO:  * STATE: queued
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: State Machine Initializing
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                 Automation request                
    INFO: --------------------------------------------------
    INFO:  * ID: 136
    INFO:  * STATE: active
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Automation Request initiated
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                      Request                      
    INFO: --------------------------------------------------
    INFO:  * ID: 136
    INFO:  * Description: Automation Task
    INFO:  * STATE: active
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Automation Request initiated
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                      Request                      
    INFO: --------------------------------------------------
    INFO:  * ID: 136
    INFO:  * Description: Automation Task
    INFO:  * STATE: finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Automation Request completed
    INFO: --------------------------------------------------
    Options from the automate request: {'namespace': 'CF_MIQ_CLI/General', 'class_name':
    'Methods', 'instance_name': 'get_floating_ip', 'user_id': 1, 'attrs': {'cloud_network_id':
    2, 'cloud_tenant_id': 1, 'userid': 'admin'}, 'delivered_on': '2018-03-09T20:07:50.248Z',
    'return': '{"status":"success","return":{"10.8.249.199":753}}'}
    got floating ip: 10.8.249.199: 753
    updated payload data w/floating ip: {'email': '<email_address_set>', 'tenant':
    'pit-jenkins', 'image': 'rhel-7.4-server-x86_64-latest', 'security_group':
    'default', 'network': 'pit-jenkins', 'flavor': 'm1.small', 'key_pair': 'pit-jenkins',
    'vm_name': '<instance_name>', 'fip_pool': '10.8.240.0', 'floating_ip_id': 753}
    INFO: Attempt to create a provision request
    INFO: Provisioning request created: 137
    ID of the request: 137
    INFO: --------------------------------------------------
    INFO:                 Provision request                 
    INFO: --------------------------------------------------
    INFO:  * ID: 137
    INFO:  * VM: <instance_name>
    INFO:  * STATE: pending
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: VM Provisioning - Request Created
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                 Provision request                 
    INFO: --------------------------------------------------
    INFO:  * ID: 137
    INFO:  * VM: <instance_name>
    INFO:  * STATE: queued
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: [EVM] VM [<instance_name>] Step [Provision] Status [Creating VM] Message [State Machine Initializing] 
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                 Provision request                 
    INFO: --------------------------------------------------
    INFO:  * ID: 137
    INFO:  * VM: <instance_name>
    INFO:  * STATE: active
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: [EVM] VM [<instance_name>] Step [CheckProvisioned] Status [Creating VM] Message [Creating VM] Current Retry Number [1]
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                      Request                      
    INFO: --------------------------------------------------
    INFO:  * ID: 137
    INFO:  * Description: Provision from [rhel-7.4-server-x86_64-latest] to [<instance_name>]
    INFO:  * STATE: provisioned
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Finished New VM Customization
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                 Provision request                 
    INFO: --------------------------------------------------
    INFO:  * ID: 137
    INFO:  * VM: <instance_name>
    INFO:  * STATE: finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: [EVM] VM [<instance_name>] IP [172.16.5.51] Provisioned Successfully
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                   Instance Info                   
    INFO: --------------------------------------------------
    INFO:  * ID: 1463
    INFO:  * NAME: <instance_name>
    INFO:  * FLOATING_IP: {'id': 753, 'type': 'ManageIQ::Providers::Openstack::
    NetworkManager::FloatingIp', 'ems_ref': 'a5507247-03f6-4140-8075-22903be3fb7a',
    'address': '10.8.249.199', 'ems_id': 4, 'vm_id': 1463, 'cloud_tenant_id': 1,
    'network_port_id': 751, 'cloud_network_id': 2, 'fixed_ip_address': '172.16.5.51',
    'status': 'ACTIVE'}
    INFO: --------------------------------------------------
    Floating ip for <instance_name>: 10.8.249.199

Delete Virtual Machine
----------------------

This section will guide you through how you can use the client to delete an
instance on OpenStack.

.. _osp_delete_cmd:

Command Line
++++++++++++

If you have an associated ip address, you need to query for the id and
send an automated request to delete the id prior to deleting the instance,
because just deleting the instance, will not delete the floating ip.  If you
wish to have an associated  floating ip with your virtual machine, start with
:ref:`osp_del_cmd_step1`, else start with :ref:`osp_del_cmd_step2`

.. _osp_del_cmd_step1:

1. Release the floating ip address
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You want to start, by querying the instance to ge the id of the floating ip:

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli instances query <instance_name> \
    --attr floating_ip
    --provider OpenStack

Output will look like this:

.. code-block:: bash
    :linenos:

    INFO: --------------------------------------------------
    INFO:                   Instance Info                   
    INFO: --------------------------------------------------
    INFO:  * ID: 1249
    INFO:  * NAME: <instance_name>
    INFO:  * FLOATING_IP: {u'status': u'ACTIVE', u'cloud_tenant_id': 1,  
    u'network_port_id': 588, u'type': u'ManageIQ::Providers::Openstack::
    NetworkManager::FloatingIp', u'cloud_network_id': 2, u'fixed_ip_address':
    u'172.16.5.51', u'address': u'10.8.242.110', u'ems_ref': u'7f31f0b1-3077-
    47a2-9cc5-726dd83e1925', u'ems_id': 4, u'vm_id': 1249, u'id': 590}
    INFO: --------------------------------------------------

From this output, we will look for the id for the floating ip, in the
example above, we can see the id is 590 (the last value), we will use this id
to release the floating ip, which is the next step.

.. code-block:: bash
    :linenos:

    (miq-client)$ miqcli automation_requests create \
    --method release_floating_ip --payload {\"floating_ip_id\":590}

Output will look like this:

.. code-block:: bash
    :linenos:

    INFO: Attempt to create an automation request
    INFO: Automation request created: 134.

Next we will check the status of the ip being released, with the given id.
You should keep checking the status until the STATE is finished:

.. code-block:: bash
    :linenos:

    (miq-client)$ miqcli request_tasks status 134

The output of a request task that is finished:

.. code-block:: bash
    :linenos:

    INFO: --------------------------------------------------
    INFO:                      Request                      
    INFO: --------------------------------------------------
    INFO:  * ID: 134
    INFO:  * Description: Automation Task
    INFO:  * STATE: finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Automation Request completed
    INFO: --------------------------------------------------

.. warning:: If you get an error running this command that states the
    following: "WARNING: Request id: <id> not found!", this is most likely
    because the automation request has not created the request task yet.
    The automation request can be in states: queued and pending, and when
    it becomes active, is the point when the request task gets created.

.. _osp_del_cmd_step2:

2. Delete the OpenStack Instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You must delete the OpenStack instance and then after that is completed,
you must delete Cloudforms reference to that instance. You can check all
possible filter options that you can use to delete the instance:

.. code-block:: bash
    :linenos:

    (miq-client)$ miqcli instances terminate --help

We will delete using the instances's id and using a Provider that is set in
Cloudforms with the name "OpenStack", the vm_id can be seen from our previous
query of the vm, see :ref:`osp_delete_cmd`

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli instances terminate 1249 --provider OpenStack --by_id True

The output will look like the following:

.. code-block:: bash
    :linenos:

     INFO: --------------------------------------------------
     INFO:                   Instance Info                   
     INFO: --------------------------------------------------
     INFO:  * ID: 1249
     INFO:  * NAME: <instance_name>
     INFO: --------------------------------------------------
     INFO: Task to terminate 1249 created: 586 

Now, we will watch the created deletion task until it is complete. In the 
example above the task is 586, so we will check that task:

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli tasks status 586

The final output when deletion is complete will look like the following:

.. code-block:: bash
    :linenos:

    INFO: --------------------------------------------------
    INFO:                       Tasks                       
    INFO: --------------------------------------------------
    INFO:  * ID: 586
    INFO:  * Name: Instance id:1249 name:'<instance_name>' terminating
    INFO:  * STATE: Finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Task completed successfully
    INFO: --------------------------------------------------

Now, the final step is to delete teh Cloudforms refrence for the instance. To
see all filter options that can be used for deletion run the following cmd:

.. code-block:: bash
    :linenos:

    miqcli vms delete --help

For this example we will use a provider on Cloudforms with the name that is
set to "OpenStack" and use the vm id, which is the same as the instance id.
So the deletion command will be the following:

.. code-block:: bash
    :linenos:

    (miq-client) $ miqcli vms delete 1249 --provider OpenStack --by_id True

The output will show the created task that was created to perform the
deletion:

.. code-block:: bash
    :linenos:

    INFO: --------------------------------------------------
    INFO:                      Vm Info                      
    INFO: --------------------------------------------------
    INFO:  * ID: 1249
    INFO:  * NAME: <instance_name>
    INFO: --------------------------------------------------
    INFO: Task to delete 1249 created: 587

Finally, we will check the deletion task until it has completed, by running
the following command.

.. code-block:: bash
    :linenos:

    INFO: --------------------------------------------------
    INFO:                       Tasks                       
    INFO: --------------------------------------------------
    INFO:  * ID: 587
    INFO:  * Name: VM id:1249 name:'cbn_ffinteropnss_ifql4' deleting
    INFO:  * STATE: Finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Task completed successfully
    INFO: --------------------------------------------------

Python Code
+++++++++++

This code example will demonstrate how you can use the client in a Python
module to delete an OpenStack instance. Before running the Python code, replace
the values for INPUT_VM_NAME, INPUT_PROVIDER_NAME, INPUT_NETWORK, INPUT_TENANT,
and INPUT_SUBNET.  The code accomplishes the following tasks:

* Query the instance to see if there is an associated ip.

* If there is an associated ip, it will attempt to delete it, and wait for
  success.

* It will then attempt to delete the instance.

* Finally, it will attempt to delete the instance reference in Cloudforms.


.. literalinclude:: ../../../example/osp_deletion_example.py
   :lines: 16-
   :linenos:

The output should look like the following:

.. code-block:: bash
    :linenos:

    INFO: --------------------------------------------------
    INFO:                   Instance Info                   
    INFO: --------------------------------------------------
    INFO:  * ID: 1222
    INFO:  * NAME: <instance_name>
    INFO:  * FLOATING_IP: {'id': 569, 'type': 'ManageIQ::Providers::Openstack::
    NetworkManager::FloatingIp', 'ems_ref': '05782b7f-602c-4566-bee6-c4fddb1928d8',
    'address': '10.8.248.129', 'ems_id': 4, 'vm_id': 1222, 'cloud_tenant_id': 1,
    'network_port_id': 565, 'cloud_network_id': 2, 'fixed_ip_address': '172.16.5.10',
    'status': 'ACTIVE'}
    INFO:  * EXT_MANAGEMENT_SYSTEM: {'id': 3, 'name': 'OpenStack', 'created_on':
    '2018-02-06T19:34:58Z', 'updated_on': '2018-03-09T19:32:46Z', 'guid': 
    'd0c32d7a-0b74-11e8-b5a8-0242ac110002', 'zone_id': 1, 'type': 'ManageIQ::
    Providers::Openstack::CloudManager', 'api_version': 'v2', 'provider_region':
    '', 'last_refresh_date': '2018-03-09T19:32:46Z', 'tenant_id': 1,
    'tenant_mapping_enabled': False}
    INFO: --------------------------------------------------
    INFO: Attempt to create an automation request
    INFO: Automation request created: 135.
    INFO: --------------------------------------------------
    INFO:                 Automation request                
    INFO: --------------------------------------------------
    INFO:  * ID: 135
    INFO:  * STATE: pending
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Automation Request - Request Created
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                 Automation request                
    INFO: --------------------------------------------------
    INFO:  * ID: 135
    INFO:  * STATE: queued
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: State Machine Initializing
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                 Automation request                
    INFO: --------------------------------------------------
    INFO:  * ID: 135
    INFO:  * STATE: active
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Automation Request initiated
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                      Request                      
    INFO: --------------------------------------------------
    INFO:  * ID: 135
    INFO:  * Description: Automation Task
    INFO:  * STATE: finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Automation Request completed
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                 Automation request                
    INFO: --------------------------------------------------
    INFO:  * ID: 135
    INFO:  * STATE: finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Automation Request completed
    INFO: --------------------------------------------------
    Options from the automate request: {'namespace': 'CF_MIQ_CLI/General',
    'class_name': 'Methods', 'instance_name': 'release_floating_ip', 'user_id':
    1, 'attrs': {'floating_ip_id': 569, 'userid': 'admin'}, 'delivered_on':
    '2018-03-09T19:55:33.590Z', 'return': '{"status":202,"return":""}'}
    INFO: --------------------------------------------------
    INFO:                   Instance Info                   
    INFO: --------------------------------------------------
    INFO:  * ID: 1222
    INFO:  * NAME: <instance_name>
    INFO: --------------------------------------------------
    INFO: Task to terminate 1222 created: 596
    Task ID of the deleted instance: 596
    INFO: --------------------------------------------------
    INFO:                       Tasks                       
    INFO: --------------------------------------------------
    INFO:  * ID: 596
    INFO:  * Name: Instance id:1222 name:'<instance_name>' terminating
    INFO:  * STATE: Queued
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Queued the action: [Instance id:1222 name:'<instance_name>' terminating] being run for user: [admin]
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                       Tasks                       
    INFO: --------------------------------------------------
    INFO:  * ID: 596
    INFO:  * Name: Instance id:1222 name:'<instance_name>' terminating
    INFO:  * STATE: Queued
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Queued the action: [Instance id:1222 name:'<instance_name>' terminating] being run for user: [admin]
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                       Tasks                       
    INFO: --------------------------------------------------
    INFO:  * ID: 596
    INFO:  * Name: Instance id:1222 name:'<instance_name>' terminating
    INFO:  * STATE: Finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Task completed successfully
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                      Vm Info                      
    INFO: --------------------------------------------------
    INFO:  * ID: 1222
    INFO:  * NAME: <instance_name>
    INFO: --------------------------------------------------
    INFO: Task to delete 1222 created: 597
    Task ID for the attempt to delete vm: 597
    INFO: --------------------------------------------------
    INFO:                       Tasks                       
    INFO: --------------------------------------------------
    INFO:  * ID: 597
    INFO:  * Name: VM id:1222 name:'<instance_name>' deleting
    INFO:  * STATE: Queued
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Queued the action: [VM id:1222 name:'<instance_name>' deleting] being run for user: [admin]
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                       Tasks                       
    INFO: --------------------------------------------------
    INFO:  * ID: 597
    INFO:  * Name: VM id:1222 name:'<instance_name>' deleting
    INFO:  * STATE: Queued
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Queued the action: [VM id:1222 name:'<instance_name>' deleting] being run for user: [admin]
    INFO: --------------------------------------------------
    INFO: --------------------------------------------------
    INFO:                       Tasks                       
    INFO: --------------------------------------------------
    INFO:  * ID: 597
    INFO:  * Name: VM id:1222 name:'<instance_name>' deleting
    INFO:  * STATE: Finished
    INFO:  * STATUS: Ok
    INFO:  * MESSAGE: Task completed successfully
    INFO: --------------------------------------------------
    Deletion successfully completed
