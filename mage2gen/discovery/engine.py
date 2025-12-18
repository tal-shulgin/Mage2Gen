import json
import os
from .inspectors.config import ConfigInspector
from .inspectors.grid import GridInspector
from ..core.library import StandardLibrary # [NEW IMPORT]

class DiscoveryEngine:
    def __init__(self, project_root):
        self.project_root = project_root
        self.inspectors = [
            ConfigInspector(project_root),
            GridInspector(project_root)
        ]

    def run(self):
        report = {}
        
        # 1. Run Dynamic Inspectors (Project Scan)
        for inspector in self.inspectors:
            try:
                data = inspector.inspect()
                report.update(data)
            except Exception as e:
                print(f"Inspector failed: {e}")
        
        # 2. Inject Static Standard Library
        # We add this as a reference section for the AI
        report['standard_library'] = {
            'source_models': StandardLibrary.SOURCE_MODELS
        }
        
        return report

    def save_report(self, report, output_path):
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=4)