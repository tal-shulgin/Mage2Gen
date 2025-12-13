# Mage2Gen DX (v6.0) 🚀

**The Intelligent Magento 2 Module Generator.**

Mage2Gen is a developer tool that scaffolds Magento 2 modules, models, plugins, and configuration files. 

**v6.0 "DX Edition"** introduces a persistent Daemon architecture, allowing for:
*   **Instant Generation:** <50ms response time (no Docker cold starts).
*   **Configuration as Code:** Define modules in `m2g.yaml` and commit them to Git.
*   **Hot Reload:** Code is regenerated instantly when you save your YAML file.

---

## ⚡ Quick Start: DDEV Integration

The recommended way to use Mage2Gen is as a "sidecar" service in your existing DDEV project.

### 1. Install the Service
Download the compose configuration into your project's `.ddev` folder:

```bash
# Run this inside your Magento project root
curl -o .ddev/docker-compose.mage2gen.yaml https://raw.githubusercontent.com/mage2gen/mage2gen/v6.0/.ddev/docker-compose.mage2gen.yaml
```

### 2. Start DDEV
```bash
ddev restart
```
The Mage2Gen daemon will start silently in the background, mounting your project root.

### 3. Generate Code
Create a file named `m2g.yaml` in your project root. Paste the following:

```yaml
version: 1.0
modules:
  MyVendor_Blog:
    description: "My Blog Module"
    components:
      - type: model
        name: Post
        fields:
          - name: title
            type: text
            required: true
          - name: is_active
            type: boolean
        admin_grid: true
        admin_form: true
```

**Save the file.** 
Check `app/code/MyVendor/Blog`. The code is already there.

---

## 📖 Configuration Reference (`m2g.yaml`)

Mage2Gen watches `m2g.yaml` for changes. You can define multiple modules and components.

### Supported Components

| Component | YAML Type | Description |
| :--- | :--- | :--- |
| **Model** | `model` | CRUD Model, Resource, Collection, Repository, API |
| **Controller** | `controller` | Frontend or Adminhtml Controller & Route |
| **Block** | `block` | Block class + PHTML + Layout XML |
| **Observer** | `observer` | Event Observer |
| **Plugin** | `plugin` | Interceptor (Before/After/Around) |
| **System Config** | `system` | `system.xml` fields (Text, Select, Image, etc.) |
| **Cron** | `cron` | Cron job definition |
| **Console** | `console` | CLI Command |
| **API** | `api` | Custom REST API Endpoint |
| **GraphQL** | `graphql` | Custom GraphQL Query/Mutation |

### Full Example
See [m2g_reference.yaml](m2g_reference.yaml) for a complete "Kitchen Sink" example containing every supported option.

---

## 🛠️ Manual Usage (Docker)

If you aren't using DDEV, you can run the daemon manually using Docker.

```bash
docker run --rm -it \
    -v $(pwd):/var/www/html \
    -u "$(id -u):$(id -g)" \
    -e MAGE2GEN_OUTPUT=/var/www/html/app/code \
    mage2gen:latest \
    python3 -m mage2gen.daemon
```

*   **-v**: Mounts your current directory (Project Root) to the container.
*   **-u**: Runs as your user ID to prevent permission issues.
*   **MAGE2GEN_OUTPUT**: Tells the generator where to write the PHP files.

---

## 👨‍💻 Contributing to Mage2Gen

Want to fix a bug or add a new Snippet?

1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/mage2gen/mage2gen.git ~/code/mage2gen
    ```

2.  **Mount Source in Your Project:**
    Edit your project's `.ddev/docker-compose.mage2gen.yaml` to override the code volume:
    ```yaml
    volumes:
      - ../:/var/www/html
      - ~/code/mage2gen:/opt/mage2gen
    ```

3.  **Develop:**
    Edit Python files in `~/code/mage2gen`. Restart `ddev` to apply changes to the daemon.

4.  **Run Tests:**
    ```bash
    # From inside the Mage2Gen repo folder
    make test
    ```

## License
GPLv3
```

---

### 4. ⚙️ Daemon Safety (`daemon.py`)

I added a check to ensure `MAGE2GEN_OUTPUT` defaults safely if not provided, preventing generation into the root of the container if misconfigured.

**File:** `mage2gen/daemon.py` (Snippet)

```python
def start_daemon():
    # Default to current directory if env var not set, but warn user
    output_dir = os.environ.get("MAGE2GEN_OUTPUT")
    
    if not output_dir:
        logger.warning("⚠️  MAGE2GEN_OUTPUT not set. Defaulting to './generated' to avoid clutter.")
        output_dir = os.path.join(os.getcwd(), "generated")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    logger.info(f"🚀 Mage2Gen Daemon starting...")
    logger.info(f"📂 Writing code to: {output_dir}")
    # ...
```
