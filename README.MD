# Pulumi Azure Template

This project is used to generate Azure resources based on the configuration provided in the `config.yaml` file, using Pulumi. 

## Prerequisites

- Python 3.7 or above
- Pulumi CLI (install from [official website](https://www.pulumi.com/docs/get-started/install/))

## Overview

The project uses three main files: `config.py`, `main.py`, and `azurenative.py`. 

This is in active development so please consider contributing by cloning. Setup Azure/Pulumi accounts, test building multiples to catch edge cases and help out :)

### `config.py`

This file contains various Python dataclasses that represent Azure resources like Managed Clusters, Subnets, Key Vaults, and others. Each dataclass maps to an Azure resource and its arguments. The `Config` dataclass at the end is the root dataclass that reads the `config.yaml` file.

### `main.py`

This file contains the main logic of the program. It reads the `config.yaml`, parses it into the `Config` dataclass, and then iterates through the teams, services, and environments defined in the config. For each environment, it initiates the `ResourceBuilder` from `azurenative.py` to build the resources.

### `azurenative.py`

This file contains the `ResourceBuilder` class, which is used to generate Azure resources based on the provided configuration.

This is the script that is responsible for building the Azure resources based on the configuration set in `config.yaml`.
Here's a high-level overview of its main components:

- `ResourceBuilder`: This class is used to construct Azure resources according to the parsed configuration. It takes an instance of the `BuildContext` which carries details about the team, service, environment, and location. 

- `BuildContext`: This class is used to store context about the current build process.

- `build` method: This asynchronous method in the `ResourceBuilder` class is used to build the resources based on the provided `AzureNative` object.

```python
class ResourceBuilder:
    def __init__(self, context: BuildContext):
        self.context = context

    async def build(self, config: Optional[AzureNative]):
        # Build resources here based on the config
```
You might have noticed that the `AzureNative` object includes lists of different Azure resources such as `resource_groups`, `managed_identities`, `role_assignments`, `virtual_networks`, `subnets`, `key_vaults`, `container_registries`, and `managed_clusters`. These represent the various resources that you can configure and manage using this script.

- `resource_groups`: A list of `ResourceGroup` objects, each representing a resource group in Azure.
- `managed_identities`: A list of `ManagedIdentity` objects, each representing a managed identity in Azure.
- `role_assignments`: A list of `RoleAssignment` objects, each representing a role assignment in Azure.
- `virtual_networks`: A list of `VirtualNetwork` objects, each representing a virtual network in Azure.
- `subnets`: A list of `Subnet` objects, each representing a subnet in Azure.
- `key_vaults`: A list of `KeyVault` objects, each representing a key vault in Azure.
- `container_registries`: A list of `containerregistry` objects, each representing a container registry in Azure.
- `managed_clusters`: A list of `ManagedCluster` objects, each representing a managed cluster in Azure.

Each of these objects has properties that match the options available for their respective Azure resources. For example, a `ManagedCluster` object has properties like `resource_group_name`, `network_profile`, `agent_pool_profiles`, and so on. These properties can be set in the `config.yaml` file.

The actual implementation of the resource building process will depend on the specifics of your project and the Azure resources you are working with. Always refer to the [Pulumi Azure-Native documentation](https://www.pulumi.com/registry/packages/azure-native/) for the most accurate and up-to-date information.

Please note that you must have the Pulumi application installed on your computer and properly set up to interact with your Azure account. You can check your setup by running `pulumi whoami` in your command line, which should return your Pulumi account username.

Once you've verified your setup, you can execute the `main.py` script by running `pulumi up` in your command line. This will start the process of building resources according to your `config.yaml` file. If you want to preview the changes without actually applying them, you can run `pulumi preview` instead.

## Usage

1. Define your Azure resources in the `config.yaml` file. You can use the dataclasses in `config.py` as a reference for what arguments each resource needs.

2. Run Pulumi to preview the changes:

```bash
pulumi preview
```
3. If the preview looks good you can apply the changes:

```bash
pulumi up
```
This will iterate through each environment defined in the config.yaml and generate the resources using Pulumi

## Example
An Example `config.yaml` could look like:

```yaml
teams:
  - name: team1
    services:
      - name: svc1
        environments:
         - name: labs
           location: canadacentral
           tags:
             CreatedBy: Pulumi
           azure_native:
            resource_groups:
              - name: rg-1
                args: []
            managed_identities:
              - name: uai-1
                args:
                  resource_group_name: Resource rg-1, name
            role_assignments:
              - name: ra-1
                args:
                  principal_id: Resource uai-1, principal_id
                  role_definition_id: /subscriptions/SUBSCRIPTION/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c
                  scope: Resource rg-1, id
            virtual_networks:
              - name: vnet-1
                args:
                  address_space:
                    address_prefixes:
                      - 10.200.0.0/16
                  resource_group_name: Resource rg-1, name
            subnets:
              - name: subnet-1
                args:
                  address_prefix: 10.200.1.0/24
                  resource_group_name: Resource rg-1, name
                  virtual_network_name: Resource vnet-1, name
            key_vaults:
             - name: kv-1
               args:
                resource_group_name: Resource rg-1, name
                properties:
                  sku:
                    family: A
                    name: standard
                  tenant_id: TENANT_ID
            managed_clusters:
              - name: aks1
                args:
                  resource_group_name: Resource rg-1, name
                  enable_rbac: true
                  aad_profile:
                    managed: true
                    enable_azure_rbac: true
                    admin_group_object_ids:
                      - ADMIN_GROUP_OBJECT_ID
                  identity:
                    type: "SystemAssigned"
                  sku:
                    name: "Basic"
                    tier: "Free"
                  agent_pool_profiles:
                    - name: "systempool"
                      count: 1
                      mode: "System"
                      vm_size: "Standard_b2ms"
                      type: "VirtualMachineScaleSets"
                      enableAutoScaling: true
                      enableEncryptionAtHost: false
                      minCount: 1
                      maxCount: 1
                      vnet_subnet_id: Resource subnet-1, id
                      orchestratorVersion: "1.24.10"
```
This would generate a series of resources in azure and shows how to use the cache system referencing properties with the shorthand.

## Explanation and Deep Dive

This section serves to help understand some aspects of the code that may not be familiar to folks coming from a non-programming background:
```python
    async def replaceValue(self, args : any, propertyName : str, value : str | pulumi.Output[any]) -> str:
        newValue : str = value
        m = re.search(r"Resource (.+),\s?(.+)", value)
        if m is not None:
            resource = await self.context.get_resource_from_cache(m.group(1))
            newValue = getattr(resource, m.group(2)) or value
        else:
            m = re.search(r"Secret (.+)", value)
            if m is not None:
              secret = pulumiConfig.require_secret(m.group(1))
              newValue = secret or value

        if value != newValue:
            setattr(args, propertyName, newValue)
```
This piece of code is a function that replaces certain values within your data structure. It's part of the 'search-and-replace' operation mentioned below:

The function `replaceValue()` takes three arguments: 

1. `args`: This is the object that the function is currently looking at.
2. `propertyName`: This is the specific property within that object which the function is considering replacing.
3. `value`: This is the current value of that property.

It first defines a new variable `newValue` to be the same as the current `value`.

Then it checks if the current `value` matches the pattern "Resource <something>, <something>". If it does, it finds the corresponding resource from a cache and replaces the `value` with a property of that resource.

If the `value` does not match the "Resource" pattern, it checks if it matches the pattern "Secret <something>". If it does, it gets the corresponding secret from the Pulumi configuration and replaces the `value` with this secret.

If neither pattern matches, `newValue` remains the same as the original `value`.

Finally, if `newValue` is different from the original `value`, it replaces the original value with `newValue` in the `args` object.

In summary, this function is checking each value in your data structure to see if it should be replaced with a value from a resource or a secret. If it should, it performs the replacement.

Additionally we have this section:

```python
    async def replaceInputArgs(self, args: any):
        properties = [a for a in dir(args) if not a.startswith('__') and not callable(getattr(args, a))]
        for property in properties:
            value = getattr(args, property)
            if value is not None:

                # loop iterables
                if (isinstance(value, Iterable)):
                    for item in value:
                        await self.replaceInputArgs(item)

                # deep replace on all child dataclasses
                if (dataclasses.is_dataclass(value)):
                    await self.replaceInputArgs(value)

                # only replace values for strings
                if isinstance(value, str):
                    await self.replaceValue(args, property, value)
```
This section of the code is an asynchronous method called `replaceInputArgs` in the `ResourceBuilder` class. The purpose of this method is to iterate over the properties of an input argument object and recursively replace any string values.

Let's break down the method:

- `properties = [a for a in dir(args) if not a.startswith('__') and not callable(getattr(args, a))]`: This line is using a list comprehension to get a list of all the properties in the `args` object. The `dir()` function is used to get a list of all attributes of the object. The list comprehension filters out any attributes that start with '__' (these are usually system attributes), and any attributes that are callable (i.e., methods).

- `for property in properties`: This line starts a loop over all the properties that were just defined.

- `value = getattr(args, property)`: For each property, this line gets the current value of the property.

- `if value is not None`: This line checks if the current value is not `None`. If it is `None`, the loop simply continues to the next property.

- `if (isinstance(value, Iterable))`: This line checks if the current value is an iterable (like a list or a dictionary). If it is, the method calls itself recursively for each item in the iterable.

- `if (dataclasses.is_dataclass(value))`: This line checks if the current value is a dataclass. If it is, the method again calls itself recursively, because a dataclass can have its own properties that might need to be replaced.

- `if isinstance(value, str)`: Finally, this line checks if the current value is a string. If it is, the method calls another method, `replaceValue()`, to replace the string value.

This process is repeated for all properties in the `args` object and all their child properties if they are iterable or dataclasses, until all string values have been replaced.

This code is essentially a deep search-and-replace function for a given data structure. Here's a simple explanation:

It takes an input object (like a complex configuration file) and goes through all its properties one by one. If it finds a property that is a list, dictionary, or any other type of collection, it digs deeper into that collection and repeats the process.

If it comes across a property that is a more complex object (a 'dataclass' in Python), it again digs deeper, looking at all the properties of that object.

Now, if it finds a property that is a simple string, it does a 'replace' operation on it. The specifics of this replacement are defined in the `replaceValue()` method, which isn't shown here.

So in short, this code is designed to traverse complex nested data structures and perform a specific operation (in this case, a 'replace' operation) on every string it encounters.
