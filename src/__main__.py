import os
import numpy as np
from threading import Thread

from src.workspace import Workspace
from src.interface import Interface
from src.interfaces.start import Start

def main():
    """Main entry for the program.
    """
    interface = Interface()
    interface.instanciate()