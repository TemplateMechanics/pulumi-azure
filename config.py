# config.py (Dynamically Generates Pulumi Azure Native Resource Mappings and Base Configuration)
import pulumi
import pulumi_azure_native as azure_native
import inspect
from dataclasses import dataclass
from typing import Dict, Type, List, Optional

# Dynamically discover all Azure Native resources available in Pulumi
def get_all_azure_resources() -> Dict[str, Type]:
    """Extracts all Azure resource classes from Pulumi Azure Native dynamically."""
    resource_types = {}
    
    for module_name in dir(azure_native):
        module = getattr(azure_native, module_name, None)
        
        if module and inspect.ismodule(module):  # Ensure it's a valid Pulumi module
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, pulumi.CustomResource) and obj != pulumi.CustomResource:
                    resource_types[f"{module_name}.{name}"] = obj
    
    return resource_types

# Generate the mapping of Azure Native resources to Pulumi classes
AZURE_RESOURCE_MAP = get_all_azure_resources()

# Define base configuration structure
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
