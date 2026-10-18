"""Persistence helpers for the application's JSON configuration."""

import json
import os
import sys
from pathlib import Path

CONFIG_FILE = "config.json"
APPDATA_PATH_SUFFIXES = ("1535311495", "1535311494", "1535311497")
APPDATA_PATH_PREFIXES = {
    "Season1_2_appdata_directory": "BeingaDIK-",
    "Season3_appdata_directory": "BeingaDIKBeingaDIKSeason3-"
}


def _config_path():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / CONFIG_FILE
    return Path(CONFIG_FILE)


class ConfigManager:
    """Load and save the configuration in the current working directory."""

    @staticmethod
    def _default_appdata_paths():
        """Build suggested game paths under the current user's AppData folder."""

        appdata_directory = os.environ.get("APPDATA")
        if not appdata_directory:
            return {}

        renpy_directory = os.path.join(appdata_directory, "RenPy")
        paths = {}
        for key, folder_prefix in APPDATA_PATH_PREFIXES.items():
            candidates = [
                os.path.join(
                    renpy_directory,
                    f"{folder_prefix}{platform_suffix}"
                )
                for platform_suffix in APPDATA_PATH_SUFFIXES
            ]
            paths[key] = next(
                (path for path in candidates if os.path.isdir(path)),
                candidates[0]
            )

        return paths

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
            data = json.load(f)

        updated = False
        for key, path in ConfigManager._default_appdata_paths().items():
            if not data.get(key):
                data[key] = path
                updated = True

        if updated:
            ConfigManager.save(data)

        return data

    @staticmethod
    def save(data):
        """Write configuration data as indented UTF-8 JSON."""

        with open(_config_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)