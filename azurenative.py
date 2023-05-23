import config
import dataclasses
from dataclasses import dataclass, field, asdict
from typing import Optional, Sequence, List
from abc import ABC, abstractmethod
import re
from collections.abc import Iterable
import uuid
import secrets
import string

import pulumi
import pulumi_azure_native.resources as resources
import pulumi_azure_native.managedidentity as managedidentity
import pulumi_azure_native.authorization as authorization
import pulumi_azure_native.network as network
import pulumi_azure_native.keyvault as keyvault
import pulumi_azure_native.containerservice as containerservice
import pulumi_azure_native.containerregistry as containerregistry

pulumiConfig : pulumi.Config = pulumi.Config()

@dataclass
class BuildContext:
    team: str
    service: str
    environment: str
    location: str
    tags: dict[str, str]

    resource_cache: dict = field(init=False, repr=False, default_factory=dict)

    async def add_resource_to_cache(self, name: str, resource: pulumi.CustomResource):
        self.resource_cache[name] = resource

    async def get_resource_from_cache(self, name: str) -> pulumi.CustomResource:
        if name in self.resource_cache:
            return self.resource_cache[name]

        return None

    def get_default_resource_name(self, unique_identifier: str) -> str:
        return f"{self.team}-{self.service}-{self.environment}-{unique_identifier}"

    def get_default_resource_name_clean(self, unique_identifier: str) -> str:
        return self.get_default_resource_name(unique_identifier).replace("-", "")
    
    def generate_password(length=16):
        all_characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(all_characters) for _ in range(length))
        return password

# region Resources
class BaseResource(ABC):

    def __init__(self, name: str, context: BuildContext):
        self.name = name
        self.context = context

    @abstractmethod
    async def find(self, id: Optional[str] = None) -> pulumi.CustomResource:
        pass

    @abstractmethod
    async def create(self, args: any) -> pulumi.CustomResource:
        pass

    async def getResourceValue(self, baseResource : pulumi.CustomResource, outputChain : str) -> Optional[str]:
        outputs = outputChain.split("->")
                
        if baseResource is None:
            return None      
        
        # loop through nested output parameters until we get to the last resource
        for outputName in outputs[:-1]:
            baseResource = getattr(baseResource, outputName)
            if baseResource is None:
                return None
    
        return getattr(baseResource, outputs[-1] )

    async def replaceValue(self, args : any, propertyName : str, value : str | pulumi.Output[any]) -> str:
        newValue : str = value
        m = re.search(r"Resource (.+),\s?(.+)", value)
        if m is not None:
            resource = await self.context.get_resource_from_cache(m.group(1))
            newValue = await self.getResourceValue(resource, m.group(2)) or newValue            
        else:
            m = re.search(r"Secret (.+)", value)
            if m is not None:
                secret = pulumiConfig.require_secret(m.group(1))
                newValue = secret or value

        if value != newValue:
            setattr(args, propertyName, newValue)

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

    async def build(self, id: Optional[str] = None, args: Optional[any] = None) -> None:
        if id is not None:
            try:
                resource_group = await self.find(id)
            except Exception as e:
                pulumi.log.warn(f"Failed to find existing resource group with id {id}: {e}")
                return

        if args is not None:
            await self.replaceInputArgs(args);
            resource_group = await self.create(args)

        await self.context.add_resource_to_cache(self.name, resource_group)

