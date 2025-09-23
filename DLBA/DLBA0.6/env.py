# env.py - Environment with lexical scoping
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
        # assign to nearest scope that has name, else current
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            env = self.parent
            while env:
                if name in env.vars:
                    env.vars[name] = value
                    return
                env = env.parent
        self.vars[name] = value

    def declare(self, name, value):
        self.vars[name] = value

    def exists(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False
