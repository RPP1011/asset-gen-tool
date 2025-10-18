"""
Asset-gen backend package initialization.

Exposes Firestore accessor and models for convenience in tests and app code.
"""

from .firebase import FirestoreAccessor, FirestoreError
from . import models

__all__ = ["FirestoreAccessor", "FirestoreError", "models"]
