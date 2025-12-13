import yaml
import logging
import os
from mage2gen import Module

# Import all snippets
from mage2gen.snippets import (
    ModelSnippet, ControllerSnippet, BlockSnippet, 
    ObserverSnippet, PluginSnippet, SystemSnippet,
    ConsoleSnippet, CronjobSnippet, ApiSnippet,
    PaymentSnippet, ShippingSnippet, WidgetSnippet
)

logger = logging.getLogger(__name__)

# Map YAML types to Snippet Classes
SNIPPET_MAP = {
    'model': ModelSnippet,
    'controller': ControllerSnippet,
    'block': BlockSnippet,
    'observer': ObserverSnippet,
    'plugin': PluginSnippet,
    'system': SystemSnippet,
    'console': ConsoleSnippet,
    'cron': CronjobSnippet,
    'api': ApiSnippet,
    'payment': PaymentSnippet,
    'shipping': ShippingSnippet,
    'widget': WidgetSnippet
}

def parse_and_generate(config_path, output_dir):
    """
    Reads m2g.yaml and executes generation.
    """
    try:
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)

        if not data or 'modules' not in data:
            logger.warning("⚠️  No 'modules' defined in m2g.yaml")
            return

        for mod_name, mod_data in data['modules'].items():
            generate_module_from_config(mod_name, mod_data, output_dir)

    except yaml.YAMLError as exc:
        logger.error(f"❌ YAML Error: {exc}")
    except Exception as e:
        logger.error(f"❌ Generation Error: {e}")

def generate_module_from_config(full_name, data, output_dir):
    """
    Generates a single module based on dict data.
    """
    try:
        # Parse "Vendor_Module"
        if '_' not in full_name:
            logger.error(f"❌ Invalid module name '{full_name}'. Must be Vendor_Module.")
            return

        vendor, name = full_name.split('_', 1)
        description = data.get('description', f'Generated module {full_name}')
        
        logger.info(f"🔨 Building Module: {full_name}...")
        
        # 1. Initialize Module
        module = Module(vendor, name, description)

        # 2. Process Components
        components = data.get('components', [])
        for comp in components:
            comp_type = comp.get('type')
            
            if comp_type not in SNIPPET_MAP:
                logger.warning(f"   ⚠️  Unknown component type: {comp_type}")
                continue

            snippet_class = SNIPPET_MAP[comp_type]
            snippet = snippet_class(module)
            
            # Prepare arguments
            # We remove 'type' from args passed to add()
            args = {k: v for k, v in comp.items() if k != 'type'}
            
            # Special case mappings (YAML friendly -> Python Argument friendly)
            # e.g. 'fields' in YAML might be a list, but Snippet expects "col:type,col:type" string
            if comp_type == 'model' and isinstance(args.get('fields'), list):
                # Convert list of dicts to string: "title:text:required,views:int"
                field_strs = []
                for f in args['fields']:
                    f_str = f"{f['name']}:{f['type']}"
                    if f.get('required'):
                        f_str += ":required"
                    field_strs.append(f_str)
                args['fields'] = ",".join(field_strs)

            try:
                snippet.add(**args)
                logger.info(f"   + Added {comp_type}: {args.get('name', 'unnamed')}")
            except Exception as e:
                logger.error(f"   ❌ Failed to add {comp_type}: {e}")

        # 3. Write to Disk
        module.generate_module(output_dir)
        logger.info(f"✅ Generated {full_name}")

    except Exception as e:
        logger.error(f"❌ Failed to generate module {full_name}: {e}")