# Environment for DLBA variables

class Environment:
    def __init__(self):
        self.vars = {}

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        raise Exception(f"Undefined variable '{name}'")

    def set(self, name, value):
        self.vars[name] = value

    def exists(self, name):
        return name in self.vars
