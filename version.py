"""
Version management for irProLink Bot
"""

import json
import os
from pathlib import Path

class VersionManager:
    """Manage bot version and updates"""
    
    def __init__(self, version_file="data/version.json"):
        self.version_file = version_file
        self.current_version = "6.2.0"
        self.release_year = "2026"
        self.load_version()
    
    def load_version(self):
        """Load version from file or use default"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_version = data.get('version', self.current_version)
                    self.release_year = data.get('release_year', self.release_year)
        except Exception:
            pass
    
    def save_version(self):
        """Save current version to file"""
        try:
            os.makedirs(os.path.dirname(self.version_file), exist_ok=True)
            data = {
                'version': self.current_version,
                'release_year': self.release_year,
                'last_updated': self.get_current_date()
            }
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def increment_version(self):
        """Increment version by one unit (e.g., 6.1.0 -> 6.1.1)"""
        parts = self.current_version.split('.')
        if len(parts) == 3:
            try:
                major = int(parts[0])
                minor = int(parts[1])
                patch = int(parts[2])
                patch += 1
                self.current_version = f"{major}.{minor}.{patch}"
                self.save_version()
                return True
            except ValueError:
                pass
        return False
    
    def get_current_date(self):
        """Get current date in YYYY-MM-DD format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_version_info(self):
        """Get version information as dictionary"""
        return {
            'version': self.current_version,
            'release_year': self.release_year,
            'last_updated': self.get_current_date()
        }
    
    def display_version(self):
        """Display version information"""
        return f"Version: {self.current_version} ({self.release_year})"


# Global instance
version_manager = VersionManager()


def get_version():
    """Get current version"""
    return version_manager.current_version


def get_release_year():
    """Get release year"""
    return version_manager.release_year


def increment_version():
    """Increment version and return new version"""
    if version_manager.increment_version():
        return version_manager.current_version
    return None
