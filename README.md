# BAD Save Switch

BAD Save Switch is a Tkinter application for storing and switching game save sets across the configured Season 1/2 and Season 3 save locations.

## Requirements

- Python 3.9 or newer
- Pillow
- A Windows environment is recommended because the default workflow targets Windows local and AppData directories.

Install the dependency with:

```text
python -m pip install -r requirements.txt
```

## Running

Run the launcher from the repository root:

```text
python main.py
```

The VS Code debugger can use `.vscode/launch.json` to launch the same file.

## Configuration

The application reads `config.json` from the current working directory. The settings window writes the same file. The main fields are:

| Key | Purpose |
| --- | --- |
| `Season1_2_local_directory` | Season 1/2 local save directory |
| `Season1_2_appdata_directory` | Season 1/2 AppData save directory |
| `Season3_local_directory` | Season 3 local save directory |
| `Season3_appdata_directory` | Season 3 AppData save directory |
| `library_path` | Root directory containing save-set folders |
| `thumbnail_path` | Directory containing selectable thumbnails |
| `language` | Current UI language, currently `de` or `en` |

At least one existing save-source directory and a usable library path are required before save-set actions can run. The settings button remains available when paths are missing.

## Save-set storage

Each save set is stored below `library_path` using a generated UUID:

```text
library_path/
  <set-id>/
    meta.json
    saves/
      Season1_2_local/
      Season1_2_appdata/
      Season3_local/
      Season3_appdata/
```

`meta.json` stores the set ID, name, description, thumbnail filename, created timestamp, modified timestamp, and active state. Thumbnail images remain in `thumbnail_path`; the metadata stores only the selected filename. The UI falls back to `default.png` when the selected image is unavailable. Save snapshots preserve the configured source directory structure, while activation transfers only `*.save` files to protect unrelated files in the live directories.

## Main workflows

- **New** creates a snapshot from the configured source directories. The checkbox controls whether source `*.save` files are retained.
- **Activate** restores a set's save files and marks exactly one set active.
- **Update** replaces the selected or active set's snapshots with current source contents and updates `modified`.
- **Delete** removes the selected set after confirmation.
- **Delete source saves** removes all `*.save` files from the configured source directories after confirmation.
- **Double-click** activates a set.
- **Right-click** opens activate, update, and delete actions for a row.
- **Language dropdown** switches between German and English and persists the choice.

Filesystem operations use backups and rollback where changes could otherwise leave live files or metadata partially modified.

## Project files

- `config.json`: Runtime paths and language selection. It is user-specific and should not be hard-coded for another machine.
- `README.md`: Project setup, configuration, storage layout, workflows, and file map.
- `main.py`: Application entry point.
- `requirements.txt`: Python package requirements.
- `core/config_manager.py`: Loads and saves the JSON configuration.
- `core/localization.py`: Runtime language selection and gettext/built-in translations.
- `core/save_manager.py`: Save-set discovery, creation, activation, update, deletion, source-save cleanup, backup, and rollback logic.
- `data/models.py`: `SaveSet` dataclass and metadata serialization.
- `gui/main_window.py`: Main list, thumbnails, action buttons, context menu, language selector, and centered dialogs.
- `gui/create_set_window.py`: New save-set form and thumbnail validation.
- `gui/settings_window.py`: Directory and thumbnail-path configuration form.
- `example_meta.json`: Example metadata shape for a save set.

## Development checks

Compile the package with:

```text
python -m compileall -q .
```

The project currently has no automated test files. Temporary-directory smoke tests should cover create, activate, update, delete, rollback, malformed metadata, and invalid configuration paths when changing filesystem behavior.
