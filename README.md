# Mage2Gen 3.2 🚀

Mage2Gen is a command-line tool for generating Magento 2 modules, creating a standardized boilerplate for Models, Controllers, Blocks, and more.

**Version 3.2** introduces Advanced System Configuration (Dynamic Rows, Image Uploads).

## Installation

```bash
pip install mage2gen
```

## Usage

Create a new module:
```bash
mage2gen module --package Vendor --name Blog --description "My Blog Module"
```

### Advanced Features (New in v3.2)

**System Configuration:**
*   **Image Upload:** `mage2gen system ... --type image`
*   **Color Picker:** `mage2gen system ... --type color`
*   **Dependencies:** `mage2gen system ... --depends "enable_field:1"`
*   **Dynamic Rows:**
    ```bash
    mage2gen system-dynamic --columns "lat:Latitude,lon:Longitude" ...
    ```

### Available Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `module` | Create a new module structure | `mage2gen module` |
| `controller` | Create a Controller Action | `mage2gen controller --action index` |
| `model` | Create a CRUD Model | `mage2gen model --name Post` |
| `block` | Create a Block & Template | `mage2gen block --name Info` |
| `observer` | Create an Event Observer | `mage2gen observer --event catalog_product_save_after` |
| `plugin` | Create a Plugin (Interceptor) | `mage2gen plugin --target-class ...` |
| `console` | Create a CLI Command | `mage2gen console --name import:run` |
| `cronjob` | Create a Cron Job | `mage2gen cronjob --schedule "*/5 * * * *"` |
| `system` | Add System Config Field | `mage2gen system --section general` |
| `system-dynamic`| **(New)** Add Dynamic Row Config | `mage2gen system-dynamic --columns "id:Label"` |
| `payment` | Create Payment Method | `mage2gen payment --name "Offline Credit"` |
| `shipping` | Create Shipping Carrier | `mage2gen shipping --name "Super Express"` |
| `api` | Create REST API Endpoint | `mage2gen api --name StockCheck` |
| `widget` | Create Frontend Widget | `mage2gen widget --name Banner` |
| `admin-crud`| Meta-feature for full Grid/Form | `mage2gen admin-crud --name Post` |

## Development

Run tests:
```bash
python3 -m unittest discover tests
```

### Environment Variables

*   `MAGE2GEN_OUTPUT`: Set the default output directory (useful for Docker).
    ```bash
    export MAGE2GEN_OUTPUT=/var/www/html/app/code
    ```

## License

GPLv3
