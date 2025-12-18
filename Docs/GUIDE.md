# Mage2Gen User Guide

## Core Concepts

Mage2Gen runs as a background process (Daemon) that watches a configuration file (`m2g.yaml`). When you change this file, Mage2Gen reads it and generates the corresponding Magento 2 PHP/XML code.

### Workflow Options

#### 1. The "Config as Code" Flow (Recommended)
Define your entire module structure in `m2g.yaml`.
*   **Pros:** Reproducible, version-controlled, easy to bulk-edit.
*   **How:** See [YAML Reference](REFERENCE.md).

#### 2. The CLI Flow
Use terminal commands to generate code on the fly.
*   **Pros:** Fast for single files (e.g., "I just need a quick Observer").
*   **How:**
    ```bash
    # If using DDEV wrapper
    ddev m2g observer --event checkout_submit_all_after --name MyObserver
    ```

## DDEV Integration

The recommended way to use Mage2Gen is adding it to your DDEV project.

**1. Installation**
Download the service definition:
```bash
curl -o .ddev/docker-compose.mage2gen.yaml https://raw.githubusercontent.com/mage2gen/mage2gen/v6.0/.ddev/docker-compose.mage2gen.yaml
ddev restart
```

**2. Commands**
You can run Mage2Gen commands from your host:
```bash
ddev m2g --help
ddev m2g model --name Product --fields title:text
```

**3. Troubleshooting**
View the daemon logs to see generation status or errors:
```bash
ddev m2g-logs
```

