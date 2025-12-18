import os
import xml.etree.ElementTree as ET
from . import BaseInspector

class GridInspector(BaseInspector):
    def inspect(self):
        columns = []
        search_path = os.path.join(self.project_root, 'app', 'code')
        if not os.path.exists(search_path):
            return {}

        for root, _, files in os.walk(search_path):
            for file in files:
                if file.endswith('.xml') and 'ui_component' in root:
                    try:
                        tree = ET.parse(os.path.join(root, file))
                        # Find all columns
                        for col in tree.findall(".//{*}column"):
                            name = col.get('name')
                            if name:
                                columns.append(name)
                    except:
                        continue
        return {'grid_columns': sorted(list(set(columns)))}