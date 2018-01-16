==================
Automate DataStore
==================

This document is provided to give information about the Automate DataStore 
additions provided by the ManageIQ/Cloudforms CLI.  It describes the mehtods 
that are added.  How to import the code to ManageIQ/Cloudforms and how to run 
the code through the REST api.

Automate DataStore Methods
--------------------------

Methods
-------

Method                Instance             Description
________________________________________________________________________________
get_floating_ip       get_floating_ip      Create floating ip
allocate_floating_ip  allocateFloatingIP   Create & attach floating ip to vm
release_floating_ip   release_floating_ip  Detach & remove a floating ip
retire_floating_ip    retireFloatingIP     Detach & delete all floating ips from vm/instance

Method Inputs
-------------

Method                Inputs            Type     Required
________________________________________________________________________________
add_floating_ip       cloud_tenant_id   Integer  Yes
                      cloud_network_id  Integer  Yes
allocate_floating_ip  vm_name           String   Yes if vm_id not given
                      vm_id             Integer  Yes if vm_name not given
                      floating_network  String   No
release_floating_ip   floating_ip       String   Yes if floating_ip_id not given
                      floating_ip_id    Integer  Yes if floating_ip not given
retire_floating_ip    vm_name           String   Yes if vm_id not given
                      vm_id             Integer  Yes if vm_name not given

Import of Datastore to Cloudforms or ManageIQ
---------------------------------------------

Steps to import datastore to Cloudforms or ManageIQ:

1. Confirm 'Git Repositories Owner' is on in your CloudForms/ManageIQ system.
   Performed from Configuration.  The Configuration located in the drop down in
   the upper right hand corner.

   Settings->Zones

2. Perform Import - Using this git
   https://github.com/rhpit/manageiq-cli.git

   Automation->Automate->Import/Export


Running Automation code through the REST API
--------------------------------------------
 
1. Update the input json payload file with correct values for method.
   The values for instance and parameters should be updated.        

   Example content for get_floating_ip.json:
   {
     "uri_parts": {
     "namespace": "CF_MIQ_CLI/General",
     "class": "Methods",
     "instance": "get_floating_ip"
     },
     "parameters": {
       "cloud_network_id": 2,
       "cloud_tenant_id": 1
     },
     "requester": {
       "auto_approve": true
     }
   }

2. Execute Rest API automation_requests:

   http --verify=no -a <user>:<password> POST https://<manageIQ/cloudforms>:8443/api/automation_requests @<payload_file.json>

3. Keep checking for command to finish. Returned request_state equals 'finished'.
   <id> is the id returned for from command executed in step 2.

   http --verify=no -a <user>:<password> https://<manageIQ/cloudform>:8443/api/automation_requests/<id>

4. Get results from returned data. Once finished, options will be updated with
   the return data.

