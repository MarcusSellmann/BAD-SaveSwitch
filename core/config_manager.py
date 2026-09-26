"""Persistence helpers for the application's JSON configuration."""

import json
import os

CONFIG_FILE = "config.json"


class ConfigManager:
    """Load and save the configuration in the current working directory."""

    @staticmethod
    def load():
        """Create default settings when needed and return parsed configuration."""

        if not os.path.exists(CONFIG_FILE):

            data = {
                "Season1_2_local_directory": "",
                "Season1_2_appdata_directory": "",
                "Season3_local_directory": "",
                "Season3_appdata_directory": "",
                "library_path": "",
                "thumbnail_path": "",
                "language": "de"
            }

            ConfigManager.save(data)

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save(data):
        """Write configuration data as indented UTF-8 JSON."""

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)