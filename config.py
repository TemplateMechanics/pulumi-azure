from dataclass_wizard import YAMLWizard, asdict
from typing import Dict, Any, Sequence ,Optional, List
from dataclasses import dataclass, field

@dataclass
class ManagedClusterSKUArgs:
    name: Optional[str] = None
    tier: Optional[str] = None
@dataclass
class ManagedClusterServicePrincipalProfileArgs:
    client_id: Optional[str] = None
    secret: Optional[str] = None
@dataclass
class NetworkProfileArgs:
    network_plugin: Optional[str] = None
    service_cidr: Optional[str] = None
    dns_service_ip: Optional[str] = None
    docker_bridge_cidr: Optional[str] = None
@dataclass
class IdentityArgs:
    type: Optional[str] = None
    user_assigned_identities: Optional[dict[str, str]] = None
@dataclass
class service_principal_profile:
    client_id: Optional[str] = None
    secret: Optional[str] = None
@dataclass
class AddonProfileArgs:
    enabled: Optional[bool] = None
    config: Optional[dict[str, str]] = None
@dataclass
class ManagedClusterAADProfileArgs:
    managed: Optional[bool] = None
    enable_azure_rbac: Optional[bool] = None
    admin_group_object_ids: Optional[List[str]] = None
    tenant_id: Optional[str] = None
@dataclass
class ManagedClusterAgentPoolProfileArgs:
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
    os_type: Optional[str] = None
    orchestrator_version: Optional[str] = None
    vnet_subnet_id: Optional[str] = None
@dataclass
class ManagedClusterAPIServerAccessProfileArgs:
    authorized_ip_ranges: Optional[List[str]] = None
    enable_private_cluster: Optional[bool] = None
    private_dns_zone: Optional[str] = None
@dataclass
class ManagedClusterArgs:
    agent_pool_profiles: Optional[List[ManagedClusterAgentPoolProfileArgs]] = None
    api_server_access_profile: Optional[ManagedClusterAPIServerAccessProfileArgs] = None
    aad_profile: Optional[ManagedClusterAADProfileArgs] = None
    addon_profiles: Optional[dict[str, AddonProfileArgs]] = None
    disable_local_accounts: Optional[bool] = None
    dns_prefix: Optional[str] = None
    enable_pod_security_policy: Optional[bool] = None
    enable_rbac: Optional[bool] = None
    fqdn_subdomain: Optional[str] = None
    identity: Optional[IdentityArgs] = None
    kubernetes_version: Optional[str] = None
    location: Optional[str] = None
    network_profile: Optional[NetworkProfileArgs] = None
    resource_group_name: Optional[str] = None
    sku: Optional[ManagedClusterSKUArgs] = None
    service_principal_profile: Optional[ManagedClusterServicePrincipalProfileArgs] = None
    tags: Optional[dict[str, str]] = None
    windows_profile: Optional[dict[str, str]] = None
    vnet_subnet_id: Optional[str] = None
