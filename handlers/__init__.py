# handlers/__init__.py

# Импорт обработчиков категорий
from .categories import (
    handle_categories,
    show_moto_packages,
    show_auto_packages
)

# Импорт обработчика обратных звонков
from .callbacks import setup_callbacks_handler

# Импорт галереи
from .gallery import show_gallery

# Импорт инструкторов
from .instructors import show_instructors

# Импорт админ-панели
from .admin import (
    admin_panel,
    add_schedule_handler,
    edit_user_handler
)

# Экспорт всех компонентов
__all__ = [
    'handle_categories',
    'show_moto_packages',
    'show_auto_packages',
    'setup_callbacks_handler',
    'show_gallery',
    'show_instructors',
    'admin_panel',
    'add_schedule_handler',
    'edit_user_handler'
]
