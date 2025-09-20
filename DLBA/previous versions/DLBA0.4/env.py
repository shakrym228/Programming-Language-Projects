# env.py
# Environment with lexical scoping via parent pointer

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise Exception(f"Undefined variable '{name}'")

    def set(self, name, value):
        # Assign to nearest existing scope; if not found, set in current (for declare use declare())
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            # try to set in parent chain
            env = self.parent
            while env:
                if name in env.vars:
                    env.vars[name] = value
                    return
                env = env.parent
        # not found -> set in current
        self.vars[name] = value

    def declare(self, name, value):
        # always set in current scope
        self.vars[name] = value

    def exists(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False
