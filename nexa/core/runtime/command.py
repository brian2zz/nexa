from nexa.core.runtime.logger import logger

class BaseCommand:
    """
    Base class for all Nexa CLI commands.
    """
    def __init__(self, args):
        self.args = args
        self.logger = logger

    def run(self):
        raise NotImplementedError("Commands must implement run()")

    def parse_flags(self):
        """
        Simple flag parser for commands.
        """
        flags = {
            "backend": "--backend" in self.args,
            "frontend": "--frontend" in self.args,
            "dry_run": "--dry-run" in self.args,
            "verbose": "--verbose" in self.args
        }
        return flags
