# mage2gen/app.py
import typer
import os
from typing import Optional

app = typer.Typer(
    name="Mage2Gen",
    help="Magento 2 Module Generator",
    add_completion=False,
)

def get_default_output_dir():
    """
    Returns output directory from env var or defaults to current directory.
    To use with Docker volume: export MAGE2GEN_OUTPUT='/usr/app/generated_modules'
    """
    return os.environ.get("MAGE2GEN_OUTPUT", ".")

@app.command()
def hello(name: str):
    """
    Say hello to verify Typer installation.
    """
    typer.echo(f"Hello {name}")

@app.command()
def module(
    package: str = typer.Option(..., prompt="Package Name", help="Vendor/Package name"),
    name: str = typer.Option(..., prompt="Module Name", help="Module Name"),
    description: str = typer.Option("", help="Module Description"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    """
    Create a new Magento 2 module.
    """
    from mage2gen import Module
    typer.echo(f"Generating module: {package}_{name} in {output_dir}")
    
    mod = Module(package, name, description)
    mod.generate_module(output_dir)

@app.command()
def observer(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    event: str = typer.Option(..., help="Event"),
    scope: str = typer.Option("all", help="Scope"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    """
    Create an Observer.
    """
    from mage2gen import Module
    from mage2gen.snippets.observer import ObserverSnippet
    
    mod = Module(package, module)
    snippet = ObserverSnippet(mod)
    snippet.add(event, scope)
    
    mod.generate_module(output_dir)

@app.command()
def model(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Model Name"),
    fields: str = typer.Option("", help="Fields (name:type,name:type)"),
    admin_grid: bool = typer.Option(False, help="Generate Admin Grid"),
    api: bool = typer.Option(False, help="Generate Web API"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    """
    Create a Model (CRUD).
    """
    from mage2gen import Module
    from mage2gen.snippets.model import ModelSnippet
    
    mod = Module(package, module)
    snippet = ModelSnippet(mod)
    snippet.add(name=name, fields=fields, admin_grid=admin_grid, api=api)
    
    mod.generate_module(output_dir)

if __name__ == "__main__":
    app()