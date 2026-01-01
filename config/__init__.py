"""
پکیج config - تنظیمات و پیکربندی ربات irProLink
"""

from .settings import *
from .constants import *

# برای سازگاری با کد موجود
try:
    from ..config import AppConfig, EnvironmentConfig, get_config, env_config
except ImportError:
    # اگر ماژول سطح بالا موجود نبود
    pass

# Re-export important classes and functions
__all__ = [
    'AppConfig',
    'EnvironmentConfig',
    'get_config',
    'env_config',
]

__version__ = "1.0.0"
__author__ = "irProLink Team"
