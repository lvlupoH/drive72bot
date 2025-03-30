from .categories import handle_categories, show_packages
from .callbacks import get_callback_handler  # Исправленный импорт
from .back import back_handler
from .gallery import show_gallery
from .instructors import show_instructors
from .profile import show_profile
# handlers/__init__.py
from .admin import get_admin_handler  # Добавьте эту строку

__all__ = [
    'handle_categories',
    'get_callback_handler',
    'show_gallery',
    'show_instructors',
    'show_profile'
]
