# azurenative.py (Handles Dynamic Azure Resource Creation in Pulumi)
import pulumi
import pulumi_azure_native as azure_native
from config import AZURE_RESOURCE_MAP, Config, AzureResource
from typing import Optional

class BuildContext:
    """Stores metadata and a cache of created resources."""
    def __init__(self, team: str, service: str, environment: str, location: str, tags: dict):
        self.team = team
        self.service = service
        self.environment = environment
        self.location = location
        self.tags = tags
        self.resource_cache = {}

    def add_resource(self, name: str, resource: pulumi.CustomResource):
        self.resource_cache[name] = resource

    def get_resource(self, name: str) -> Optional[pulumi.CustomResource]:
        return self.resource_cache.get(name)

class AzureResourceBuilder:
    """Dynamically creates Azure resources using Pulumi."""
    def __init__(self, context: BuildContext):
        self.context = context

    def build(self, config: Config):
        for resource_data in config.azure_resources:
            resource_type = resource_data.type
            
            if resource_type in AZURE_RESOURCE_MAP:
                ResourceClass = AZURE_RESOURCE_MAP[resource_type]
                
                args = resource_data.args.copy()
                
                # Resolve dependencies by replacing string references with actual Pulumi objects
                for key, value in args.items():
                    if isinstance(value, str) and value in self.context.resource_cache:
                        args[key] = self.context.get_resource(value).name  # Resolve Pulumi reference

                # Set location and tags if not explicitly defined
                args.setdefault("location", self.context.location)
                args.setdefault("tags", self.context.tags)

                # Create the resource
                resource = ResourceClass(resource_data.name, **args)
                self.context.add_resource(resource_data.name, resource)
                pulumi.export(resource_data.name, resource.id)
                pulumi.log.info(f"Created: {resource_data.name} ({resource_type})")
            else:
                pulumi.log.error(f"Resource type {resource_type} not found in Pulumi Azure Native package.")
