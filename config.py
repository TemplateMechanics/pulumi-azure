# config.py (Dynamically Maps Pulumi Azure Native Resource Types)
import pulumi
import pulumi_azure_native as azure_native
import inspect
from dataclasses import dataclass
from typing import Dict, Type, List

# Auto-discover all Azure resources dynamically
def get_all_azure_resources() -> Dict[str, Type]:
    """Extracts all Azure resource classes from Pulumi Azure Native dynamically."""
    resource_types = {}

    for module_name in dir(azure_native):
        module = getattr(azure_native, module_name, None)
        if not inspect.ismodule(module):
            continue  # Skip non-modules
        
        try:
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, pulumi.CustomResource) and obj is not pulumi.CustomResource:
                    resource_types[f"{module_name}.{name}"] = obj
        except TypeError:
            continue  # Skip invalid modules

    return resource_types

# Generate the dynamic resource mapping
AZURE_RESOURCE_MAP = get_all_azure_resources()

@dataclass
class AzureResource:
    name: str
    type: str
    args: Dict

@dataclass
class Config:
    team: str
    service: str
    environment: str
    location: str
    tags: Dict[str, str]
    azure_resources: List[AzureResource]
