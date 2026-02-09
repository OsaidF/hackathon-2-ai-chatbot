"""
Authentication module for Todo AI Chatbot.

Provides dependencies for Better Auth JWT token verification.
"""

from .dependencies import get_current_user, get_optional_user

__all__ = ["get_current_user", "get_optional_user"]
