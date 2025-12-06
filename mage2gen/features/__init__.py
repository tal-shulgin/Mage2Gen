class Feature:
    def __init__(self, module):
        self._module = module

    def add(self, *args, **kwargs):
        raise NotImplementedError("Features must implement add()")
