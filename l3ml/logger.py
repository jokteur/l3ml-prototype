import logging
import sys

from l3ml.singleton import Singleton
from l3ml.exceptions import ProgramInterrupt

class Logger(metaclass=Singleton):
    """Logging class which is a wrapper around the logging module.

    The log is sometimes desired in the web-based GUI and in the console at the same time."""

    def __init__(self, format='%(levelname)s - %(message)s'):
        """Sets the logging module with the specified format"""
        logging.basicConfig()
        self.logger = logging.getLogger('l3ml')

        self.formatter = logging.Formatter(format)

        self.server = None

        self.handlers = []

        handler = logging.NullHandler()
        self.handlers.append(handler)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)  # Default level

        # Due to Bokeh serve messing up the logging module, this is a work-around
        # to avoid printing the same message twice to the console
        for h in logging.getLogger().handlers:
            h.setFormatter(self.formatter)

        self.log_file = None

    def add_server(self, server):
        """Adds a Bokeh server to the logger such that it is able to quit
        safely the app"""
        self.server = server

    def add_handler(self, handler, verbosity):
        """Adds a custom logging StreamHandler to the logging module"""
        if int(verbosity) == 2:
            handler.setLevel(logging.INFO)
        elif int(verbosity) == 1:
            handler.setLevel(logging.WARNING)
        elif int(verbosity) == 0:
            handler.setLevel(logging.ERROR)

        handler.setFormatter(self.formatter)

        self.handlers.append(handler)
        self.logger.addHandler(handler)

    def set_verbosity(self, verbosity):
        """Sets the level of verbosity of the logger.

         2 (by default) : infos, warning and errors are printed
         1 : only warning and errors are printed
         0 : only errors are printed
        """
        if int(verbosity) == 2:
            self.logger.setLevel(logging.INFO)
        elif int(verbosity) == 1:
            self.logger.setLevel(logging.WARNING)
        elif int(verbosity) == 0:
            self.logger.setLevel(logging.ERROR)

    def flush(self):
        """Flushes the last entry in all log handlers"""
        for h in logging.getLogger('pymcs').handlers:
            h.flush()

        # Dirty hack for flushing the console, because of the NullHandler
        sys.stdout.write("\033[F")  # back to previous line
        sys.stdout.write("\033[K")  # clear line
        sys.stdout.flush()

    def _add_spacing(self, message, level):
        """Adds spaces before to define the level"""
        if level > 0:
            return "  " * level + message
        return message

    def info(self, message, level=0, replace=False):
        """Emits an information in the log."""
        if replace:
            self.flush()
        self.logger.info(self._add_spacing(message, level))

    def warning(self, message, level=0, replace=False):
        """Emits a warning in the log."""
        if replace:
            self.flush()
        self.logger.warning(self._add_spacing(message, level))

    def error(self, message, level=0, replace=False):
        """Emits an error in the log."""
        if replace:
            self.flush()
        self.logger.error(self._add_spacing(message, level))

    def fatal(self, message, level=0, replace=False):
        """Emits an error in the log and quits the program."""
        if replace:
            self.flush()
        self.logger.error(self._add_spacing(message, level))
        if self.server:
            self.server.stop()
        raise ProgramInterrupt()
