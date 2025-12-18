# Mage2Gen DX (v6.0) 🚀

**The Intelligent Magento 2 Module Generator.**

Mage2Gen is a developer tool that scaffolds Magento 2 modules, models, plugins, and configuration files instantly.

**v6.0 "DX Edition"** introduces a persistent Daemon architecture, allowing for:
*   **Instant Generation:** <50ms response time.
*   **Configuration as Code:** Define modules in `m2g.yaml`.
*   **Hot Reload:** Code is regenerated instantly when you save.

---

## ⚡ Quick Start (DDEV)

1.  **Install Service:**
    ```bash
    curl -o .ddev/docker-compose.mage2gen.yaml https://raw.githubusercontent.com/mage2gen/mage2gen/v6.0/.ddev/docker-compose.mage2gen.yaml
    ddev restart
    ```

2.  **Create Config:**
    Create `m2g.yaml` in your project root:
    ```yaml
    version: 1.0
    modules:
      Vendor_Blog:
        description: "My Blog"
        components:
          - type: model
            name: Post
            fields: "title:text,is_active:boolean"
            admin_grid: true
    ```

3.  **Generate:**
    Just save the file. The code appears in `app/code/Vendor/Blog`.

---

## 📚 Documentation

*   **[User Guide](Docs/GUIDE.md):** Detailed usage instructions, CLI commands, and DDEV integration.
*   **[YAML Reference](Docs/REFERENCE.md):** Complete specification for `m2g.yaml` components.
*   **[Contributing](Docs/CONTRIBUTING.md):** How to build and test Mage2Gen itself.

## License
GPLv3