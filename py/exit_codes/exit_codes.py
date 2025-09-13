from enum import Enum

class ExitCode(Enum):
    """ExitCode is a general purpose Enum for detailed exit codes.

    Some errors are intentionally grouped in ranges by the leading digit.
    For example, all codes of value 1X might be recoverable,
    while all codes of value 2X might be due to configuration,
    and so on.

    Initially created for the ARTILLERY game's Python packages,
    this module could be used for other projects.
    
    Attributes:
        SUCCESS (int): Program exited successfully and normally.
    """
    SUCCESS = 0
