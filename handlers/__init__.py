from .categories import handle_categories, show_moto_packages
from .callbacks import setup_callbacks_handler
from .gallery import show_gallery
from .instructors import show_instructors
from .admin import setup_admin_handlers

__all__ = [
    'handle_categories',
    'show_moto_packages',
    'setup_callbacks_handler',
    'show_gallery',
    'show_instructors',
    'setup_admin_handlers'
]
