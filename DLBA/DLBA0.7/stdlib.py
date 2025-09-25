# stdlib.py - convenience loader (v0.7)
from interpreter import register_stdlib

a = register_stdlib
# simple wrapper file: consumers can import register_stdlib from interpreter or import this file to force registration
# Typically main will call register_stdlib(env)
