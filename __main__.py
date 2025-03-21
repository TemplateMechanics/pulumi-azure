import yaml
import pulumi
import pulumi_azure_native as azure_native
from azurenative import AzureResourceBuilder

# Load YAML configuration
with open("config.yaml", "r") as file:
    config_data = yaml.safe_load(file)

# Ensure all required config values exist
required_keys = ["team", "service", "environment", "location"]
for key in required_keys:
    if key not in config_data:
        raise ValueError(f"Missing required configuration key: {key}")

# Initialize builder with config
try:
    builder = AzureResourceBuilder(config_data)
except Exception as e:
    pulumi.log.error(f"Failed to initialize AzureResourceBuilder: {e}")
    raise

# Build resources
try:
    builder.build()
except Exception as e:
    pulumi.log.error(f"Failed during resource build: {e}")
    raise

# Export created resources
for name, resource in builder.resources.items():
    try:
        pulumi.export(name, resource.id)
    except Exception as e:
        pulumi.log.warn(f"Failed to export resource '{name}': {e}")
