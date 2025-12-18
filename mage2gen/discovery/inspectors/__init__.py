class BaseInspector:
    """Base class for all project inspectors."""
    
    def __init__(self, project_root):
        self.project_root = project_root

    def inspect(self):
        """
        Returns a dictionary of found items.
        Format: {'key': 'category', 'items': [...]}
        """
        raise NotImplementedError