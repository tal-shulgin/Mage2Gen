# mage2gen/app.py
import typer
from typing import Optional
from mage2gen.snippets.observer import ObserverSnippet

app = typer.Typer(
    name="Mage2Gen",
    help="Magento 2 Module Generator",
    add_completion=False,
)

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
    description: str = typer.Option("", help="Module Description")
):
    """
    Create a new Magento 2 module.
    """
    typer.echo(f"Generating module: {package}_{name}")
    # Logic to call Module class would go here

@app.command()
def observer(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    event: str = typer.Option(..., help="Event"),
    scope: str = typer.Option("all", help="Scope")
):
    from mage2gen import Module
    from mage2gen.snippets.observer import ObserverSnippet
    
    mod = Module(package, module)
    snippet = ObserverSnippet(mod)
    snippet.add(event, scope)
    
    # Generate files to current directory or specified path
    mod.generate_module('.')

if __name__ == "__main__":
    app()