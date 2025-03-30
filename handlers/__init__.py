from .categories import (
    handle_categories,
    show_moto_packages,
    show_auto_packages,
    show_package_details,
    handle_back
)
from .callbacks import get_callback_conversation_handler  # Исправленный импорт
from .gallery import show_gallery
from .instructors import show_instructors
from .admin import admin_panel

__all__ = [
    'handle_categories',
    'get_callback_handler',
    'show_gallery',
    'show_instructors',
    'show_profile'
]
