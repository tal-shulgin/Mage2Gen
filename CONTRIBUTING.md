# Contributing to Mage2Gen 3.0

Welcome to Mage2Gen 3.0! We have modernized the architecture to use **Typer** (CLI) and **Jinja2** (Templates).

## Architecture Overview

*   **`mage2gen/app.py`**: The CLI entry point. Commands are defined here using `typer`.
*   **`mage2gen/core/template.py`**: The Jinja2 template engine wrapper.
*   **`mage2gen/snippets/*.py`**: Logic classes that prepare data for templates.
*   **`mage2gen/templates/`**: Jinja2 templates (`.j2`).
*   **`mage2gen/schema.py`**: Abstraction layer for `db_schema.xml` generation.

## How to Migrate a Legacy Snippet

We are slowly migrating old snippets (which use `argparse` and `string.format`) to the new system.

### Step 1: Identify the Snippet
Pick a snippet from `mage2gen/snippets/` that hasn't been migrated (e.g., `widget.py`).

### Step 2: Create Templates
1.  Look at the code to see what PHP/XML it generates.
2.  Create corresponding `.j2` files in `mage2gen/templates/snippets/<name>/`.
3.  Use `{{ variable }}` syntax instead of `{variable}`.
4.  Use loops `{% for x in y %}` instead of Python string concatenation.

### Step 3: Refactor the Class
1.  Import `typer` and `TemplateEngine`.
2.  Change the `add()` method signature to use type hints:
    ```python
    def add(self, name: str = typer.Option(..., help="Name")):
    ```
3.  Replace `self.add_static_file(...)` logic to use `TemplateEngine.render()`.

### Step 4: Register Command
1.  Open `mage2gen/app.py`.
2.  Add a new `@app.command()` function.
3.  Instantiate the Module and Snippet, then call `add()`.

## How to Add a New Feature

1.  Create your template in `templates/`.
2.  Create a Snippet class in `snippets/`.
3.  Register it in `app.py`.
4.  If it involves database tables, use `mage2gen.schema.Table`.

## Testing
Run unit tests:
```bash
python3 -m unittest discover tests
```
```
