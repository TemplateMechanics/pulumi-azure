from dataclass_wizard import YAMLWizard
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
@dataclass
class RegistryArgs:
    resource_group_name: Optional[str] = None
    location: Optional[str] = None
    admin_user_enabled: Optional[bool] = None
    sku: Optional[dict[str, str]] = None
    network_rule_set: Optional[dict[str, str]] = None
    policies: Optional[dict[str, str]] = None
@dataclass
class containerregistry:
    name: str
    id: Optional[str] = None
    args: Optional[RegistryArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/containerregistry/registry/ ###
@dataclass
class IdentityArgs:
    type: Optional[str] = None
    user_assigned_identities: Optional[dict[str, str]] = None
@dataclass
class AgentPoolProfileArgs:
    name: Optional[str] = None
    mode: Optional[str] = None
    vm_size: Optional[str] = None
    type: Optional[str] = None
    enable_auto_scaling: Optional[bool] = None
    enable_encryption_at_host: Optional[bool] = None
    count: Optional[int] = None
    min_count: Optional[int] = None
    max_count: Optional[int] = None
    max_pods: Optional[int] = None
    vnet_subnet_id: Optional[str] = None
    orchestrator_version: Optional[str] = None
@dataclass
class AADProfileArgs:
    managed: Optional[bool] = None
    admin_group_object_ids: Optional[list[str]] = None
@dataclass
class NetworkProfileArgs:
    network_plugin: Optional[str] = None
    service_cidr: Optional[str] = None
    dns_service_ip: Optional[str] = None
    docker_bridge_cidr: Optional[str] = None
@dataclass
class ManagedClusterArgs:
    resource_group_name: Optional[str] = None
    network_profile: Optional[NetworkProfileArgs] = None
    agent_pool_profiles: Optional[list[AgentPoolProfileArgs]] = None
    enable_rbac: Optional[bool] = None
    aad_profile: Optional[AADProfileArgs] = None
    identity: Optional[IdentityArgs] = None
    identity_profile: Optional[dict[str, str]] = None
    tags: Optional[dict[str, str]] = None
@dataclass
class ManagedCluster:
    name: str
    id: Optional[str] = None
    args: Optional[ManagedClusterArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/containerservice/managedcluster/ ###
@dataclass
class VaultPropertiesArgs:
    sku: Optional[dict[str, str]] = None
    tenant_id: Optional[str] = None
    enabled_for_deployment: Optional[bool] = None
    enabled_for_disk_encryption: Optional[bool] = None
    enabled_for_template_deployment: Optional[bool] = None
    enable_rbac_authorization: Optional[bool] = None
    enable_soft_delete: Optional[bool] = None
    create_mode: Optional[str] = None
    access_policies: Optional[list[dict[str, str]]] = None
@dataclass
class KeyVaultArgs:
    vault_name: Optional[str] = None
    resource_group_name: Optional[str] = None
    location:  Optional[str] = None
    properties: Optional[VaultPropertiesArgs] = None
@dataclass
class KeyVault:
    name: str
    id: Optional[str] = None
    args: Optional[KeyVaultArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/keyvault/vault/ ###
@dataclass
class SubnetInitArgs:
    name: Optional[str] = None
    resource_group_name: Optional[str] = None
    virtual_network_name: Optional[str] = None
    address_prefix: Optional[str] = None
@dataclass
class Subnet:
    name: str
    id: Optional[str] = None
    args: Optional[SubnetInitArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/network/subnet/ ###
@dataclass
class VirtualNetworkArgs:
    address_space: Optional[list[str]] = None
    location: Optional[str] = None
    resource_group_name: Optional[str] = None
@dataclass
class VirtualNetwork:
    name: str
    id: Optional[str] = None
    args: Optional[VirtualNetworkArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/network/virtualnetwork/ ###
@dataclass
class RoleAssignmentArgs:
    role_assignment_name: Optional[str] = None
    description: Optional[str] = None
    principal_id: Optional[str] = None
    principal_type: Optional[str] = None
    role_definition_id: Optional[str] = None
    scope: Optional[str] = None
@dataclass
class RoleAssignment:
    name: str
    id: Optional[str] = None
    args: Optional[RoleAssignmentArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/authorization/roleassignment/ ###
@dataclass
class ManagedIdentityArgs:
    location: Optional[str] = None
    resource_group_name: Optional[str] = None
    resource_name_: Optional[str] = None
    tags: Optional[dict[str, str]] = None
@dataclass
class ManagedIdentity:
    name: str
    id: Optional[str] = None
    args: Optional[ManagedIdentityArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/managedidentity/ ###
@dataclass
class ResourceGroupArgs:
    resource_group_name: Optional[str] = None
    location: Optional[str] = None
@dataclass
class ResourceGroup:
    name: str
    id: Optional[str] = None
    args: Optional[ResourceGroupArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/resources/resourcegroup/ ###
@dataclass
class AzureNative:
    resource_groups: Optional[list[ResourceGroup]] = None
    managed_identities: Optional[list[ManagedIdentity]] = None
    role_assignments: Optional[list[RoleAssignment]] = None
    virtual_networks: Optional[list[VirtualNetwork]] = None
    subnets: Optional[list[Subnet]] = None
    key_vaults: Optional[list[KeyVault]] = None
    container_registries: Optional[list[containerregistry]] = None
    managed_clusters: Optional[list[ManagedCluster]] = None
### https://www.pulumi.com/registry/packages/azure-native/ ###
@dataclass
class Environment:
    name: str
    tags: dict[str, str]
    location: Optional[str] = None
    azure_native: Optional[AzureNative] = None
@dataclass
class Service:
    name: str
    environments: list[Environment]
@dataclass
class Team:
    name: str
    services: list[Service]
@dataclass
class Config(YAMLWizard):
    teams: list[Team]
### Base Config ###