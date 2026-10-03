# BAD Save Switch

BAD Save Switch is a Tkinter application for Being a DIK that makes it easy to store and switch between multiple game save sets across the configured Season 1/2 and Season 3 save locations. It lets you preserve different playthroughs, experiment with choices without overwriting progress, and quickly return to an earlier point in the story. Save sets are organized with names, descriptions, and thumbnails, helping you identify the right playthrough at a glance while keeping unrelated files in the live save directories protected.

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

## Building for Windows

Run `build_windows.bat` from the repository or by double-clicking it. The script installs the app and build dependencies, then creates a standalone GUI executable at `dist\BAD-SaveSwitch.exe` with the BAD Save Switch icon. The first launch creates `config.json` beside the executable; configure the save, library, and thumbnail paths in Settings.

To build manually, install `requirements.txt` and `requirements-build.txt`, then run:

```text
python -m PyInstaller --noconfirm --clean --windowed --onefile --icon=assets\BAD_Save_Switch.ico --add-data "assets\BAD_Save_Switch.ico;assets" --name BAD-SaveSwitch main.py
```

## Configuration

Source runs read `config.json` from the current working directory. Packaged executables read and write it beside the `.exe`. The settings window writes the same file. The main fields are:

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

- **Create from savegame** creates a snapshot from the configured source directories. The checkbox controls whether source `*.save` files are retained.
- **Empty Set** creates the standard save-set folder structure and metadata without copying any files.
- **Activate set** restores a set's save files and marks exactly one set active.
- **Synchronize set** replaces the selected set's snapshots with current source contents and updates `modified`. It is available only when the selected set is active.
- **Delete** removes the selected set after confirmation.
- **Delete source saves** removes all `*.save` files from the configured source directories after confirmation.
- **Double-click** activates a set.
- **Right-click** opens activate, synchronize, edit, and delete actions for a row. Synchronize is disabled for inactive sets.
- **Language dropdown** switches between German and English and persists the choice.

Filesystem operations use backups and rollback where changes could otherwise leave live files or metadata partially modified.

## Project files

- `config.json`: Runtime paths and language selection. It is user-specific and should not be hard-coded for another machine. In a packaged executable, it is stored beside the `.exe`.
- `README.md`: Project setup, configuration, storage layout, workflows, and file map.
- `main.py`: Application entry point.
- `requirements.txt`: Python package requirements.
- `requirements-build.txt`: Windows executable build dependencies.
- `build_windows.bat`: Builds the standalone Windows executable.
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

## Donate

If BAD Save Switch is useful to you, you can support its development through [PayPal](https://www.paypal.com/donate/?hosted_button_id=CT9NQZE8DTKKJ).
