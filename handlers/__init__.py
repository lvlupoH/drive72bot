from .categories import (
    handle_categories,
    show_moto_packages,
    show_auto_packages,
    show_package_details,
    handle_back
)
from .callbacks import start_callback, get_name, get_phone, get_question
from .back import back_handler
from .gallery import show_gallery
from .instructors import show_instructors
from .profile import show_profile
# handlers/__init__.py
from .admin import get_admin_handler  # Добавьте эту строку
from .admin import admin_panel

__all__ = [
    'handle_categories',
    'get_callback_handler',
    'show_gallery',
    'show_instructors',
    'show_profile'
]
