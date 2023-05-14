# Pulumi Azure Template

This project is used to generate Azure resources based on the configuration provided in the `config.yaml` file, using Pulumi. 

## Prerequisites

- Python 3.7 or above
- Pulumi CLI (install from [official website](https://www.pulumi.com/docs/get-started/install/))
- Azure SDK for Python

## Overview

The project uses three main files: `config.py`, `main.py`, and `azurenative.py`. 

This is in active development so please consider contributing by cloning. Setup Azure/Pulumi accounts, test building multiples to catch edge cases and help out :)

### `config.py`

This file contains various Python dataclasses that represent Azure resources like Managed Clusters, Subnets, Key Vaults, and others. Each dataclass maps to an Azure resource and its arguments. The `Config` dataclass at the end is the root dataclass that reads the `config.yaml` file.

### `main.py`

This file contains the main logic of the program. It reads the `config.yaml`, parses it into the `Config` dataclass, and then iterates through the teams, services, and environments defined in the config. For each environment, it initiates the `ResourceBuilder` from `azurenative.py` to build the resources.

### `azurenative.py`

This file contains the `ResourceBuilder` class, which is used to generate Azure resources based on the provided configuration. 

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
This will iterate through each environment defined in the config.yaml and generate the resources using Pulumi and the Azure SDK for Python.

## Example
An Example `config.yaml` could look like:

```yaml
teams:
- name: Team1
  services:
  - name: Service1
    environments:
    - name: Dev
      location: West US
      azure_native:
        resource_groups:
        - name: rg1
          args: []
        managed_clusters:
        - name: Cluster1
          args:
            resource_group_name: Resource rg1, id
            agent_pool_profiles:
            - name: systempool
              vm_size: Standard_B2s
              count: 1
```
This would generate a managed cluster named "Cluster1" in the resource group "RG1" in the "Dev" environment of the "Service1" service in "Team1".
### `azurenative.py`

This is the script that is responsible for building the Azure resources based on the configuration set in `config.yaml`. It uses the Azure SDK for Python to interact with Azure and manage resources.

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

The actual implementation of the resource building process will depend on the specifics of your project and the Azure resources you are working with. Always refer to the [official Azure SDK for Python documentation](https://docs.microsoft.com/en-us/python/api/overview/azure/?view=azure-python) and the [Pulumi Azure-Native documentation](https://www.pulumi.com/registry/packages/azure-native/) for the most accurate and up-to-date information.

Please note that you must have the Pulumi application installed on your computer and properly set up to interact with your Azure account. You can check your setup by running `pulumi whoami` in your command line, which should return your Pulumi account username.

Once you've verified your setup, you can execute the `main.py` script by running `pulumi up` in your command line. This will start the process of building resources according to your `config.yaml` file. If you want to preview the changes without actually applying them, you can run `pulumi preview` instead.