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
from automapper import mapper

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
        args.location = args.location or self.context.location
        resource_group_args = mapper.to(resources.ResourceGroupArgs).map(args, use_deepcopy=False, skip_none_values=True)
        return resources.ResourceGroup(self.context.get_default_resource_name(self.name), args=resource_group_args)

class ManagedIdentity(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[managedidentity.UserAssignedIdentity]:
        if not id:
            return None

        return managedidentity.UserAssignedIdentity.get(self.context.get_default_resource_name(self.name), id)

    async def create(self, args: config.ManagedIdentityArgs) -> managedidentity.UserAssignedIdentity:
        args.resourceGroupName = args.resource_group_name or self.context.get_default_resource_name(self.name)
        args.location = args.location or self.context.location
        managed_identity_args = mapper.to(managedidentity.UserAssignedIdentityArgs).map(args, use_deepcopy=False, skip_none_values=True)
        
        return managedidentity.UserAssignedIdentity(self.context.get_default_resource_name(self.name), args=managed_identity_args)

class RoleAssignment(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[authorization.RoleAssignment]:
        if not id:
            return None

        return authorization.RoleAssignment.get(self.context.get_default_resource_name(self.name), id)

    async def create(self, args: config.RoleAssignmentArgs) -> authorization.RoleAssignment:
        role_assignment_args = authorization.RoleAssignmentArgs(
            role_assignment_name= str(uuid.uuid4()),
            description = args.description or "",
            principal_id = args.principal_id or pulumi.log.warn("Principal ID is required for role assignment"),
            principal_type = args.principal_type or "ServicePrincipal",
            role_definition_id = args.role_definition_id or pulumi.log.warn("Role definition ID is required for role assignment"),
            scope = args.scope or pulumi.log.warn("Scope is required for role assignment"),
        )
        return authorization.RoleAssignment(self.context.get_default_resource_name(self.name), args=role_assignment_args, opts=pulumi.ResourceOptions(ignore_changes=["role_assignment_name"]))

class VirtualNetwork(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[network.VirtualNetwork]:
        if id is None:
            return None

        return network.VirtualNetwork.get(self.context.get_default_resource_name(self.name), id)

    async def create(self, args: config.VirtualNetworkArgs) -> network.VirtualNetwork:
        args.location = args.location or self.context.location
        
        if args.address_space is not None:
            args.address_space = mapper.to(network.AddressSpaceArgs).map(args.address_space, use_deepcopy=False, skip_none_values=True)
        
        virtual_network_args = mapper.to(network.VirtualNetworkArgs).map(args, use_deepcopy=False, skip_none_values=True)
        return network.VirtualNetwork(self.context.get_default_resource_name(self.name), args=virtual_network_args)

class Subnet(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[network.Subnet]:
        if id is None:
            return None

        return network.Subnet.get(self.context.get_default_resource_name(self.name), id)

    async def create(self, args: config.SubnetArgs) -> network.Subnet:
        args.private_endpoint_network_policies = args.private_endpoint_network_policies or "Disabled"
        args.private_link_service_network_policies = args.private_link_service_network_policies or "Disabled"
        subnet_args = mapper.to(network.SubnetInitArgs).map(args, use_deepcopy=False, skip_none_values=True)
        return network.Subnet(self.context.get_default_resource_name(self.name), args=subnet_args)

class KeyVault(BaseResource):
    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[keyvault.Vault]:
        if id is None:
            return None

        return keyvault.Vault.get(self.name, id)

    async def create(self, args: config.KeyVaultArgs) -> keyvault.Vault:
        vault_properties: Optional[keyvault.VaultPropertiesArgs] = None
        if args.properties is not None:
            properties = args.properties
            vault_properties = keyvault.VaultPropertiesArgs(
                sku=properties.sku if properties.sku is not None else {"family": "A", "name": "standard"},
                create_mode=properties.create_mode if properties.create_mode is not None else "default",
                access_policies=properties.access_policies if properties.access_policies is not None else [],
                tenant_id=properties.tenant_id if properties.tenant_id is not None else pulumi.warn("Tenant ID is required for key vault"),
                enabled_for_deployment=properties.enabled_for_deployment if properties.enabled_for_deployment is not None else True,
                enabled_for_disk_encryption=properties.enabled_for_disk_encryption if properties.enabled_for_disk_encryption is not None else True,
                enabled_for_template_deployment=properties.enabled_for_template_deployment if properties.enabled_for_template_deployment is not None else True,
                enable_rbac_authorization=properties.enable_rbac_authorization if properties.enable_rbac_authorization is not None else False,
                enable_soft_delete=properties.enable_soft_delete if properties.enable_soft_delete is not None else False
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

    async def create(self, args: config.ContainerRegistryArgs) -> containerregistry.Registry:
        args.location = args.location or self.context.location
        args.registry_name = args.registry_name or self.context.get_default_resource_name_clean(self.name)
        args.network_rule_set = args.network_rule_set or {"default_action": "Allow"}
        args.sku = args.sku or containerregistry.SkuArgs(name="Standard")
        
        registry_args = mapper.to(containerregistry.RegistryArgs).map(args, use_deepcopy=False, skip_none_values=True)
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
                agent_pool_profile_args = mapper.to(containerservice.ManagedClusterAgentPoolProfileArgs).map(agent_pool_profile, use_deepcopy=False, skip_none_values=True)
                agent_pool_profiles_args.append(agent_pool_profile_args)
        aad_profile = mapper.to(containerservice.ManagedClusterAADProfileArgs).map(args.aad_profile, use_deepcopy=False, skip_none_values=True)
        # addon_profile = mapper.to(containerservice.ManagedClusterAddonProfileArgs).map(args.addon_profiles, use_deepcopy=False, skip_none_values=True)
        if args.identity is not None:
            identity = mapper.to(containerservice.ManagedClusterIdentityArgs).map(args.identity, use_deepcopy=False, skip_none_values=True)
        if args.sku is not None:
            sku = mapper.to(containerservice.ManagedClusterSKUArgs).map(args.sku, use_deepcopy=False, skip_none_values=True)
        managed_cluster_args = containerservice.ManagedClusterArgs(
            resource_group_name=args.resource_group_name or pulumi.warn("Resource group name is required for managed cluster"),
            location=args.location or self.context.location,
            dns_prefix=args.dns_prefix or self.context.get_default_resource_name(self.name),
            enable_rbac=args.enable_rbac or True,
            tags=args.tags or self.context.tags,
            agent_pool_profiles=agent_pool_profiles_args,
            aad_profile=aad_profile,
            # addon_profile=addon_profile,
            identity=identity,
            sku=sku,
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
        await self.build_virtual_networks(config.virtual_networks)
        await self.build_subnets(config.subnets)
        await self.build_container_registries(config.container_registries)
        await self.build_key_vaults(config.key_vaults)
        await self.build_managed_clusters(config.managed_clusters)
        await self.build_role_assignments(config.role_assignments)

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

    async def build_container_registries(self, configs: Optional[list[config.ContainerRegistry]] = None):
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
