"""Filesystem operations for save-set creation and switching."""

import os
import json
import shutil
import tempfile
import uuid

from data.models import SaveSet
from datetime import datetime

class SaveManager:
    """Manage save snapshots across the configured game directories."""

    SAVE_LOCATIONS = {
        "Season1_2_local": "Season1_2_local_directory",
        "Season1_2_appdata": "Season1_2_appdata_directory",
        "Season3_local": "Season3_local_directory",
        "Season3_appdata": "Season3_appdata_directory"
    }

    def __init__(self, config):
        """Create a manager using the shared application configuration."""
        self.config = config

    def get_all_sets(self):
        """Load valid save-set metadata and return it sorted by name."""

        library = self.config["library_path"]

        if not os.path.exists(library):
            return []

        result = []

        for folder in os.listdir(library):

            meta_file = os.path.join(
                library,
                folder,
                "meta.json"
            )

            if not os.path.exists(meta_file):
                continue

            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue

            save_set = SaveSet.from_dict(meta)

            if not save_set.id:
                save_set.id = folder

            result.append(save_set)

        return sorted(result, key=lambda x: x.name)

    def create_set(
            self,
            name,
            thumbnail,
            keep_original=True,
            description=""
    ):
        """Create a snapshot and optionally remove source save files."""

        library = self.config["library_path"]
        os.makedirs(library, exist_ok=True)

        set_id = str(uuid.uuid4())

        folder = os.path.join(
            library,
            set_id
        )

        saves_folder = os.path.join(
            folder,
            "saves"
        )

        sources = []
        for location_name, config_key in self.SAVE_LOCATIONS.items():
            source = self.config.get(config_key, "")
            if source and os.path.isdir(source):
                sources.append((location_name, source))

        with tempfile.TemporaryDirectory() as backup_root:
            source_backups = {}
            metadata_backups = {}

            if not keep_original:
                for index, (_, source) in enumerate(sources):
                    if source in source_backups:
                        continue
                    backup = os.path.join(backup_root, f"source_{index}")
                    shutil.copytree(source, backup)
                    source_backups[source] = backup

                for existing_folder in os.listdir(library):
                    existing_meta_file = os.path.join(
                        library,
                        existing_folder,
                        "meta.json"
                    )

                    if os.path.isfile(existing_meta_file):
                        with open(existing_meta_file, "rb") as f:
                            metadata_backups[existing_meta_file] = f.read()

            try:
                os.makedirs(saves_folder)

                for location_name, source in sources:
                    location_folder = os.path.join(saves_folder, location_name)
                    shutil.copytree(source, location_folder)

                    if not keep_original:
                        self._remove_save_files(source)

                thumb_name = ""

                if thumbnail:
                    thumb_name = os.path.basename(thumbnail)

                with open(
                        os.path.join(folder, "meta.json"),
                        "w",
                        encoding="utf-8"
                ) as f:

                    save_set = SaveSet(
                        id=set_id,
                        name=name,
                        description=description,
                        thumbnail=thumb_name,
                        created=datetime.now().isoformat()
                    )

                    json.dump(
                        save_set.to_dict(),
                        f,
                        indent=4
                    )

                if not keep_original:
                    for existing_folder in os.listdir(library):

                        existing_meta_file = os.path.join(
                            library,
                            existing_folder,
                            "meta.json"
                        )

                        if not os.path.isfile(existing_meta_file):
                            continue

                        with open(existing_meta_file, "r", encoding="utf-8") as f:
                            metadata = json.load(f)

                        metadata["active"] = False

                        with open(existing_meta_file, "w", encoding="utf-8") as f:
                            json.dump(metadata, f, indent=4)
            except Exception:
                if os.path.isdir(folder):
                    shutil.rmtree(folder)

                for source, backup in source_backups.items():
                    shutil.rmtree(source)
                    shutil.copytree(backup, source)

                for meta_file, contents in metadata_backups.items():
                    with open(meta_file, "wb") as f:
                        f.write(contents)

                raise

    def create_empty_set(self, name, thumbnail, description=""):
        """Create a save set with empty save-location folders."""

        library = self.config["library_path"]
        os.makedirs(library, exist_ok=True)

        set_id = str(uuid.uuid4())
        folder = os.path.join(library, set_id)

        try:
            saves_folder = os.path.join(folder, "saves")
            os.makedirs(saves_folder)

            for location_name in self.SAVE_LOCATIONS:
                os.makedirs(os.path.join(saves_folder, location_name))

            save_set = SaveSet(
                id=set_id,
                name=name,
                description=description,
                thumbnail=os.path.basename(thumbnail) if thumbnail else "",
                created=datetime.now().isoformat()
            )

            with open(
                    os.path.join(folder, "meta.json"),
                    "w",
                    encoding="utf-8"
            ) as f:
                json.dump(save_set.to_dict(), f, indent=4)
        except Exception:
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            raise

        return set_id

    def activate_set(self, set_id):
        """Restore a set's save files and mark it as the active set."""

        source = os.path.join(
            self.config["library_path"],
            set_id,
            "saves"
        )

        library = self.config["library_path"]

        targets = []
        for location_name, config_key in self.SAVE_LOCATIONS.items():
            target = self.config.get(config_key, "")
            if target:
                targets.append((
                    target,
                    os.path.join(source, location_name)
                ))

        metadata_backups = {}
        for folder in os.listdir(library):
            meta_file = os.path.join(library, folder, "meta.json")
            if os.path.isfile(meta_file):
                with open(meta_file, "rb") as f:
                    metadata_backups[meta_file] = f.read()

        with tempfile.TemporaryDirectory() as backup_root:
            target_backups = {}

            for index, (target, _) in enumerate(targets):
                if os.path.isdir(target):
                    backup = os.path.join(backup_root, str(index))
                    shutil.copytree(target, backup)
                    target_backups[target] = backup

            try:
                for target, location_source in targets:
                    os.makedirs(target, exist_ok=True)
                    self._remove_save_files(target)

                    if os.path.isdir(location_source):
                        self._copy_save_files(location_source, target)

                for folder in os.listdir(library):
                    meta_file = os.path.join(
                        library,
                        folder,
                        "meta.json"
                    )

                    if not os.path.isfile(meta_file):
                        continue

                    with open(meta_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)

                    metadata["active"] = folder == set_id

                    with open(meta_file, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=4)
            except Exception:
                for target, backup in target_backups.items():
                    shutil.rmtree(target)
                    shutil.copytree(backup, target)

                for target, _ in targets:
                    if target not in target_backups and os.path.isdir(target):
                        shutil.rmtree(target)

                for meta_file, contents in metadata_backups.items():
                    with open(meta_file, "wb") as f:
                        f.write(contents)

                raise

    @staticmethod
    def _remove_save_files(folder):
        """Remove only save files below a directory, preserving other data."""

        for root, _, files in os.walk(folder):
            for filename in files:
                if filename.lower().endswith(".save"):
                    os.remove(os.path.join(root, filename))

    @staticmethod
    def _copy_save_files(source, target):
        """Copy save files recursively while preserving their relative paths."""

        for root, _, files in os.walk(source):
            relative_root = os.path.relpath(root, source)
            target_root = target if relative_root == "." else os.path.join(
                target,
                relative_root
            )
            os.makedirs(target_root, exist_ok=True)

            for filename in files:
                if filename.lower().endswith(".save"):
                    shutil.copy2(
                        os.path.join(root, filename),
                        os.path.join(target_root, filename)
                    )

    def delete_set(self, set_id):
        """Delete a save-set directory from the configured library."""

        shutil.rmtree(
            os.path.join(
                self.config["library_path"],
                set_id
            )
        )

    def update_set_details(self, set_id, name, description, thumbnail):
        """Update a set's display metadata without changing its save files."""

        set_folder = os.path.join(
            self.config["library_path"],
            set_id
        )
        meta_file = os.path.join(set_folder, "meta.json")

        if not os.path.isfile(meta_file):
            return False

        with open(meta_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        metadata["name"] = name
        metadata["description"] = description
        metadata["thumbnail"] = os.path.basename(thumbnail) if thumbnail else ""

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        return True

    def clear_source_save_files(self):
        """Delete all *.save files across the configured source directories."""

        sources = []
        for config_key in self.SAVE_LOCATIONS.values():
            source = self.config.get(config_key, "")
            if source and os.path.isdir(source):
                sources.append(source)

        if not sources:
            return False

        for source in sources:
            self._remove_save_files(source)

        library = self.config.get("library_path", "")
        if os.path.isdir(library):
            for folder in os.listdir(library):
                meta_file = os.path.join(library, folder, "meta.json")
                if not os.path.isfile(meta_file):
                    continue

                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                except (OSError, json.JSONDecodeError):
                    continue

                metadata["active"] = False

                with open(meta_file, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=4)

        return True

    def update_active_set(self):
        """Update the active set, returning false when none is active."""

        active_sets = [
            save_set
            for save_set in self.get_all_sets()
            if save_set.active
        ]

        if not active_sets:
            return False

        return self.update_set(active_sets[0].id)

    def update_set(self, set_id):
        """Replace a set's snapshots and update its modified timestamp."""

        set_folder = os.path.join(
            self.config["library_path"],
            set_id
        )

        if not os.path.isdir(set_folder):
            return False

        with tempfile.TemporaryDirectory() as backup_root:
            backup = os.path.join(backup_root, "set")
            shutil.copytree(set_folder, backup)

            try:
                saves_folder = os.path.join(set_folder, "saves")
                os.makedirs(saves_folder, exist_ok=True)

                for location_name, config_key in self.SAVE_LOCATIONS.items():

                    source = self.config.get(config_key, "")

                    if not source or not os.path.isdir(source):
                        continue

                    location_folder = os.path.join(saves_folder, location_name)

                    if os.path.isdir(location_folder):
                        shutil.rmtree(location_folder)

                    shutil.copytree(source, location_folder)

                meta_file = os.path.join(set_folder, "meta.json")

                with open(meta_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                metadata["modified"] = datetime.now().isoformat()

                with open(meta_file, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=4)
            except Exception:
                shutil.rmtree(set_folder)
                shutil.copytree(backup, set_folder)
                raise

        return True