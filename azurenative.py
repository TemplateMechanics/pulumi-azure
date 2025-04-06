import pulumi
import pulumi_azure_native as azure_native
import inspect
import re
from typing import Any, Dict

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

def resolve_value(value: Any, resources: Dict[str, Any]) -> Any:
    if isinstance(value, dict):
        return {k: resolve_value(v, resources) for k, v in value.items()}
    elif isinstance(value, list):
        return [resolve_value(item, resources) for item in value]
    elif isinstance(value, str):
        if value.startswith("secret:"):
            # Fetch secret from Pulumi config
            secret_key = value[len("secret:"):]
            config = pulumi.Config()
            return config.require_secret(secret_key)
        elif value.startswith("ref:"):
            ref_text = value[4:]
            if "." in ref_text:
                ref_res, ref_attr = ref_text.split(".", 1)
            else:
                ref_res, ref_attr = ref_text, "id"
            if ref_res not in resources:
                raise ValueError(f"Referenced resource '{ref_res}' not found.")
            resource_obj = resources[ref_res]
            attr_val = getattr(resource_obj, ref_attr, None)
            if attr_val is None:
                raise ValueError(f"Attribute '{ref_attr}' not found on resource '{ref_res}'")
            return attr_val
        else:
            return value
    else:
        return value

def get_lookup_params(required_params: set, resolved_args: dict) -> dict:
    lookup_params = {}
    for param in required_params:
        snake_key = to_snake_case(param)
        if snake_key in resolved_args:
            lookup_params[param] = resolved_args[snake_key]
        elif param in resolved_args:
            lookup_params[param] = resolved_args[param]
    return lookup_params

class AzureResourceBuilder:
    def __init__(self, config_data: dict):
        self.config = config_data
        self.resources: Dict[str, Any] = {}

    def get_abbreviation(self, location: str) -> str:
        return AZURE_LOCATION_ABBREVIATIONS.get(location.lower(), location[:3].lower())

    def generate_resource_name(self, base_name: str) -> str:
        team = self.config.get("team", "team").strip().lower()
        service = self.config.get("service", "svc").strip().lower()
        env = self.config.get("environment", "dev").strip().lower()
        loc_abbr = self.get_abbreviation(self.config.get("location", "eastus"))
        return f"{team}-{service}-{env}-{loc_abbr}-{base_name}".lower()

    def resolve_args(self, args: dict) -> dict:
        return {key: resolve_value(value, self.resources) for key, value in args.items()}

    def _apply_common_parameters(self, resolved_args: dict, init_sig: inspect.Signature) -> dict:
        if "tags" in init_sig.parameters:
            resource_tags = self.config.get("tags")
            if resource_tags:
                resolved_args.setdefault("tags", resource_tags)
        else:
            resolved_args.pop("tags", None)
        if "location" in init_sig.parameters:
            if "location" not in resolved_args:
                resolved_args["location"] = self.config.get("location", "eastus")
        else:
            resolved_args.pop("location", None)
        return resolved_args

    def build(self):
        azure_resources = self.config.get("azure_resources", [])
        for resource_cfg in azure_resources:
            name = resource_cfg["name"]
            resource_type = resource_cfg["type"]
            args = resource_cfg.get("args", {}).copy()
            custom_name = resource_cfg.get("custom_name", None)
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
                pulumi.log.warn(f"Resource class '{class_name}' not found in module '{module_name}'. Skipping '{name}'.")
                continue
            init_sig = inspect.signature(ResourceClass.__init__)
            if is_existing:
                get_func_name = f"get_{to_snake_case(class_name)}"
                try:
                    get_func = getattr(module, get_func_name)
                    sig = inspect.signature(get_func)
                    get_required = {k for k, param in sig.parameters.items() if k not in {"opts"} and param.default == param.empty}
                    get_params = get_lookup_params(get_required, resolved_args)
                    missing = get_required - set(get_params.keys())
                    if missing:
                        pulumi.log.warn(f"Missing required params {missing} for existing resource '{name}'. Skipping the lookup attempt.")
                    else:
                        existing_resource = get_func(**get_params)
                        self.resources[name] = existing_resource
                        pulumi.log.info(f"Fetched existing resource '{name}' via '{get_func_name}' with {get_params}")
                        continue
                except AttributeError:
                    pulumi.log.warn(f"Function '{get_func_name}' not found for '{resource_type}'. Proceeding to create new resource '{name}'.")
                except Exception as e:
                    pulumi.log.warn(f"Failed to retrieve existing resource '{name}': {e}. Proceeding with creation.")
                if "location" in init_sig.parameters and "location" not in resolved_args:
                    resolved_args["location"] = self.config.get("location", "eastus")
                else:
                    resolved_args.pop("location", None)
            resolved_args = self._apply_common_parameters(resolved_args, init_sig)
            pulumi_name = custom_name if custom_name else self.generate_resource_name(name)
            pulumi.log.info(f"DEBUG for '{name}': final resolved_args => {resolved_args}")
            resource_instance = ResourceClass(pulumi_name, **resolved_args)
            self.resources[name] = resource_instance
            pulumi.log.info(f"Created resource: {pulumi_name} ({resource_type})")
