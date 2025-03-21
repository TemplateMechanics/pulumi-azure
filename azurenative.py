import pulumi
import pulumi_azure_native as azure_native
import importlib
import hashlib
import inspect
import re
from typing import Any

AZURE_LOCATION_ABBREVIATIONS = {
    "eastus": "eus",
    "eastus2": "eus2",
    "westus": "wus",
    "westus2": "wus2",
    "centralus": "cus",
    "northcentralus": "ncus",
    "southcentralus": "scus",
    "canadacentral": "ccc",
    "canadaeast": "cce",
    "brazilsouth": "brs",
    "northeurope": "ne",
    "westeurope": "we",
    "uksouth": "uks",
    "ukwest": "ukw",
    "francecentral": "frc",
    "francesouth": "frs",
    "germanywestcentral": "gwc",
    "norwayeast": "nwe",
    "swedencentral": "swc",
    "switzerlandnorth": "swn",
    "uaenorth": "uaen",
    "australiaeast": "aue",
    "australiasoutheast": "ause",
    "japaneast": "jpe",
    "japanwest": "jpw",
    "koreacentral": "kc",
    "koreasouth": "ks",
    "southeastasia": "sea",
    "southindia": "si",
    "centralindia": "ci",
    "westindia": "wi",
    "eastasia": "ea",
    "australiacentral": "auc",
    "australiacentral2": "auc2",
    "brazilse": "brse",
    "southafricanorth": "san",
    "qatarcentral": "qc"
}

def to_snake_case(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

class AzureResourceBuilder:
    def __init__(self, config_data: dict):
        self.config = config_data
        self.resources = {}

    def get_abbreviation(self, location):
        return AZURE_LOCATION_ABBREVIATIONS.get(location.lower(), location.replace(" ", "")[:3].lower())

    def generate_resource_name(self, base_name):
        team = self.config.get("team", "team")
        service = self.config.get("service", "svc")
        env = self.config.get("environment", "dev")
        loc = self.get_abbreviation(self.config.get("location", "eastus"))
        return f"{team}-{service}-{env}-{loc}-{base_name}".lower()

    def get_resource_reference(self, ref_name: str):
        ref_resource = self.resources.get(ref_name)
        if ref_resource is None:
            raise ValueError(f"Referenced resource '{ref_name}' not found.")

        if hasattr(ref_resource, 'name'):
            return ref_resource.name
        elif hasattr(ref_resource, 'id'):
            return ref_resource.id
        return ref_resource

    def resolve_args(self, args: dict):
        resolved_args = {}
        for key, value in args.items():
            if isinstance(value, dict):
                resolved_args[key] = self.resolve_args(value)
            elif isinstance(value, list):
                resolved_args[key] = [self.resolve_args(v) if isinstance(v, dict) else v for v in value]
            elif isinstance(value, str) and value in self.resources:
                resolved_args[key] = self.get_resource_reference(value)
            else:
                resolved_args[key] = value
        return resolved_args

    def build(self):
        azure_resources = self.config.get("azure_resources", [])

        for resource in azure_resources:
            name = resource["name"]
            resource_type = resource["type"]
            args = resource.get("args", {})
            is_existing = args.pop("existing", False)

            module_name, class_name = resource_type.rsplit(".", 1)
            module = getattr(azure_native, module_name)
            ResourceClass = getattr(module, class_name)

            resolved_args = self.resolve_args(args)

            if is_existing:
                get_func_name = f"get_{to_snake_case(class_name)}"
                try:
                    get_func = getattr(module, get_func_name)
                    if "resource_group_name" in resolved_args:
                        existing = get_func(resource_group_name=resolved_args["resource_group_name"])
                        self.resources[name] = existing
                        pulumi.log.info(f"Fetched existing {resource_type}: {resolved_args['resource_group_name']}")
                        continue
                    else:
                        pulumi.log.warn(f"Skipping lookup: 'resource_group_name' is required but missing for '{resource_type}'")
                except AttributeError:
                    pulumi.log.warn(f"Function '{get_func_name}' not found in module '{module_name}'.")
                except Exception as e:
                    pulumi.log.warn(f"Failed to retrieve existing resource: {name}. Proceeding with creation. Error: {e}")

            unsupported_tag_types = {
                "network.Subnet",
            }
            if resource_type not in unsupported_tag_types:
                tags = self.config.get("tags")
                if tags:
                    resolved_args.setdefault("tags", tags)
            else:
                resolved_args.pop("tags", None)

            pulumi_name = self.generate_resource_name(name)
            resource_instance = ResourceClass(pulumi_name, **resolved_args)
            self.resources[name] = resource_instance
            pulumi.log.info(f"Created resource: {pulumi_name} ({resource_type})")