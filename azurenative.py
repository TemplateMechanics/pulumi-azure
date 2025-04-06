import pulumi
import pulumi_azure_native as azure_native
import inspect
import re
from typing import Any

AZURE_LOCATION_ABBREVIATIONS = {
    "eastus": "eus",
    "eastus2": "eus2",
    "westus": "wus",
    "westus2": "wus2",
    "westus3": "wus3",
    "centralus": "cus",
    "northcentralus": "ncus",
    "southcentralus": "scus",
    "canadacentral": "ccc",
    "canadaeast": "cce",
    "brazilsouth": "brs",
    "brazilsoutheast": "brse",
    "northeurope": "ne",
    "westeurope": "we",
    "uksouth": "uks",
    "ukwest": "ukw",
    "francecentral": "frc",
    "francesouth": "frs",
    "germanywestcentral": "gwc",
    "germanynorth": "gn",
    "norwayeast": "nwe",
    "norwaywest": "nww",
    "swedencentral": "swc",
    "switzerlandnorth": "swn",
    "switzerlandwest": "sww",
    "uaenorth": "uaen",
    "uaecentral": "uaec",
    "australiaeast": "aue",
    "australiasoutheast": "ause",
    "australiacentral": "auc",
    "australiacentral2": "auc2",
    "japaneast": "jpe",
    "japanwest": "jpw",
    "koreacentral": "kc",
    "koreasouth": "ks",
    "southeastasia": "sea",
    "eastasia": "ea",
    "southindia": "si",
    "centralindia": "ci",
    "westindia": "wi",
    "southafricanorth": "san",
    "southafricawest": "saw",
    "qatarcentral": "qc",
    "polandcentral": "plc",
    "israelcentral": "ilc",
    "israelnorth": "iln",
}

def to_snake_case(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

class AzureResourceBuilder:
    def __init__(self, config_data: dict):
        self.config = config_data
        self.resources = {}

    def get_abbreviation(self, location: str) -> str:
        # If the location is recognized, use abbreviation; else fallback to first 3 letters
        return AZURE_LOCATION_ABBREVIATIONS.get(location.lower(), location[:3].lower())

    def generate_resource_name(self, base_name: str) -> str:
        team = self.config.get("team", "team").lower()
        service = self.config.get("service", "svc").lower()
        env = self.config.get("environment", "dev").lower()
        loc_abbr = self.get_abbreviation(self.config.get("location", "eastus"))
        return f"{team}-{service}-{env}-{loc_abbr}-{base_name}".lower()

    def resolve_args(self, args: dict) -> dict:
        resolved_args = {}
        for key, value in args.items():
            if isinstance(value, dict):
                resolved_args[key] = self.resolve_args(value)
            elif isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, dict):
                        new_list.append(self.resolve_args(item))
                    elif isinstance(item, str) and item.startswith("ref:"):
                        item_res = self.resolve_args({"temp": item})["temp"]
                        new_list.append(item_res)
                    else:
                        new_list.append(item)
                resolved_args[key] = new_list
            elif isinstance(value, str) and value.startswith("ref:"):
                # handle "ref:resourceName.attribute"
                ref_text = value[4:]
                if "." in ref_text:
                    ref_res, ref_attr = ref_text.split(".", 1)
                else:
                    ref_res, ref_attr = (ref_text, "id")

                if ref_res not in self.resources:
                    raise ValueError(f"Referenced resource '{ref_res}' not found.")

                resource_obj = self.resources[ref_res]
                attr_val = getattr(resource_obj, ref_attr, None)
                if attr_val is None:
                    raise ValueError(f"Attribute '{ref_attr}' not found on resource '{ref_res}'")
                resolved_args[key] = attr_val
            else:
                resolved_args[key] = value
        return resolved_args

    def build(self):
        azure_resources = self.config.get("azure_resources", [])

        for resource_cfg in azure_resources:
            name = resource_cfg["name"]
            resource_type = resource_cfg["type"]
            args = resource_cfg.get("args", {}).copy()

            is_existing = args.pop("existing", False)
            resolved_args = self.resolve_args(args)

            module_name, class_name = resource_type.rsplit(".", 1)
            module = getattr(azure_native, module_name, None)
            if not module:
                pulumi.log.warn(f"Azure module '{module_name}' not found. Skipping '{name}'.")
                continue

            try:
                ResourceClass = getattr(module, class_name)
            except AttributeError:
                pulumi.log.warn(
                    f"Resource class '{class_name}' not found in module '{module_name}'. Skipping '{name}'."
                )
                continue

            init_sig = inspect.signature(ResourceClass.__init__)

            # If the resource is marked as existing, attempt a dynamic get_* function
            if is_existing:
                get_func_name = f"get_{to_snake_case(class_name)}"
                try:
                    get_func = getattr(module, get_func_name)
                    sig = inspect.signature(get_func)
                    valid_params = set(sig.parameters.keys())
                    required_params = valid_params - {"opts"}

                    # Filter resolved_args for what the get_* function actually needs
                    get_params = {
                        k: v for k, v in resolved_args.items() if k in required_params
                    }

                    missing = required_params - set(get_params.keys())
                    if missing:
                        pulumi.log.warn(
                            f"Missing required params {missing} for existing resource '{name}'. "
                            f"Skipping the lookup attempt."
                        )
                    else:
                        existing_resource = get_func(**get_params)
                        self.resources[name] = existing_resource
                        pulumi.log.info(
                            f"Fetched existing resource '{name}' via '{get_func_name}' with {get_params}"
                        )
                        continue
                except AttributeError:
                    pulumi.log.warn(
                        f"Function '{get_func_name}' not found for '{resource_type}'. "
                        f"Proceeding to create new resource '{name}'."
                    )
                except Exception as e:
                    pulumi.log.warn(
                        f"Failed to retrieve existing resource '{name}': {e}. Proceeding with creation."
                    )

                # << KEY FIX >>
                # If the lookup fails, we are about to create a new resource. 
                # So if location is in the constructor signature, ensure we have it:
                if "location" in init_sig.parameters and "location" not in resolved_args:
                    # Use top-level config or a fallback default
                    resolved_args["location"] = self.config.get("location", "eastus")
                else:
                    resolved_args.pop("location", None)

            # Check if resource supports 'tags'
            if "tags" in init_sig.parameters:
                resource_tags = self.config.get("tags")
                if resource_tags:
                    resolved_args.setdefault("tags", resource_tags)
            else:
                resolved_args.pop("tags", None)

            # If resource constructor expects location, ensure it's present or fallback
            if "location" in init_sig.parameters:
                if "location" not in resolved_args:
                    resolved_args["location"] = self.config.get("location", "eastus")
            else:
                resolved_args.pop("location", None)

            pulumi_name = self.generate_resource_name(name)

            # Debug log to confirm final arguments used:
            pulumi.log.info(f"DEBUG for '{name}': final resolved_args => {resolved_args}")

            resource_instance = ResourceClass(pulumi_name, **resolved_args)
            self.resources[name] = resource_instance
            pulumi.log.info(f"Created resource: {pulumi_name} ({resource_type})")
