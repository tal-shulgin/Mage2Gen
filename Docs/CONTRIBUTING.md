# Contributing to Mage2Gen

We use **Docker** and **Make** to standardize development. You do not need Python installed locally.

## Setup

1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/mage2gen/mage2gen.git
    cd mage2gen
    ```

2.  **Build Container:**
    ```bash
    make build
    ```

## Development Cycle

1.  **Run Tests:**
    ```bash
    make test
    ```

2.  **Generate Kitchen Sink:**
    This runs a script to generate a massive module covering all features, useful for manual review.
    ```bash
    make samples
    ```
    Output is generated in `./generated/`.

3.  **Linting:**
    The test suite runs PHPCS automatically. Ensure your Python code is clean (we use standard `unittest`).

## Architecture
*   `mage2gen/app.py`: CLI Entry point (Typer).
*   `mage2gen/daemon.py`: The file watcher.
*   `mage2gen/snippets/`: Logic for specific Magento components.
*   `mage2gen/templates/`: Jinja2 templates.