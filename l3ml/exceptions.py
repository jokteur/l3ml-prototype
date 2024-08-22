class ProgramInterrupt(Exception):
    """Base class for launching a program interrupt."""
    pass

class StateError(Exception):
    """Base class for when something failed when loaded the next state in MCS"""
    pass
