import json
import os
from pathlib import Path
from typing import Any, Dict

class ConfigManager:
    DEFAULT_CONFIG = {
        "app": {
            "name": "SystemWatch",
            "version": "1.0.0",
            "debug": False,
            "theme": "dark"
        },
        "monitoring": {
            "process_interval": 2.0,
            "network_interval": 1.0,
            "resource_interval": 1.0,
            "file_system_paths": [
                "C:\\Windows\\System32\\drivers\\etc\\hosts",
                "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
            ]
        },
        "ai": {
            "enabled": True,
            "anomaly_threshold": 0.8,
            "learning_period_hours": 24
        },
        "logging": {
            "level": "INFO",
            "file_path": "logs/system_watch.log",
            "max_size_mb": 10
        }
    }

    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        self._ensure_config_exists()
        self.load_config()

    def _ensure_config_exists(self):
        path = Path(self.config_path)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        if not path.exists():
            self.save_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)
                self._update_recursive(self.config, user_config)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")

    def save_config(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _update_recursive(self, base: Dict, update: Dict):
        for k, v in update.items():
            if isinstance(v, dict) and k in base:
                self._update_recursive(base[k], v)
            else:
                base[k] = v

    def get(self, path: str, default: Any = None) -> Any:
        """Get config value using dot notation e.g. 'app.debug'"""
        keys = path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            return default

    def set(self, path: str, value: Any):
        """Set config value using dot notation"""
        keys = path.split('.')
        target = self.config
        for key in keys[:-1]:
            target = target.setdefault(key, {})
        target[keys[-1]] = value
        self.save_config()

# Global instance
config = ConfigManager()
