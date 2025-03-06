# __main__.py (Dynamically Deploys Azure Resources from config.py and config.yaml)
import pulumi
import pulumi_azure_native as azure_native
from config import Config, AzureResource, AZURE_RESOURCE_MAP
import yaml

# Load configuration from config.yaml
with open("config.yaml", "r") as file:
    config_data = yaml.safe_load(file)

# Parse config.yaml into Config dataclass
stack_config = Config(
    team=config_data["team"],
    service=config_data["service"],
    environment=config_data["environment"],
    location=config_data["location"],
    tags=config_data["tags"],
    azure_resources=[
        AzureResource(
            name=res["name"],
            type=res["type"],
            args=res["args"]
        ) for res in config_data["azure_resources"]
    ]
)

# Create a dictionary to store deployed resources for dependency resolution
resource_cache = {}

# Deploy resources dynamically
for resource_data in stack_config.azure_resources:
    resource_type = resource_data.type
    
    if resource_type in AZURE_RESOURCE_MAP:
        ResourceClass = AZURE_RESOURCE_MAP[resource_type]
        
        # Resolve dependencies by replacing string references with actual Pulumi objects
        args = resource_data.args.copy()
        for key, value in args.items():
            if isinstance(value, str) and value in resource_cache:
                args[key] = resource_cache[value].name  # Resolve Pulumi reference

        # Create the resource
        resource = ResourceClass(resource_data.name, **args)
        resource_cache[resource_data.name] = resource

        # Export resource ID
        pulumi.export(resource_data.name, resource.id)
        pulumi.log.info(f"Deployed: {resource_data.name} ({resource_type})")
    else:
        pulumi.log.error(f"Resource type {resource_type} not found in Pulumi Azure Native package.")