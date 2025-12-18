import typer
import os
from typing import Optional
from mage2gen.utils import upperfirst
from mage2gen.discovery.engine import DiscoveryEngine

try:
    from gitingest import ingest
    HAS_GITINGEST = True
except ImportError:
    HAS_GITINGEST = False

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

def validate_name(value: str):
    if not value or not value.strip():
        raise typer.BadParameter("Name cannot be empty")
    return value.strip()

@app.command()
def hello(name: str):
    """
    Say hello to verify Typer installation.
    """
    typer.echo(f"Hello {name}")

@app.command()
def module(
    package: str = typer.Option(..., prompt="Package Name", help="Vendor/Package name", callback=validate_name),
    name: str = typer.Option(..., prompt="Module Name", help="Module Name", callback=validate_name),
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
    fields: str = typer.Option("", help="Fields (name:type)"),
    admin_grid: bool = typer.Option(False, help="Generate Admin Grid"),
    admin_form: bool = typer.Option(False, help="Generate Admin Form"),
    api: bool = typer.Option(False, help="Generate Web API"),
    graphql: bool = typer.Option(False, help="Generate GraphQL CRUD"),
    menu_parent: str = typer.Option(None, help="Parent Menu ID (e.g. Magento_Backend::content)"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    """
    Create a Model (CRUD).
    """
    from mage2gen import Module
    from mage2gen.snippets.model import ModelSnippet
    
    mod = Module(package, module)
    snippet = ModelSnippet(mod)
    snippet.add(
        name=name, 
        fields=fields, 
        admin_grid=admin_grid, 
        admin_form=admin_form, 
        api=api,
        graphql=graphql,
        menu_parent=menu_parent
    )
    
    mod.generate_module(output_dir)

@app.command()
def controller(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    frontname: str = typer.Option(None, help="Frontname"),
    section: str = typer.Option("index", help="Section"),
    action: str = typer.Option("index", help="Action"),
    admin: bool = typer.Option(False, help="Is Admin?"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
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
    depends: str = typer.Option(None, help="Depends on field (e.g. enable:1)"),
    tooltip: str = typer.Option(None, help="Tooltip text"),
    can_restore: bool = typer.Option(False, help="Add canRestore attribute"),
    frontend_class: str = typer.Option(None, help="Frontend CSS class"),
    config_path: str = typer.Option(None, help="Custom config path"),
    if_module_enabled: str = typer.Option(None, help="Only show if module enabled"),
    
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.system import SystemSnippet
    mod = Module(package, module)
    SystemSnippet(mod).add(
        tab, section, group, field, 
        field_type=type, 
        default_value=default, 
        create_tab=create_tab, 
        source_model_options=source_model_options,
        depends=depends,
        tooltip=tooltip,
        can_restore=can_restore,
        frontend_class=frontend_class,
        config_path=config_path,
        if_module_enabled=if_module_enabled
    )
    mod.generate_module(output_dir)

@app.command("system-dynamic")
def system_dynamic(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    tab: str = typer.Option(..., help="Tab ID"),
    section: str = typer.Option(..., help="Section ID"),
    group: str = typer.Option(..., help="Group ID"),
    field: str = typer.Option(..., help="Field ID"),
    columns: str = typer.Option(..., help="Columns (id:Label,id:Label)"),
    create_tab: bool = typer.Option(False, help="Create Tab?"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.system_dynamic import SystemDynamicRowSnippet
    mod = Module(package, module)
    SystemDynamicRowSnippet(mod).add(
        tab, section, group, field, columns, create_tab=create_tab
    )
    mod.generate_module(output_dir)

@app.command("admin-crud")
def admin_crud(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Entity Name"),
    fields: str = typer.Option("", help="Fields (name:type)"),
    menu_parent: str = typer.Option(None, help="Parent Menu ID (e.g. Magento_Backend::content)"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    """
    [Feature] Generates a full Admin CRUD (Grid + Form).
    """
    from mage2gen import Module
    from mage2gen.snippets.model import ModelSnippet
    from mage2gen.snippets.controller import ControllerSnippet
    from mage2gen.utils import upperfirst
    
    mod = Module(package, module)
    
    # Reuse Model Snippet logic which now handles the full stack including menu
    snippet = ModelSnippet(mod)
    snippet.add(
        name=name, 
        fields=fields, 
        admin_grid=True, 
        admin_form=True,
        menu_parent=menu_parent
    )
    
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

@app.command()
def widget(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Widget Name"),
    field: str = typer.Option("title", help="Parameter Name"),
    type: str = typer.Option("text", help="Parameter Type"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.widget import WidgetSnippet
    mod = Module(package, module)
    WidgetSnippet(mod).add(name, field, type)
    mod.generate_module(output_dir)

@app.command("unit-test")
def unit_test(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    suite: str = typer.Option(..., help="Test Suite Name"),
    name: str = typer.Option(..., help="Test Method Name"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.unittest import UnitTestSnippet
    mod = Module(package, module)
    UnitTestSnippet(mod).add(suite, name)
    mod.generate_module(output_dir)

@app.command()
def graphql(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    type: str = typer.Option("Query", help="Type: Query, Mutation"),
    name: str = typer.Option(..., help="Field Name"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.graphqlendpoint import GraphQlEndpointSnippet
    mod = Module(package, module)
    GraphQlEndpointSnippet(mod).add(base_type=type, identifier=name)
    mod.generate_module(output_dir)

@app.command("product-type")
def product_type(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    code: str = typer.Option(..., help="Type Code (e.g. ebook)"),
    label: str = typer.Option(..., help="Label"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.producttype import ProductTypeSnippet
    mod = Module(package, module)
    ProductTypeSnippet(mod).add(code, label)
    mod.generate_module(output_dir)

@app.command("company-attribute")
def company_attribute(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    code: str = typer.Option(..., help="Code"),
    label: str = typer.Option(..., help="Label"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.companyattribute import CompanyAttributeSnippet
    mod = Module(package, module)
    CompanyAttributeSnippet(mod).add(attribute_label=label, extra_params={'attribute_code': code})
    mod.generate_module(output_dir)

@app.command("eav-entity")
def eav_entity(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    name: str = typer.Option(..., help="Entity Name"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.eaventity import EavEntitySnippet
    mod = Module(package, module)
    EavEntitySnippet(mod).add(entity_name=name, adminhtml_grid=True, adminhtml_form=True)
    mod.generate_module(output_dir)

@app.command("configuration-type")
def configuration_type(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    config_name: str = typer.Option(..., help="Config Name (e.g. events)"),
    node_name: str = typer.Option(..., help="Node Name (e.g. event)"),
    field_name: str = typer.Option(..., help="Field Name (e.g. name)"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.configurationtype import ConfigurationTypeSnippet
    mod = Module(package, module)
    ConfigurationTypeSnippet(mod).add(config_name=config_name, node_name=node_name, field_name=field_name)
    mod.generate_module(output_dir)

@app.command("view-model")
def view_model(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    class_name: str = typer.Option(..., help="Class Name"),
    method_name: str = typer.Option(..., help="Method Name"),
    layout_handle: str = typer.Option(..., help="Layout Handle (e.g. catalog_product_view)"),
    reference: str = typer.Option("content", help="Reference Block/Container"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    """
    Create a View Model and inject it into Layout.
    """
    from mage2gen import Module
    from mage2gen.snippets.viewmodel import ViewModelSnippet
    mod = Module(package, module)
    ViewModelSnippet(mod).add(
        classname=class_name,
        methodname=method_name,
        layout_handle=layout_handle,
        reference_name=reference
    )
    mod.generate_module(output_dir)

@app.command()
def language(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    language: str = typer.Option(..., help="Language Code (e.g. nl_NL)"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    from mage2gen import Module
    from mage2gen.snippets.language import LanguageSnippet
    mod = Module(package, module)
    LanguageSnippet(mod).add(language)
    mod.generate_module(output_dir)

@app.command("extension-attribute")
def extension_attribute(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    interface: str = typer.Option(..., help="Target Interface (e.g. Magento\\Sales\\Api\\Data\\OrderInterface)"),
    code: str = typer.Option(..., help="Attribute Code (e.g. vip_points)"),
    type: str = typer.Option("string", help="Attribute Type (string, int, bool)"),
    repository: str = typer.Option(None, help="Repository Interface (for persistence)"),
    table: str = typer.Option(None, help="Database Table (for persistence)"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    """
    Add an Extension Attribute with optional persistence (DB+Plugin).
    """
    from mage2gen import Module
    from mage2gen.snippets.extensionattribute import ExtensionAttributeSnippet
    mod = Module(package, module)
    ExtensionAttributeSnippet(mod).add(
        interface=interface,
        code=code,
        type=type,
        repository=repository,
        table=table
    )
    mod.generate_module(output_dir)

@app.command("message-queue")
def message_queue(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    topic: str = typer.Option(..., help="Topic Name (e.g. vendor.module.event)"),
    consumer: str = typer.Option(..., help="Consumer Class Name (e.g. SyncConsumer)"),
    queue: str = typer.Option(..., help="Queue Name"),
    exchange: str = typer.Option("magento", help="Exchange Name"),
    schema_type: str = typer.Option("string", help="Data Interface or type"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    """
    Create Async Message Queue topology (Topic, Exchange, Queue, Consumer).
    """
    from mage2gen import Module
    from mage2gen.snippets.messagequeue import MessageQueueSnippet
    
    mod = Module(package, module)
    MessageQueueSnippet(mod).add(
        topic=topic,
        consumer=consumer,
        queue=queue,
        exchange=exchange,
        schema_type=schema_type,
        generate_publisher=True
    )
    
    mod.generate_module(output_dir)

@app.command("integration-test")
def integration_test(
    package: str = typer.Option(..., help="Package"),
    module: str = typer.Option(..., help="Module"),
    repository: str = typer.Option(..., help="Repository Interface (e.g. Vendor\\Mod\\Api\\PostRepositoryInterface)"),
    data_interface: str = typer.Option(..., help="Data Interface (e.g. Vendor\\Mod\\Api\\Data\\PostInterface)"),
    test_field: str = typer.Option(None, help="Field to set/check in test (e.g. title)"),
    output_dir: str = typer.Option(default_factory=get_default_output_dir, help="Output directory")
):
    """
    Create a CRUD Integration Test.
    """
    from mage2gen import Module
    from mage2gen.snippets.integrationtest import IntegrationTestSnippet
    
    mod = Module(package, module)
    IntegrationTestSnippet(mod).add(
        repository=repository,
        data_interface=data_interface,
        test_field=test_field
    )
    
    mod.generate_module(output_dir)

@app.command()
def digest(
    path: str = typer.Option(".", help="Root directory to digest"),
    output: str = typer.Option("context.txt", help="Output filename"),
    config: str = typer.Option("m2g.yaml", help="Configuration file to prepend")
):
    """
    Create a context file for AI agents (m2g.yaml + Source Code).
    Requires 'gitingest' to be installed.
    """
    if not HAS_GITINGEST:
        typer.echo("❌ Error: 'gitingest' library not found. Please run 'pip install gitingest'.")
        raise typer.Exit(code=1)

    typer.echo(f"🍪 Baking context digest from: {path}")

    # 1. Define Ignore Patterns (Standard Magento Noise)
    ignore_patterns = [
        "vendor",
        "var",
        "pub",
        "generated", # Magento generated code (factories/proxies)
        "lib",
        "node_modules",
        ".git",
        ".idea",
        ".vscode",
        "*.lock",
        "*.phar",
        "phpserver",
        "auth.json",
        "m2g-index.json", # Don't include the index if present
        output # Don't include the output file itself
    ]

    # 2. Run Ingest
    try:
        summary, tree, content = ingest(path, exclude_patterns=ignore_patterns)
    except Exception as e:
        typer.echo(f"❌ Error during ingestion: {e}")
        raise typer.Exit(code=1)

    # 3. Construct Context
    final_output = []

    # A. Header: The Definition (m2g.yaml)
    config_path = os.path.join(path, config)
    if os.path.exists(config_path):
        final_output.append("=" * 50)
        final_output.append(f"FILE: {config} (Project Definition)")
        final_output.append("=" * 50)
        with open(config_path, 'r') as f:
            final_output.append(f.read())
        final_output.append("\n")

    # B. The Tree Structure
    final_output.append("=" * 50)
    final_output.append("DIRECTORY STRUCTURE")
    final_output.append("=" * 50)
    final_output.append(tree)
    final_output.append("\n")

    # C. The Code Content
    final_output.append(content)

    # 4. Write to File
    output_path = os.path.join(path, output)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(final_output))

    typer.echo(f"✅ Context saved to: {output_path}")
    typer.echo(f"   - Definition: {config} {'(Included)' if os.path.exists(config_path) else '(Not Found)'}")
    typer.echo(f"   - Source Code: {len(content)} chars")

@app.command()
def inspect(
    path: str = typer.Option("/var/www/html", help="Path to Magento project root (Container path)"),
    output: str = typer.Option("m2g-index.json", help="Output filename")
):
    """
    Scan the project and index existing config paths and grid columns.
    """
    typer.echo(f"🕵️  Scanning Project at: {path}...")
    
    if not os.path.exists(os.path.join(path, 'app', 'code')):
        typer.echo("⚠️  Warning: 'app/code' not found. Are you in the project root?")

    engine = DiscoveryEngine(path)
    report = engine.run()
    
    # Save to current working dir (where m2g.yaml likely is)
    output_path = os.path.join(os.getcwd(), output)
    engine.save_report(report, output_path)
    
    typer.echo(f"✅ Index saved to: {output}")
    typer.echo(f"   Found {len(report.get('config_paths', []))} config paths")
    typer.echo(f"   Found {len(report.get('grid_columns', []))} unique grid columns")

if __name__ == "__main__":
    app()
