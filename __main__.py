# main.py
import yaml
import pulumi
from azurenative import AzureResourceBuilder
from typing import Any, Dict

def load_config(file_path: str) -> Dict[str, Any]:
    """Load and validate YAML configuration from the given file path."""
    with open(file_path, "r") as file:
        config_data = yaml.safe_load(file)
    
    # Ensure required keys exist
    required_keys = ["team", "service", "environment", "location"]
    for key in required_keys:
        if key not in config_data:
            raise ValueError(f"Missing required configuration key: {key}")
    
    return config_data

def main():
    # Load YAML configuration
    config_data = load_config("config.yaml")

    # Optionally, you can convert config_data into the Config dataclass defined in config.py
    # For now, we pass the dictionary directly to the builder.
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

if __name__ == "__main__":
    main()
