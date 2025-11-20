"""
API module cho MekongAI Content Generator.

Chứa các router cho different API endpoints.
"""

from .chatbot import router as chatbot_router
from .document import router as document_router
from .history import router as history_router
from .products import router as products_router
from .image import router as image_router

__all__ = ["chatbot_router", "document_router", "history_router", "products_router", "image_router"]