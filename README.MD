# Pulumi YAML-Based Infrastructure Builder for Azure

This project provides a dynamic and extensible Pulumi-based infrastructure-as-code solution for Azure, fully configured using a YAML file. It automatically manages resource naming (with custom name overrides), supports referencing existing resources, allows dynamic linking between resources, and integrates secret resolution via Pulumi configuration.

## 📂 Project Structure

```
.
├── __main__.py         # Entry point: parses YAML and builds resources
├── azurenative.py      # Azure-specific logic, naming standards, and secret resolution
├── config.py           # Dataclasses and dynamic Pulumi resource mapping
├── config.yaml         # User-defined infrastructure configuration
└── README.md           # Documentation (this file)
```

---

## 🚀 Features

- **YAML-defined infrastructure**: Define all infrastructure clearly in YAML.
- **Dynamic Pulumi resource mapping**: Automatically maps YAML definitions to Pulumi resource classes.
- **Intelligent resource naming**: Automatically incorporates team, service, environment, and location abbreviations.
- **Azure region abbreviation**: Converts full Azure region names (e.g., `eastus`) into standardized abbreviations (e.g., `eus`).
- **Resource referencing**: Use `ref:<resource-name>.<attribute>` syntax to dynamically link resources.
- **New and existing resources**: Seamlessly create new resources or fetch existing ones.
- **Custom name overrides**: Override generated names with a `custom_name` field for resources with strict naming rules.
- **Secret resolution**: Use `secret:<key>` in your YAML to securely reference sensitive data from Pulumi configuration.

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

  - name: "sqlserver-01"
    type: "sql.SqlServer"
    args:
      administrator_login: "adminUser"
      administrator_login_password: "secret:sqlServerPassword"
```

---

## 🛠 Getting Started

```bash
pulumi login
pulumi stack init dev
pulumi config set azure-native:location eastus
pulumi config set sqlServerPassword YOUR_SECRET_VALUE --secret
pulumi up
```

---

## 🔗 Referencing Resources

Use the syntax `ref:<resource-name>.<attribute>` to dynamically reference outputs from previously defined resources.

Example:

```yaml
resource_group_name: "ref:rg-01.name"
virtual_network_name: "ref:vnet-01.name"
```

---

## 🏷 Resource Naming Convention

Resource names follow the pattern:

```
<team>-<service>-<environment>-<location-abbr>-<resource-name>
```

**Example:**

```
devops-test-svc-dev-eus-vnet-01
```

---

## ⚙️ Dynamic Resource Resolution

The system automatically introspects Pulumi Azure Native packages (`pulumi_azure_native`) to dynamically map resources without explicit resource class definitions, simplifying management and ensuring new resources are available as Pulumi updates.

---

## ✨ Potential Enhancements

- **Reusable YAML templates** for resource patterns.
- **Multi-region and multi-environment support**.
- **Dependency visualization** for resource relationships.
- **Pre-execution YAML validation**.

---

## 👥 Authors & Contributors

Developed using the **Benitez-Johnson Method** by:
- **Dave Johnson**
- **Christian Benitez**

Special thanks to **Brandon Rutledge** for architecture and implementation contributions.
