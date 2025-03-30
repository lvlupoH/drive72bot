from .categories import handle_categories, show_packages
from .callbacks import setup_callbacks_handler
from .gallery import handle_photo, show_gallery
from .instructors import show_instructors
from .admin import admin_panel

__all__ = [
    'handle_categories',
    'show_moto_packages',
    'show_auto_packages',
    'setup_callbacks_handler',
    'handle_photo',
    'show_gallery',
    'show_instructors',
    'admin_panel'
]
