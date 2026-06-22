# cangling/__init__.py

# 1. Define the package version
__version__ = "0.1.20"

# 2. Maintain your existing package imports
from .workflow import Workflow, ProgressContent, MessageType, ProgressBaseMessage
from .engine import Engine, Context

# 3. Expose everything via __all__ so it is clean for "from cangling import *"
__all__ = [
    "__version__",
    "Workflow", 
    "MessageType", 
    "ProgressBaseMessage", 
    "ProgressContent",
    "Engine",
    "Context"
]