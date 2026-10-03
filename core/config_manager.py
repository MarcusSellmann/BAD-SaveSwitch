"""Persistence helpers for the application's JSON configuration."""

import json
import os
import sys
from pathlib import Path

CONFIG_FILE = "config.json"


def _config_path():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / CONFIG_FILE
    return Path(CONFIG_FILE)


class ConfigManager:
    """Load and save the configuration in the current working directory."""

    @staticmethod
    def load():
        """Create default settings when needed and return parsed configuration."""

        config_path = _config_path()
        if not os.path.exists(config_path):

            data = {
                "Season1_2_local_directory": "",
                "Season1_2_appdata_directory": "",
                "Season3_local_directory": "",
                "Season3_appdata_directory": "",
                "library_path": "",
                "thumbnail_path": "",
                "language": "en"
            }

            ConfigManager.save(data)

        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save(data):
        """Write configuration data as indented UTF-8 JSON."""

        with open(_config_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)