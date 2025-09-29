# env.py - environment with lexical scoping (v0.8)
class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}

    def declare(self, name, value):
        # declare in current scope (used for let and module bindings)
        self.vars[name] = value

    def set(self, name, value):
        # set walks up the chain to find the variable; if not found, raise
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            self.parent.set(name, value)
            return
        raise Exception(f"Undefined variable '{name}'")

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise Exception(f"Undefined variable '{name}'")

    def exists(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False