@dataclass
class ManagedCluster:
    name: str
    id: Optional[str] = None
    args: Optional[ManagedClusterArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/containerservice/managedcluster/ ###
@dataclass
class ContainerRegistryArgs:
    registry_name: Optional[str] = None
    resource_group_name: Optional[str] = None
    location: Optional[str] = None
    admin_user_enabled: Optional[bool] = None
    sku: Optional[dict[str, str]] = None
    network_rule_set: Optional[dict[str, str]] = None
    policies: Optional[dict[str, str]] = None
    tags: Optional[dict[str, str]] = None
@dataclass
class ContainerRegistry:
    name: str
    id: Optional[str] = None
    args: Optional[ContainerRegistryArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/containerregistry/registry/ ###
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
    access_policies: Optional[List[dict[str, str]]] = None
@dataclass
class KeyVaultArgs:
    vault_name: Optional[str] = None
    resource_group_name: Optional[str] = None
    location:  Optional[str] = None
    properties: Optional[VaultPropertiesArgs] = None
    tags: Optional[dict[str, str]] = None
@dataclass
class KeyVault:
    name: str
    id: Optional[str] = None
    args: Optional[KeyVaultArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/keyvault/vault/ ###
@dataclass
class ManagedServiceIdentityType:
    SYSTEM_ASSIGNED: Optional[str] = None
    USER_ASSIGNED: Optional[str] = None
    SYSTEM_ASSIGNED_USER_ASSIGNED: Optional[str] = None
    NONE: Optional[str] = None
@dataclass
class ManagedServiceIdentityArgs:
    type: Optional[ManagedServiceIdentityType] = None
    user_assigned_identities: Optional[dict[str, str]] = None
class IpSecurityRestrictions:
    action: Optional[str] = None
    description: Optional[str] = None
    headers: Optional[dict[str, Sequence[str]]] = None
    ip_address: Optional[str] = None
    name: Optional[str] = None
    priority: Optional[int] = None
    subnet_mask: Optional[str] = None
    subnet_traffic_tag: Optional[str] = None
    tag: Optional[str] = None
    vnet_subnet_resource_id: Optional[str] = None
    vnet_traffic_tag: Optional[str] = None
@dataclass
class PushSettings:
    is_push_enabled: Optional[bool] = None
    dynamic_tags_json: Optional[str] = None
    kind: Optional[str] = None
    tag_whitelist_json: Optional[str] = None
    tags_requiring_auth: Optional[str] = None
@dataclass
class ManagedPipelineMode:
    INTEGRATED: Optional[str] = None
    CLASSIC: Optional[str] = None
@dataclass
class SiteLoadBalancing:
    WEIGHTED_ROUND_ROBIN: Optional[str] = None
    LEAST_REQUESTS: Optional[str] = None
    LEAST_RESPONSE_TIME: Optional[str] = None
    WEIGHTED_TOTAL_TRAFFIC: Optional[str] = None
    REQUEST_HASH: Optional[str] = None
    PER_SITE_ROUND_ROBIN: Optional[str] = None
@dataclass
class SiteLimits:
    max_disk_size_in_mb: Optional[float] = None
    max_memory_in_mb: Optional[float] = None
    max_percentage_cpu: Optional[float] = None
# @dataclass
# class IpSecurityRestriction:
#     action: Optional[str] = None
#     description: Optional[str] = None
#     headers: Optional[dict[str, Sequence[str]]] = None
#     ip_address: Optional[str] = None
#     name: Optional[str] = None
#     priority: Optional[int] = None
#     subnet_mask: Optional[str] = None
#     subnet_traffic_tag: Optional[str] = None
#     tag: Optional[str] = None
#     vnet_subnet_resource_id: Optional[str] = None
#     vnet_traffic_tag: Optional[str] = None
@dataclass
class HandlerMapping:
    arguments: Optional[str] = None
    extension: Optional[str] = None
    script_processor: Optional[str] = None
# @dataclass
# class RampUpRules:
#     action_host_name: Optional[str] = None
#     change_decision_callback_url: Optional[str] = None
#     change_interval_in_minutes: Optional[int] = None
#     change_step: Optional[float] = None
#     max_reroute_percentage: Optional[float] = None
#     min_reroute_percentage: Optional[float] = None
#     name: Optional[str] = None
#     reroute_percentage: Optional[float] = None
# @dataclass
# class Experiments:
#     ramp_up_rules: Optional[RampUpRules] = None
# @dataclass
# class CorsSettings:
#     allowed_origins: Optional[List[str]] = None
#     support_credentials: Optional[bool] = None
# @dataclass
# class RequestBasedTrigger:
#     count: Optional[int] = None
#     time_interval: Optional[str] = None
# @dataclass
# class AutoHealTriggers:
#     private_bytes_in_kb: Optional[int] = None
#     requests: Optional[RequestBasedTrigger] = None
# @dataclass
# class AutoHealActionType:
#     RECYCLE: Optional[str] = None
#     LOG_EVENT: Optional[str] = None
#     CUSTOM_ACTION: Optional[str] = None
# @dataclass
# class AutoHealActions:
#     action_type: Optional[AutoHealActionType] = None
#     min_process_execution_time: Optional[str] = None
# @dataclass
# class AutoHealRules:
#     actions: Optional[AutoHealActions] = None
#     triggers: Optional[AutoHealTriggers] = None
# @dataclass
# class ApiManagementConfig:
#     id: Optional[str] = None
# @dataclass
# class ApiDefinitionInfo:
#     url: Optional[str] = None
@dataclass
class SiteConfigArgs:
    acr_use_managed_identity_creds: Optional[bool] = None
    acr_user_managed_identity_id: Optional[str] = None
    always_on: Optional[bool] = None
    # api_definition: Optional[ApiDefinitionInfo] = None
    # api_management_config: Optional[ApiManagementConfig] = None
    app_command_line: Optional[str] = None
    app_settings: Optional[List[dict[str, str]]] = None
    # auto_heal_enabled: Optional[bool] = None
    # auto_heal_rules: Optional[AutoHealRules] = None
    # auto_swap_slot_name: Optional[str] = None
    azure_storage_accounts: Optional[List[dict[str, str]]] = None
    connection_strings: Optional[List[dict[str, str]]] = None
    # cors: Optional[CorsSettings] = None
    default_documents: Optional[List[str]] = None
    detailed_error_logging_enabled: Optional[bool] = None
    document_root: Optional[str] = None
    # experiments: Optional[Experiments] = None
    ftps_state: Optional[str] = None
    function_app_scale_limit: Optional[int] = None
    functions_runtime_scale_monitoring_enabled: Optional[bool] = None
    handler_mappings: Optional[HandlerMapping] = None
    health_check_path: Optional[str] = None
    http20_enabled: Optional[bool] = None
    http_logging_enabled: Optional[bool] = None
    # ip_security_restriction: Optional[IpSecurityRestriction] = None
    java_container: Optional[str] = None
    java_container_version: Optional[str] = None
    java_version: Optional[str] = None
    key_vault_reference_identity: Optional[str] = None
    limits: Optional[SiteLimits] = None
    linux_fx_version: Optional[str] = None
    # load_balancing: Optional[SiteLoadBalancing] = None
    # local_mysql_enabled: Optional[bool] = None
    # logs_directory_size_limit: Optional[int] = None
    # managed_pipeline_mode: Optional[ManagedPipelineMode] = None
    # managed_service_identity_id: Optional[str] = None
    # min_tls_version: Optional[str] = None
    # minimum_elastic_instance_count: Optional[int] = None
    # net_framework_version: Optional[str] = None
    # node_version: Optional[str] = None
    # number_of_workers: Optional[int] = None
    # php_version: Optional[str] = None
    # power_shell_version: Optional[str] = None
    # prewarmed_instance_count: Optional[int] = None
    # public_network_access: Optional[str] = None
    # publishing_username: Optional[str] = None
    # push: Optional[PushSettings] = None
    python_version: Optional[str] = None
    # remote_debugging_enabled: Optional[bool] = None
    # remote_debugging_version: Optional[str] = None
    # request_tracing_enabled: Optional[bool] = None
    # request_tracing_expiration_time: Optional[str] = None
    # scm_ip_security_restrictions: Optional[IpSecurityRestriction] = None
    # scm_ip_security_restrictions_use_main: Optional[bool] = None
    # scm_min_tls_version: Optional[str] = None
    # scm_type: Optional[str] = None
    # tracing_options: Optional[str] = None
    # use_32_bit_worker_process: Optional[bool] = None
    # vnet_name: Optional[str] = None
    # vnet_private_ports_count: Optional[int] = None
    # vnet_route_all_enabled: Optional[bool] = None
    # web_sockets_enabled: Optional[bool] = None
    # website_time_zone: Optional[str] = None
    # windows_fx_version: Optional[str] = None
    # x_managed_service_identity_id: Optional[str] = None
@dataclass
class RedundancyMode:
    NONE: Optional[str] = None
    MANUAL: Optional[str] = None
    FAILOVER: Optional[str] = None
    ACTIVE_ACTIVE: Optional[str] = None
    GEO_REDUNDANT: Optional[str] = None
@dataclass
class HostingEnvirontmentProfileArgs:
    id: Optional[str] = None
@dataclass
class CloningInfoArgs:
    source_web_app_id: Optional[str] = None
    app_settings_overrides: Optional[dict[str, str]] = None
    clone_custom_host_names: Optional[bool] = None
    clone_source_control: Optional[bool] = None
    configure_load_balancing: Optional[bool] = None
    correlation_id: Optional[str] = None
    hosting_environment: Optional[str] = None
    overwrite: Optional[bool] = None
    source_web_app_location: Optional[str] = None
    traffic_manager_profile_id: Optional[str] = None
    traffic_manager_profile_name: Optional[str] = None
@dataclass
class ClientCertMode:
    REQUIRED: Optional[str] = None
    OPTIONAL: Optional[str] = None
    OPTIONAL_INTERACTIVE_USER: Optional[str] = None
@dataclass
class WebAppArgs:
    resource_group_name: Optional[str] = None
    client_affinity_enabled: Optional[bool] = None
    client_cert_enabled: Optional[bool] = None
    client_cert_mode: Optional[ClientCertMode] = None
    cloning_info: Optional[CloningInfoArgs] = None
    container_size: Optional[int] = None
    custom_domain_verification_id: Optional[str] = None
    daily_memory_time_quota: Optional[int] = None
    enabled: Optional[bool] = None
    host_names_disabled: Optional[bool] = None
    hosting_environment_profile: Optional[HostingEnvirontmentProfileArgs] = None
    https_only: Optional[bool] = None
    hyper_v: Optional[bool] = None
    identity: Optional[ManagedServiceIdentityArgs] = None
    is_xenon: Optional[bool] = None
    key_vault_reference_identity: Optional[str] = None
    kind: Optional[str] = None
    location: Optional[str] = None
    name: Optional[str] = None
    redundancy_mode: Optional[RedundancyMode] = None
    reserved: Optional[bool] = None
    resource_group_name: Optional[str] = None
    scm_site_also_stopped: Optional[bool] = None
    server_farm_id: Optional[str] = None
    site_config: Optional[SiteConfigArgs] = None
    storage_account_required: Optional[bool] = None
    tags: Optional[dict[str, str]] = None
    virtual_network_subnet_id: Optional[str] = None
@dataclass
class WebApp:
    name: str
    id: Optional[str] = None
    args: Optional[WebAppArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/web/webapp/ ###
@dataclass
class AppServicePlanArgs:
    name: Optional[str] = None
    resource_group_name: Optional[str] = None
    location: Optional[str] = None
    app_service_plan_name: Optional[str] = None
    kind: Optional[str] = None
    reserved: Optional[bool] = None
    sku: Optional[dict[str, str]] = None
    tags: Optional[dict[str, str]] = None
    free_offer_expiration_time: Optional[str] = None
    hyper_v: Optional[bool] = None
    is_spot: Optional[bool] = None
    is_xenon: Optional[bool] = None
    maximum_elastic_worker_count: Optional[int] = None
    per_site_scaling: Optional[bool] = None
    reserved: Optional[bool] = None
    spot_expiration_time: Optional[str] = None
    target_worker_count: Optional[int] = None
    target_worker_size_id: Optional[str] = None
    worker_tier_name: Optional[str] = None
@dataclass
class AppServicePlan:
    name: str
    id: Optional[str] = None
    args: Optional[AppServicePlanArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/web/appserviceplan/ ###
@dataclass
class SkuArgs:
    name: Optional[str] = None
    capacity: Optional[int] = None
    family: Optional[str] = None
    size: Optional[str] = None
    tier: Optional[str] = None
@dataclass
class SqlDatabaseArgs:
    auto_pause_delay: Optional[str] = None
    collation: Optional[str] = None
    create_mode: Optional[str] = None
    database_name: Optional[str] = None
    elastic_pool_id: Optional[str] = None
    high_availability_replica_count: Optional[int] = None
    location: Optional[str] = None
    long_term_retention_backup_resource_id: Optional[str] = None
    maintenance_configuration_id: Optional[str] = None
    max_size_bytes: Optional[float] = None
    min_capacity: Optional[float] = None
    recoverable_database_id: Optional[str] = None
    recovery_services_recovery_point_id: Optional[str] = None
    resource_group_name: Optional[str] = None
    restorable_dropped_database_id: Optional[str] = None
    restore_point_in_time: Optional[str] = None
    server_name: Optional[str] = None
    sku: Optional[SkuArgs] = None
    source_database_deletion_date: Optional[str] = None
    source_database_id: Optional[str] = None
    tags: Optional[dict[str, str]] = None
    zone_redundant: Optional[bool] = None
@dataclass
class SqlDatabase:
    name: str
    id: Optional[str] = None
    args: Optional[SqlDatabaseArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/sql/database/ ###
@dataclass
class ResourceIdentityArgs:
    type: Optional[str] = None
    user_assigned_identities: Optional[dict[str, str]] = None
@dataclass
class ServerExternalAdministrator:
    administrator_type: Optional[str] = None
    azure_ad_only_authentication: Optional[bool] = None
    login: Optional[str] = None
    principal_type: Optional[str] = None
    sid: Optional[str] = None
    tenant_id: Optional[str] = None
@dataclass
class ServerArgs:
    administrator_login: Optional[str] = None
    administrator_login_password: Optional[str] = None
    administrators: Optional[ServerExternalAdministrator] = None
    identity: Optional[ResourceIdentityArgs] = None
    key_id: Optional[str] = None
    location: Optional[str] = None
    minimal_tls_version: Optional[str] = None
    primary_user_assigned_identity_id: Optional[str] = None
    public_network_access: Optional[str] = None
    resource_group_name: Optional[str] = None
    server_name: Optional[str] = None
    tags: Optional[dict[str, str]] = None
    version: Optional[str] = None
@dataclass
class SqlServer:
    name: str
    id: Optional[str] = None
    args: Optional[ServerArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/sql/server/ ###
@dataclass
class SubnetArgs:
    name: Optional[str] = None
    resource_group_name: Optional[str] = None
    virtual_network_name: Optional[str] = None
    address_prefix: Optional[str] = None
    private_endpoint_network_policies: Optional[str] = None
    private_link_service_network_policies: Optional[str] = None
@dataclass
class Subnet:
    name: str
    id: Optional[str] = None
    args: Optional[SubnetArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/network/subnet/ ###
@dataclass
class AddressSpaceArgs:
    address_prefixes: Optional[List[str]] = None
@dataclass
class VirtualNetworkArgs:
    address_space: Optional[AddressSpaceArgs] = None
    location: Optional[str] = None
    resource_group_name: Optional[str] = None
    tags: Optional[dict[str, str]] = None
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
    tags: Optional[dict[str, str]] = None
@dataclass
class ResourceGroup:
    name: str
    id: Optional[str] = None
    args: Optional[ResourceGroupArgs] = None
### https://www.pulumi.com/registry/packages/azure-native/api-docs/resources/resourcegroup/ ###
@dataclass
class AzureNative:
    resource_groups: Optional[List[ResourceGroup]] = None
    managed_identities: Optional[List[ManagedIdentity]] = None
    role_assignments: Optional[List[RoleAssignment]] = None
    virtual_networks: Optional[List[VirtualNetwork]] = None
    subnets: Optional[List[Subnet]] = None
    sql_servers: Optional[List[SqlServer]] = None
    sql_databases: Optional[List[SqlDatabase]] = None
    app_service_plans: Optional[List[AppServicePlan]] = None
    app_services: Optional[List[WebApp]] = None
    key_vaults: Optional[List[KeyVault]] = None
    container_registries: Optional[List[ContainerRegistry]] = None
    managed_clusters: Optional[List[ManagedCluster]] = None
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
    environments: List[Environment]
@dataclass
class Team:
    name: str
    services: List[Service]
@dataclass
class Config(YAMLWizard):
    teams: List[Team]
### Base Config ###