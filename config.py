# config.py (Optimized for Faster Pulumi Execution)
import pulumi
import pulumi_azure_native as azure_native
from dataclasses import dataclass
from typing import Dict, Type, List

# Hardcode frequently used Azure resources to avoid dynamic lookup
AZURE_RESOURCE_MAP = {
    "resources.ResourceGroup": azure_native.resources.ResourceGroup,
    "network.VirtualNetwork": azure_native.network.VirtualNetwork,
    "network.Subnet": azure_native.network.Subnet
}

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
