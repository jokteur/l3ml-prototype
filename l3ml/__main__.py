import os
import numpy as np
from threading import Thread

from l3ml.workspace import Workspace
from l3ml.interface import Interface
from l3ml.interfaces.start import Start

def main():
    """Main entry for the program.
    """
    interface = Interface()
    interface.instanciate()