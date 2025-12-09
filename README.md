# Mage2Gen 3.2 🚀

Mage2Gen is a command-line tool for generating Magento 2 modules, creating a standardized boilerplate for Models, Controllers, Blocks, and more.

**Version 3.2** introduces Advanced System Configuration (Dynamic Rows, Image Uploads) and a **Dockerized/DDEV** workflow for zero-configuration usage across multiple projects.

## Prerequisites

*   **Docker**
*   **DDEV** (Global configuration)

## Installation (Setup Guide)

This setup allows you to run `ddev m2g` in **any** Magento project folder on your machine without installing Python locally.

### 1. Build the Docker Image
Run this command from the root of this repository:

```bash
docker build -t mage2gen:latest .
```

### 2. Install the Global Command
Create the global DDEV command file at `~/.ddev/commands/host/m2g`.

**Linux/macOS:**
```bash
# Create directory if it doesn't exist
mkdir -p ~/.ddev/commands/host

# Create the command file (Copy/Paste this block)
cat << 'EOF' > ~/.ddev/commands/host/m2g
#!/bin/bash

## Description: Global Mage2Gen Generator
## Usage: m2g [model|module|etc] [flags]
## Example: ddev m2g module --package Vendor --name Shop

# 1. Configuration
IMAGE_NAME="mage2gen:latest"

# 2. Validation
# Check if image exists
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
  echo "❌ Error: Docker image '$IMAGE_NAME' not found."
  echo "Please build it in your source folder: docker build -t mage2gen:latest ."
  exit 1
fi

# 3. Determine Output Directory
# We attempt to find app/code relative to where you are standing
TARGET_DIR="${PWD}"

# Heuristic: If we are in project root, map to app/code
if [ -d "${PWD}/app/code" ]; then
    TARGET_DIR="${PWD}/app/code"
elif [[ "${PWD}" == *"/app/code"* ]]; then
    # We are already inside or below app/code, map current dir
    TARGET_DIR="${PWD}"
else
    # Fallback: create 'generated' folder in current dir to be safe
    mkdir -p generated
    TARGET_DIR="${PWD}/generated"
fi

# 4. Run Container
# --rm: Delete container after running
# -v: Map host User/Group ID so files are owned by you (not root)
# -v: Map the Target Directory to /output
# -e: Tell Mage2Gen to write to /output
docker run --rm \
    -u "$(id -u):$(id -g)" \
    -v "$TARGET_DIR":/output \
    -e MAGE2GEN_OUTPUT=/output \
    $IMAGE_NAME "$@"

# 5. Feedback
echo "✅ Code generated in: $TARGET_DIR"

EOF

# Make it executable
chmod +x ~/.ddev/commands/host/m2g
```

### 3. Install Test Suite Command (Optional)
To run unit tests for Mage2Gen itself:

```bash
cat << 'EOF' > ~/.ddev/commands/host/m2g-test-suite
#!/bin/bash

## Description: Run Mage2Gen Unit Tests
## Usage: m2g-test-suite

# Configuration
IMAGE_NAME="mage2gen:latest"

# Check if image exists
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    echo "❌ Error: Docker image '$IMAGE_NAME' not found."
    echo "Please build it in your source folder: docker build -t mage2gen:latest ."
    exit 1
fi

# Create a temporary directory on the host for test artifacts
TEMP_DIR="$(mktemp -d)"

# Run tests inside the mage2gen container with proper volume mounting
docker run --rm \
    -u "$(id -u):$(id -g)" \
    --entrypoint python3 \
    $IMAGE_NAME -m unittest discover -s tests -v

# Capture exit code
EXIT_CODE=$?

# Cleanup temp directory
rm -rf "$TEMP_DIR"

# Exit with the same code as the tests
exit $EXIT_CODE

# Alternative: If you prefer using run_tests.py:
# docker run --rm \
#     -u "$(id -u):$(id -g)" \
#     --entrypoint python3 \
#     $IMAGE_NAME tests/run_tests.py
EOF
chmod +x ~/.ddev/commands/host/m2g-test-suite
```

---

## Usage

Navigate to **any** Magento 2 project directory and run the commands.

### Initialize a Module
```bash
cd ~/my-magento-project
ddev m2g module --package Vendor --name Blog --description "My Blog Module"
```
*   **Result:** `app/code/Vendor/Blog` is created automatically.

### Generate Components
Once the module structure exists, add components to it:

```bash
# Add a CRUD Model
ddev m2g model --package Vendor --module Blog --name Post --admin-grid

# Add a Controller
ddev m2g controller --package Vendor --module Blog --action index
```

### Advanced Features (v3.2)

**System Configuration:**
*   **Image Upload:** `ddev m2g system ... --type image`
*   **Color Picker:** `ddev m2g system ... --type color`
*   **Dependencies:** `ddev m2g system ... --depends "enable_field:1"`
*   **Dynamic Rows:**
    ```bash
    ddev m2g system-dynamic --columns "lat:Latitude,lon:Longitude" ...
    ```

### Available Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `module` | Create a new module structure | `ddev m2g module` |
| `model` | Create a CRUD Model | `ddev m2g model --name Post` |
| `admin-crud`| **(Meta)** Full Grid + Form + Logic | `ddev m2g admin-crud --name Post` |
| `controller` | Create a Controller Action | `ddev m2g controller --action index` |
| `block` | Create a Block & Template | `ddev m2g block --name Info` |
| `observer` | Create an Event Observer | `ddev m2g observer --event ...` |
| `plugin` | Create a Plugin (Interceptor) | `ddev m2g plugin --target-class ...` |
| `console` | Create a CLI Command | `ddev m2g console --name import:run` |
| `cronjob` | Create a Cron Job | `ddev m2g cronjob --schedule "*/5 * * *"` |
| `system` | Add System Config Field | `ddev m2g system --section general` |
| `system-dynamic`| **(New)** Add Dynamic Row Config | `ddev m2g system-dynamic ...` |
| `api` | Create REST API Endpoint | `ddev m2g api --name StockCheck` |
| `graphql` | Create GraphQL Endpoint | `ddev m2g graphql --name getPost` |
| `message-queue`| Async Queue Topology | `ddev m2g message-queue ...` |

## Development

To contribute to Mage2Gen, modify the source code and rebuild the image:

```bash
docker build -t mage2gen:latest .
```

### Running Tests
Run the unit tests inside the Docker container using the helper command:

```bash
ddev m2g-test-suite
```

## License

GPLv3


### Wishlist
- admin form text fields rendered as pagebuilder but not always we want this, some times we prefer simple wisiwig
- admin complex forms with models for item selection
- admin store config dynamic row dnd
- customer sections to bypass fpc

