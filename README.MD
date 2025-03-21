# Pulumi YAML-Based Infrastructure Builder

This project provides a dynamic and extensible Pulumi-based infrastructure-as-code solution for Azure, fully configured using a YAML file. It automatically manages resource naming, supports referencing existing resources, allows dynamic linking between resources, and is easily extensible to additional cloud providers.

## 📂 Project Structure

```
.
├── __main__.py         # Entry point: parses YAML and builds resources
├── azurenative.py      # Azure-specific logic and naming standards
├── config.py           # Dataclasses and dynamic Pulumi resource mapping
├── config.yaml         # User-defined infrastructure config
└── README.md           # Documentation (this file)
```

---

## 🚀 Features

- **YAML-defined infrastructure**: Define all infrastructure clearly in YAML.
- **Dynamic Pulumi resource mapping**: No need to explicitly hardcode resource types.
- **Intelligent resource naming**: Automatically incorporates team, service, environment, and region abbreviations.
- **Azure region abbreviation**: Converts full Azure region names (e.g., `eastus`) into standardized abbreviations (`eus`).
- **Resource referencing**: Use `ref:<resource-name>.<attribute>` syntax to dynamically link resources.
- **New and existing resources**: Seamlessly create new resources or fetch existing ones from Azure.

---

## 📄 Example `config.yaml`

```yaml
team: "DevOps"
service: "test-svc"
environment: "dev"
location: "eastus"
tags:
  owner: "test-user"
  project: "PulumiTest"

azure_resources:
  - name: "rg-01"
    type: "resources.ResourceGroup"
    args:
      location: "eastus"

  - name: "existing-rg"
    type: "resources.ResourceGroup"
    args:
      existing: true
      resource_group_name: "team1-svc1-labs-rg-1d3bf5cca"

  - name: "vnet-01"
    type: "network.VirtualNetwork"
    args:
      resource_group_name: "ref:rg-01.name"
      location: "eastus"
      address_space:
        address_prefixes: ["10.0.0.0/16"]

  - name: "snet-01"
    type: "network.Subnet"
    args:
      resource_group_name: "ref:existing-rg.name"
      virtual_network_name: "ref:vnet-01.name"
      address_prefix: "10.0.0.0/24"
```

---

## 🛠 Getting Started

Initialize Pulumi and deploy your infrastructure:

```bash
pulumi login
pulumi stack init dev
pulumi config set azure-native:location eastus

pulumi up
```

---

## 🔗 Referencing Resources

Use the syntax `ref:<resource-name>.<attribute>` in YAML to dynamically reference outputs from previously defined resources.

Example:

```yaml
resource_group_name: "ref:rg-01.name"
virtual_network_name: "ref:vnet-01.name"
```

This ensures dynamic resolution instead of static values.

---

## 🏷 Resource Naming Convention

Resource names follow the pattern:

```
<team>-<service>-<environment>-<location-abbr>-<resource-name>
```

**Example**:

```
devops-test-svc-dev-eus-vnet-01
```

Azure location abbreviations are automatically handled internally (`eastus` → `eus`).

---

## ⚙️ Dynamic Resource Resolution

The system automatically introspects Pulumi Azure Native packages (`pulumi_azure_native`) to dynamically map resources without explicitly defining resource classes. This simplifies management and allows automatic inclusion of new resources as Pulumi updates.

---

## ✨ Potential Enhancements

- **Reusable YAML templates** for resource patterns.
- **Multi-region and multi-environment** support.
- **Dependency visualization** to clearly show resource relationships.
- **Pre-execution YAML validation** to prevent errors.

---

## 🌐 Multi-Provider Support

This solution is structured to easily extend support to other cloud providers beyond Azure. Each provider can have a dedicated builder module, allowing the project to manage infrastructure across multiple clouds consistently from a single YAML configuration.

### Suggested Directory Structure

```
project-root/
├── azure/
│   └── builder.py
├── aws/
│   └── builder.py
├── gcp/
│   └── builder.py
├── config.yaml
└── main.py
```

### `config.yaml` Example for Providers

```yaml
provider: "azure"  # or "aws", "gcp", etc.
```

### Dynamic Provider Import (`main.py`)

```python
provider = config_data.get("provider", "azure")

if provider == "aws":
    from aws.builder import AWSResourceBuilder as ResourceBuilder
elif provider == "gcp":
    from gcp.builder import GCPResourceBuilder as ResourceBuilder
else:
    from azure.builder import AzureResourceBuilder as ResourceBuilder

builder = ResourceBuilder(config_data)
builder.build()
```

Each provider-specific builder (`builder.py`) should:

- Define its resource mapping and naming strategy.
- Manage region abbreviations and resource conventions.
- Handle resource reference linking.

---

## 👥 Authors & Contributors

This approach follows the **Benitez-Johnson Method**, developed by:

- **Dave Johnson**
- **Christian Benitez**

Special thanks to **Brandon Rutledge** for architecture and implementation contributions.

