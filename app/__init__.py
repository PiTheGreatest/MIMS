"""
MIMS: Unified Healthcare Management System
Statutory Registry Headquarters
"""
from .models import Base
from .database import engine

__version__ = "2.3.0"
__author__ = "Ezinne Priscilla Ngwu"

__all__ = ["Base", "engine", "__version__"]