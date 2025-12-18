# Mage2Gen YAML Reference

This document details the schema for `m2g.yaml`.

## Structure
```yaml
version: 1.0
modules:
  Vendor_Module:
    description: "String"
    components:
      - type: "component_type"
        # component specific fields...
```

## Component Types

### Model (CRUD)
Generates Model, ResourceModel, Collection, Repository, Interfaces, and optional Admin UI.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `type` | string | `model` | **Required** |
| `name` | string | - | Class name (e.g. `BlogPost`) |
| `fields` | string | - | Format: `name:type:required,name2:type` |
| `admin_grid` | bool | `false` | Generate Admin Listing (Grid) |
| `admin_form` | bool | `false` | Generate Admin Edit Form |
| `api` | bool | `false` | Generate Web API (REST) endpoints |
| `graphql` | bool | `false` | Generate GraphQL Schema & Resolvers |

**Example:**
```yaml
- type: model
  name: Post
  fields: "title:text:required,views:int,content:textarea"
  admin_grid: true
```

### Controller
Generates a Controller Action and `routes.xml`.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `type` | string | `controller` | **Required** |
| `frontname` | string | module_name | URL prefix |
| `section` | string | `index` | Controller subfolder |
| `action` | string | `index` | Action class name |
| `admin` | bool | `false` | If true, creates in `Adminhtml` |

**Example:**
```yaml
- type: controller
  frontname: "blog"
  section: "post"
  action: "view"
```

### Observer
Hooks into a Magento Event.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `type` | string | `observer` | **Required** |
| `event` | string | - | Event name (e.g. `sales_order_place_after`) |
| `scope` | string | `all` | `all`, `frontend`, `adminhtml`, `graphql`, `webapi` |

### Plugin
Interceptors for public methods.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `type` | string | `plugin` | **Required** |
| `target_class` | string | - | Class to intercept |
| `method` | string | - | Method name |
| `plugin_type` | string | `after` | `before`, `after`, `around` |
| `sort_order` | int | `10` | Execution order |

*(Note: Use `plugin_type` in YAML to avoid conflict with the component `type`)*


