from .categories import (
    handle_categories,
    show_moto_packages,
    show_auto_packages
)

from .callbacks import (
    setup_callbacks_handler
)

from .gallery import (
    show_gallery
)

from .instructors import (
    show_instructors  # Исправленное имя функции
)

from .admin import (
    admin_panel
)

__all__ = [
    'handle_categories',
    'show_moto_packages',
    'show_auto_packages',
    'setup_callbacks_handler',
    'show_gallery',
    'show_instructors',  # Добавлен экспорт
    'admin_panel'
]
