import os
import xml.etree.ElementTree as ET
from . import BaseInspector

class ConfigInspector(BaseInspector):
    def inspect(self):
        paths = {} # Use dict for deduplication by path key
        
        # Walk through app/code
        search_path = os.path.join(self.project_root, 'app', 'code')
        if not os.path.exists(search_path):
            return {}

        for root, _, files in os.walk(search_path):
            if 'system.xml' in files:
                try:
                    tree = ET.parse(os.path.join(root, 'system.xml'))
                    # Iterate Sections
                    for section in tree.findall(".//{*}section"):
                        sec_id = section.get('id')
                        # Iterate Groups
                        for group in section.findall(".//{*}group"):
                            grp_id = group.get('id')
                            # Iterate Fields
                            for field in group.findall(".//{*}field"):
                                field_id = field.get('id')
                                path = f"{sec_id}/{grp_id}/{field_id}"
                                
                                # Extract Attributes
                                field_type = field.get('type')
                                
                                # Extract Child Nodes (Source/Backend Models)
                                source_model = None
                                source_node = field.find(".//{*}source_model")
                                if source_node is not None:
                                    source_model = source_node.text

                                backend_model = None
                                backend_node = field.find(".//{*}backend_model")
                                if backend_node is not None:
                                    backend_model = backend_node.text

                                # Store object
                                paths[path] = {
                                    'path': path,
                                    'type': field_type,
                                    'source_model': source_model,
                                    'backend_model': backend_model
                                }
                except Exception as e:
                    # XML parsing error, skip file
                    continue
        
        # Return sorted list of objects
        sorted_paths = sorted(paths.values(), key=lambda x: x['path'])
        return {'config_paths': sorted_paths}