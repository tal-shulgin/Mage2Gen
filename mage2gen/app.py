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
    from mage2gen.snippets.observer import ObserverSnippet, Scope

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
    admin_form: bool = typer.Option(False, help="Generate Admin Form"), # V3
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
    # Pass all mapped args
    snippet.add(name=name, fields=fields, admin_grid=admin_grid, admin_form=admin_form, api=api)
    
    mod.generate_module(output_dir)

@app.command()
def controller(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    frontname: str = typer.Option(None, help="Frontname"),
    section: str = typer.Option("index", help="Section"),
    action: str = typer.Option("index", help="Action"),
    admin: bool = typer.Option(False, help="Is Admin?")
):
    from mage2gen import Module
    from mage2gen.snippets.controller import ControllerSnippet
    
    mod = Module(package, module)
    snippet = ControllerSnippet(mod)
    snippet.add(frontname=frontname, section=section, action=action, adminhtml=admin)
    
    mod.generate_module(output_dir)

@app.command()
def block(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Block Name"),
    layout_handle: str = typer.Option(..., help="Layout Handle"),
    reference: str = typer.Option("content", help="Container Reference"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.block import BlockSnippet
    
    mod = Module(package, module)
    snippet = BlockSnippet(mod)
    snippet.add(name=name, layout_handle=layout_handle, reference=reference)
    
    mod.generate_module(output_dir)

@app.command()
def plugin(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    target_class: str = typer.Option(..., help="Target Class"),
    method: str = typer.Option(..., help="Method"),
    type: str = typer.Option("after", help="Type"),
    sort_order: int = typer.Option(10, help="Sort Order"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.plugin import PluginSnippet
    
    mod = Module(package, module)
    snippet = PluginSnippet(mod)
    snippet.add(target_class=target_class, method=method, type=type, sort_order=sort_order)
    
    mod.generate_module(output_dir)

@app.command()
def schemapatch(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Patch Name (e.g. RenameTable)"),
    operation: str = typer.Option("custom", help="Operation: custom, rename_table, rename_column"),
    table: str = typer.Option(None, help="Table Name (for rename_column)"),
    old_name: str = typer.Option(None, help="Old Name"),
    new_name: str = typer.Option(None, help="New Name"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    """
    Create a Schema Patch for safe DB migrations.
    """
    from mage2gen import Module
    from mage2gen.snippets.schemapatch import SchemaPatchSnippet
    
    mod = Module(package, module)
    snippet = SchemaPatchSnippet(mod)
    snippet.add(
        patch_name=name, 
        operation=operation, 
        table_name=table, 
        old_name=old_name, 
        new_name=new_name
    )
    
    mod.generate_module(output_dir)

@app.command()
def console(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Command Name"),
    description: str = typer.Option("Sample command", help="Description"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.console import ConsoleSnippet
    mod = Module(package, module)
    ConsoleSnippet(mod).add(name, description)
    mod.generate_module(output_dir)

@app.command()
def cronjob(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Job Name"),
    schedule: str = typer.Option("*/5 * * * *", help="Schedule"),
    group: str = typer.Option("default", help="Group"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.cronjob import CronjobSnippet
    mod = Module(package, module)
    CronjobSnippet(mod).add(name, schedule, group)
    mod.generate_module(output_dir)

@app.command()
def helper(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Name"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.helper import HelperSnippet
    mod = Module(package, module)
    HelperSnippet(mod).add(name)
    mod.generate_module(output_dir)

@app.command()
def logger(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Name"),
    filename: str = typer.Option("custom.log", help="Filename"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.logger import LoggerSnippet
    mod = Module(package, module)
    LoggerSnippet(mod).add(name, filename)
    mod.generate_module(output_dir)

@app.command("product-attribute")
def product_attribute(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    code: str = typer.Option(..., help="Code"),
    label: str = typer.Option(..., help="Label"),
    input_type: str = typer.Option("text", help="Input Type"),
    source_model: str = typer.Option(None, help="Source Model"),
    required: bool = typer.Option(False, help="Required?"),
    sort_order: int = typer.Option(100, help="Sort Order"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.productattribute import ProductAttributeSnippet
    mod = Module(package, module)
    ProductAttributeSnippet(mod).add(code=code, label=label, input_type=input_type, source_model=source_model, required=required, sort_order=sort_order)
    mod.generate_module(output_dir)

@app.command("category-attribute")
def category_attribute(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    code: str = typer.Option(..., help="Code"),
    label: str = typer.Option(..., help="Label"),
    input_type: str = typer.Option("text", help="Input Type"),
    required: bool = typer.Option(False, help="Required?"),
    source_model: str = typer.Option(None, help="Source Model"),
    source_model_options: str = typer.Option(None, help="Options"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.categoryattribute import CategoryAttributeSnippet
    mod = Module(package, module)
    CategoryAttributeSnippet(mod).add(label=label, code=code, frontend_input=input_type, required=required, source_model=source_model, source_model_options=source_model_options)
    mod.generate_module(output_dir)

@app.command("customer-attribute")
def customer_attribute(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    code: str = typer.Option(..., help="Code"),
    label: str = typer.Option(..., help="Label"),
    input_type: str = typer.Option("text", help="Input Type"),
    customer_entity: str = typer.Option("customer", help="Entity"),
    customer_forms: str = typer.Option(None, help="Forms"),
    customer_address_forms: str = typer.Option(None, help="Address Forms"),
    static_field: bool = typer.Option(False, help="Static?"),
    required: bool = typer.Option(False, help="Required?"),
    source_model: str = typer.Option(None, help="Source Model"),
    source_model_options: str = typer.Option(None, help="Options"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.customerattribute import CustomerAttributeSnippet
    mod = Module(package, module)
    CustomerAttributeSnippet(mod).add(
        label=label,
        code=code, 
        frontend_input=input_type,
        customer_entity=customer_entity,
        customer_forms=customer_forms,
        customer_address_forms=customer_address_forms,
        static_field=static_field,
        required=required,
        source_model=source_model,
        source_model_options=source_model_options
    )
    mod.generate_module(output_dir)

@app.command()
def system(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    tab: str = typer.Option(..., help="Tab ID"),
    section: str = typer.Option(..., help="Section ID"),
    group: str = typer.Option(..., help="Group ID"),
    field: str = typer.Option(..., help="Field ID"),
    type: str = typer.Option("text", help="Type"),
    default: str = typer.Option("", help="Default Value"),
    create_tab: bool = typer.Option(False, help="Create Tab?"),
    source_model_options: str = typer.Option(None, help="Options"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.system import SystemSnippet
    mod = Module(package, module)
    SystemSnippet(mod).add(tab, section, group, field, field_type=type, default_value=default, create_tab=create_tab, source_model_options=source_model_options)
    mod.generate_module(output_dir)

@app.command("admin-crud")
def admin_crud(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Entity Name"),
    fields: str = typer.Option("", help="Fields (name:type)"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    """
    [Feature] Generates a full Admin CRUD (Model + Grid + Controllers).
    """
    from mage2gen import Module
    from mage2gen.features.admin_crud import AdminCrudFeature
    
    mod = Module(package, module)
    feature = AdminCrudFeature(mod)
    feature.add(name=name, fields=fields)
    
    mod.generate_module(output_dir)

@app.command()
def payment(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Method Name"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.payment import PaymentSnippet
    mod = Module(package, module)
    PaymentSnippet(mod).add(name)
    mod.generate_module(output_dir)

@app.command()
def shipping(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Method Name"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.shipping import ShippingSnippet
    mod = Module(package, module)
    ShippingSnippet(mod).add(name)
    mod.generate_module(output_dir)

@app.command()
def api(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="API Name"),
    method: str = typer.Option("GET", help="HTTP Method"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.api import ApiSnippet
    mod = Module(package, module)
    ApiSnippet(mod).add(name, method)
    mod.generate_module(output_dir)

if __name__ == "__main__":
    app()