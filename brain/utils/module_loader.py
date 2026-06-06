"""
Utility for dynamically loading Python modules from relative paths.
"""
import importlib.util
from pathlib import Path


def load_module_from_relative_path(name: str, relative_path: Path):
    """
    Dynamically load a Python module from a relative path.
    
    Args:
        name: Module name (for identification)
        relative_path: Relative path from this file to the module
        
    Returns:
        The loaded module object
        
    Raises:
        ImportError: If module cannot be loaded
    """
    module_path = Path(__file__).resolve().parent.parent / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module '{name}' from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