class ResourceGroup(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[resources.ResourceGroup]:
        if not id:
            return None

        return resources.ResourceGroup.get(self.context.get_default_resource_name(self.name), id)

    async def create(self, args: config.ResourceGroupArgs) -> resources.ResourceGroup:
        resource_group_args = resources.ResourceGroupArgs(
            resource_group_name = args.resource_group_name or self.context.get_default_resource_name(self.name),
            location = args.location or self.context.location,
            tags = args.tags or self.context.tags,
        )
        return resources.ResourceGroup(self.context.get_default_resource_name(self.name), args=resource_group_args)

class ManagedIdentity(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[managedidentity.UserAssignedIdentity]:
        if not id:
            return None

        return managedidentity.UserAssignedIdentity.get(self.context.get_default_resource_name(self.name), id)

    async def create(self, args: config.ManagedIdentityArgs) -> managedidentity.UserAssignedIdentity:
        managed_identity_args = managedidentity.UserAssignedIdentityArgs(
            resource_group_name = args.resource_group_name or pulumi.log.warn("Resource Group Name is required for managed identity"),
            location = args.location or self.context.location,
            tags = args.tags or self.context.tags,
        )
        return managedidentity.UserAssignedIdentity(self.context.get_default_resource_name(self.name), args=managed_identity_args)

class RoleAssignment(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[authorization.RoleAssignment]:
        if not id:
            return None

        return authorization.RoleAssignment.get(self.name, id)

    async def create(self, args: config.RoleAssignmentArgs) -> authorization.RoleAssignment:
        role_assignment_args = authorization.RoleAssignmentArgs(
            role_assignment_name= str(uuid.uuid4()),
            description = args.description or "",
            principal_id = args.principal_id or pulumi.log.warn("Principal ID is required for role assignment"),
            principal_type = args.principal_type or "ServicePrincipal",
            role_definition_id = args.role_definition_id or pulumi.log.warn("Role definition ID is required for role assignment"),
            scope = args.scope or pulumi.log.warn("Scope is required for role assignment"),
        )
        return authorization.RoleAssignment(
            self.context.get_default_resource_name(self.name), 
            args=role_assignment_args,
            opts=pulumi.ResourceOptions(ignore_changes=["role_assignment_name"])
        )

class VirtualNetwork(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[network.VirtualNetwork]:
        if id is None:
            return None

        return network.VirtualNetwork.get(self.context.get_default_resource_name(self.name), id)

    async def create(self, args: config.VirtualNetworkArgs) -> network.VirtualNetwork:

        address_space_args = network.AddressSpaceArgs(
            address_prefixes = args.address_space.address_prefixes or pulumi.log.warn("address_prefixes is required for virtual network creation"),
        )

        virtual_network_args = network.VirtualNetworkArgs(
            resource_group_name = args.resource_group_name or pulumi.log.warn("Resource Group Name is required for virtual network"),
            location = args.location or self.context.location,
            address_space = address_space_args,
            tags = args.tags or self.context.tags,
        )
        
        return network.VirtualNetwork(self.context.get_default_resource_name(self.name), args=virtual_network_args)

class Subnet(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[network.Subnet]:
        if id is None:
            return None

        return network.Subnet.get(self.context.get_default_resource_name(self.name), id)

    async def create(self, args: config.SubnetInitArgs) -> network.Subnet:
        subnet_args = network.SubnetInitArgs(
            resource_group_name = args.resource_group_name or pulumi.log.warn("Resource Group Name is required for subnet creation"),
            virtual_network_name = args.virtual_network_name or pulumi.log.warn("Virtual Network Name is required for subnet creation"),
            address_prefix = args.address_prefix or pulumi.log.warn("address_prefix is required for subnet creation"),
        )
        return network.Subnet(self.context.get_default_resource_name(self.name), args=subnet_args)

class KeyVault(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[keyvault.Vault]:
        if id is None:
            return None

        return keyvault.Vault.get(self.context.get_default_resource_name(self.name), id)

    async def create(self, args: config.KeyVaultArgs) -> keyvault.Vault:
        vault_properties: Optional[keyvault.VaultPropertiesArgs] = None
        if args.properties is not None:
            properties = args.properties
            vault_properties = keyvault.VaultPropertiesArgs(
                sku=properties.sku if properties.sku is not None else {"family": "A", "name": "standard"},
                create_mode=properties.create_mode if properties.create_mode is not None else "default",
                access_policies=properties.access_policies if properties.access_policies is not None else [],
                tenant_id=properties.tenant_id if properties.tenant_id is not None else pulumi.log.warn("tenant_id is required for keyvault creation"),
                enabled_for_deployment=properties.enabled_for_deployment if properties.enabled_for_deployment is not None else True,
                enabled_for_disk_encryption=properties.enabled_for_disk_encryption if properties.enabled_for_disk_encryption is not None else True,
                enabled_for_template_deployment=properties.enabled_for_template_deployment if properties.enabled_for_template_deployment is not None else True,
                enable_rbac_authorization=properties.enable_rbac_authorization if properties.enable_rbac_authorization is not None else False,
                enable_soft_delete=properties.enable_soft_delete if properties.enable_soft_delete is not None else False,
            )

        vault_args = keyvault.VaultArgs(
            properties=vault_properties,
            vault_name=args.vault_name or self.context.get_default_resource_name(self.name),
            resource_group_name=args.resource_group_name or self.context.get_default_resource_name(self.name),
            location=args.location or self.context.location,
            tags=args.tags or self.context.tags,
        )

        return keyvault.Vault(self.context.get_default_resource_name(self.name), args=vault_args)

class ContainerRegistry(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[containerregistry.Registry]:
        if id is None:
            return None

        return containerregistry.Registry.get(self.context.get_default_resource_name(self.name), id)

    async def create(self, args: config.containerregistry) -> containerregistry.Registry:
        registry_args = containerregistry.RegistryArgs(
            resource_group_name=args.resource_group_name or self.context.get_default_resource_name(self.name),
            location=args.location or self.context.location,
            sku=args.sku or containerregistry.SkuArgs(name="Standard"),
            admin_user_enabled=args.admin_user_enabled or False,
            network_rule_set=args.network_rule_set or {"default_action": "Allow"},
            policies=args.policies or {"quarantine_policy": {"status": "disabled"}},
            tags=args.tags or self.context.tags,
        )

        return containerregistry.Registry(self.context.get_default_resource_name_clean(self.name), registry_args)
    
class ManagedCluster(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[containerservice.ManagedCluster]:
        if not id:
            return None

        return containerservice.ManagedCluster.get(self.context.get_default_resource_name(self.name), id)
    
    async def create(self, args: config.ManagedClusterArgs) -> containerservice.ManagedCluster:
        agent_pool_profiles_args: list[containerservice.ManagedClusterAgentPoolProfileArgs] = []
        if args.agent_pool_profiles is not None:
            for agent_pool_profile in args.agent_pool_profiles:
                agent_pool_profile_args = containerservice.ManagedClusterAgentPoolProfileArgs(
                    name=agent_pool_profile.name if agent_pool_profile.name is not None else "systempool",
                    mode=agent_pool_profile.mode if agent_pool_profile.mode is not None else "System",
                    vm_size=agent_pool_profile.vm_size if agent_pool_profile.vm_size is not None else "Standard_b2ms",
                    type=agent_pool_profile.type if agent_pool_profile.type is not None else "VirtualMachineScaleSets",
                    enable_auto_scaling=agent_pool_profile.enable_auto_scaling if agent_pool_profile.enable_auto_scaling is not None else True,
                    enable_encryption_at_host=agent_pool_profile.enable_encryption_at_host if agent_pool_profile.enable_encryption_at_host is not None else False,
                    count=agent_pool_profile.count if agent_pool_profile.count is not None else 1,
                    min_count=agent_pool_profile.min_count if agent_pool_profile.min_count is not None else 1,
                    max_count=agent_pool_profile.max_count if agent_pool_profile.max_count is not None else 3,
                    max_pods=agent_pool_profile.max_pods if agent_pool_profile.max_pods is not None else 30,
                    os_type=agent_pool_profile.os_type if agent_pool_profile.os_type is not None else "Linux",
                    orchestrator_version=agent_pool_profile.orchestrator_version if agent_pool_profile.orchestrator_version is not None else "1.24.10",
                    vnet_subnet_id=agent_pool_profile.vnet_subnet_id if agent_pool_profile.vnet_subnet_id is not None else None,
                )
                agent_pool_profiles_args.append(agent_pool_profile_args)

        managed_cluster_args = containerservice.ManagedClusterArgs(
            resource_group_name=args.resource_group_name or self.context.get_default_resource_name(self.name),
            location=args.location or self.context.location,
            dns_prefix=args.dns_prefix or self.context.get_default_resource_name(self.name),
            kubernetes_version=args.kubernetes_version or "1.24.10",
            enable_rbac=args.enable_rbac or True,
            tags=args.tags or self.context.tags,
            agent_pool_profiles=agent_pool_profiles_args,
        )
    
        return containerservice.ManagedCluster(self.context.get_default_resource_name(self.name), args=managed_cluster_args)
#endregion

class ResourceBuilder:

    def __init__(self, context: BuildContext):
        self.context = context
        self.location = context.location
        self.tags = context.tags

    async def build(self, config: config.AzureNative):
        await self.build_resource_groups(config.resource_groups)
        await self.build_managed_identities(config.managed_identities)
        await self.build_role_assignments(config.role_assignments)
        await self.build_key_vaults(config.key_vaults)
        await self.build_container_registries(config.container_registries)
        await self.build_virtual_networks(config.virtual_networks)
        await self.build_subnets(config.subnets)
        await self.build_managed_clusters(config.managed_clusters)

    async def build_resource_groups(self, configs: Optional[list[config.ResourceGroup]] = None):
        if configs is None:
            return

        for config in configs:
            builder = ResourceGroup(config.name, self.context)
            await builder.build(config.id, config.args)

    async def build_managed_identities(self, configs: Optional[list[config.ManagedIdentity]] = None):
        if configs is None:
            return

        for config in configs:
            builder = ManagedIdentity(config.name, self.context)
            await builder.build(config.id, config.args)

    async def build_role_assignments(self, configs: Optional[list[config.RoleAssignment]] = None):
        if configs is None:
            return

        for config in configs:
            builder = RoleAssignment(config.name, self.context)
            await builder.build(config.id, config.args)

    async def build_virtual_networks(self, configs: Optional[list[config.VirtualNetwork]] = None):
        if configs is None:
            return

        for config in configs:
            builder = VirtualNetwork(config.name, self.context)
            await builder.build(config.id, config.args)

    async def build_subnets(self, configs: Optional[list[config.Subnet]] = None):
        if configs is None:
            return

        for config in configs:
            builder = Subnet(config.name, self.context)
            await builder.build(config.id, config.args)

    async def build_key_vaults(self, configs: Optional[list[config.KeyVault]] = None):
        if configs is None:
            return

        for config in configs:
            builder = KeyVault(config.name, self.context)
            await builder.build(config.id, config.args)

    async def build_container_registries(self, configs: Optional[list[config.containerregistry]] = None):
        if configs is None:
            return

        for config in configs:
            builder = ContainerRegistry(config.name, self.context)
            await builder.build(config.id, config.args)

    async def build_managed_clusters(self, configs: Optional[list[config.ManagedCluster]] = None):
        if configs is None:
            return

        for config in configs:
            builder = ManagedCluster(config.name, self.context)
            await builder.build(config.id, config.args)
