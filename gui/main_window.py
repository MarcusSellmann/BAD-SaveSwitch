"""Main application window and save-set interaction workflows."""

import tkinter as tk
import os
import sys
from datetime import datetime

from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import font as tkfont

from core.save_manager import SaveManager
from core.config_manager import ConfigManager
from core.localization import _, get_current_language, set_language

from gui.settings_window import SettingsWindow
from gui.create_set_window import CreateSetWindow


class MainWindow(tk.Tk):
    """Display the save-set library and expose its primary actions."""

    THUMBNAIL_SIZE = (96, 64)
    TREE_IMAGE_INSET = 20
    TREE_ROW_HEIGHT = 72
    DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"
    DATETIME_SAMPLE = "00.00.0000 00:00:00"
    LANGUAGES = {
        "de": "🇩🇪 Deutsch",
        "en": "🇬🇧 English"
    }

    def __init__(self):
        """Initialize the main window, services, widgets, and initial rows."""

        super().__init__()

        self.title(
            _("BAD Save Switch")
        )

        application_directory = getattr(
            sys,
            "_MEIPASS",
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.iconbitmap(
            os.path.join(
                application_directory,
                "assets",
                "BAD_Save_Switch.ico"
            )
        )

        self.geometry(
            "1600x700"
        )

        self.config_data = ConfigManager.load()
        set_language(
            self.config_data.get(
                "language",
                get_current_language()
            )
        )

        self.manager = SaveManager(
            self.config_data
        )

        self.thumbnail_images = {}
        self.active_set_ids = set()

        self.build()

        self.refresh()

    def build(self):
        """Construct the list, controls, language selector, and bindings."""

        style = ttk.Style(self)
        style.configure(
            "Treeview",
            rowheight=self.TREE_ROW_HEIGHT
        )

        columns = (
            "id",
            "name",
            "description",
            "created",
            "modified",
            "active"
        )

        headings = {
            "id": _("ID"),
            "name": _("Name"),
            "description": _("Beschreibung"),
            "created": _("Erstellt"),
            "modified": _("Geändert"),
            "active": _("Aktiv")
        }

        widths = {
            "id": 150,
            "name": 180,
            "description": 240,
            "created": tkfont.nametofont("TkDefaultFont").measure(
                self.DATETIME_SAMPLE
            ) + 12,
            "modified": tkfont.nametofont("TkDefaultFont").measure(
                self.DATETIME_SAMPLE
            ) + 12,
            "active": 70
        }

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show=("tree", "headings")
        )

        self.tree.heading("#0", text=_("Thumbnail"))
        self.tree.column(
            "#0",
            width=self.THUMBNAIL_SIZE[0],
            minwidth=self.THUMBNAIL_SIZE[0],
            stretch=False,
            anchor="w"
        )

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(10, 0)
        )

        scrollbar = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(xscrollcommand=scrollbar.set)
        scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=10
        )

        self.tree.bind(
            "<Double-1>",
            self.double_click_activate
        )
        self.tree.bind(
            "<<TreeviewSelect>>",
            self.update_sync_action_state
        )

        self.tree.bind(
            "<Button-3>",
            self.show_context_menu
        )

        buttons = ttk.Frame(self)
        self.action_buttons = {}

        buttons.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=10,
            pady=10
        )

        self.action_buttons["new"] = ttk.Button(
            buttons,
            text=_("Aus Spielstand erstellen"),
            command=self.new_set
        )
        self.action_buttons["new"].pack(side="left", padx=5)

        self.action_buttons["activate"] = ttk.Button(
            buttons,
            text=_("Satz aktivieren"),
            command=self.activate
        )
        self.action_buttons["activate"].pack(side="left", padx=5)

        self.action_buttons["update"] = ttk.Button(
            buttons,
            text=_("Satz synchronisieren"),
            command=self.update_selected_set,
            state="disabled"
        )
        self.action_buttons["update"].pack(side="left", padx=5)

        self.action_buttons["delete"] = ttk.Button(
            buttons,
            text=_("Löschen"),
            command=self.delete
        )
        self.action_buttons["delete"].pack(side="left", padx=5)

        ttk.Separator(
            buttons,
            orient="vertical"
        ).pack(
            side="left",
            fill="y",
            padx=8,
            pady=4
        )

        self.action_buttons["clear_sources"] = ttk.Button(
            buttons,
            text=_("Saves löschen"),
            command=self.clear_source_save_files
        )
        self.action_buttons["clear_sources"].pack(side="left", padx=5)

        self.action_buttons["new_empty"] = ttk.Button(
            buttons,
            text=_("Leerer Satz"),
            command=self.new_empty_set
        )
        self.action_buttons["new_empty"].pack(side="left", padx=5)

        self.action_buttons["copy"] = ttk.Button(
            buttons,
            text=_("Satz kopieren"),
            command=self.copy_selected_set,
            state="disabled"
        )
        self.action_buttons["copy"].pack(side="left", padx=5)

        self.action_buttons["settings"] = ttk.Button(
            buttons,
            text=_("Einstellungen"),
            command=self.settings
        )
        self.action_buttons["settings"].pack(side="right", padx=5)

        self.language_var = tk.StringVar(
            value=self.LANGUAGES.get(
                get_current_language(),
                self.LANGUAGES["de"]
            )
        )

        language_dropdown = ttk.Combobox(
            buttons,
            textvariable=self.language_var,
            values=list(self.LANGUAGES.values()),
            state="readonly",
            width=16
        )

        language_dropdown.pack(side="right", padx=5)
        language_dropdown.bind(
            "<<ComboboxSelected>>",
            self.change_language
        )

    def refresh(self):
        """Reload all save-set rows and their thumbnail images."""

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.thumbnail_images.clear()

        save_sets = self.manager.get_all_sets()
        self.active_set_ids = {
            save.id
            for save in save_sets
            if save.active
        }

        for save in save_sets:

            thumbnail = self.load_thumbnail(save.thumbnail)

            self.tree.insert(
                "",
                "end",
                iid=save.id,
                image=thumbnail,
                values=(
                    save.id,
                    save.name,
                    save.description,
                    self.format_datetime(save.created),
                    self.format_datetime(save.modified),
                    _("Ja") if save.active else _("Nein")
                )
            )

        self.update_sync_action_state()

    def update_sync_action_state(self, event=None):
        """Update action availability based on the selected save set."""

        selected = self.tree.selection()
        is_active = bool(
            selected
            and selected[0] in self.active_set_ids
        )
        self.action_buttons["update"].state(
            ["!disabled"] if is_active else ["disabled"]
        )
        self.action_buttons["copy"].state(
            ["!disabled"] if selected else ["disabled"]
        )

    def load_thumbnail(self, thumbnail_name):
        """Load and scale a set thumbnail for use by the Treeview."""

        thumbnail_directory = self.config_data.get("thumbnail_path", "")
        thumbnail_path = os.path.join(
            thumbnail_directory,
            os.path.basename(thumbnail_name)
        ) if thumbnail_name else ""

        if not os.path.isfile(thumbnail_path):
            thumbnail_path = os.path.join(
                thumbnail_directory,
                "default.png"
            )

        if not os.path.isfile(thumbnail_path):
            return ""

        if thumbnail_path in self.thumbnail_images:
            return self.thumbnail_images[thumbnail_path]

        try:
            image = Image.open(thumbnail_path)
            image.thumbnail(self.THUMBNAIL_SIZE)
            if image.height > image.width:
                centered_image = Image.new(
                    "RGBA",
                    self.THUMBNAIL_SIZE,
                    (0, 0, 0, 0)
                )
                image = image.convert("RGBA")
                image_left = max(
                    0,
                    (self.THUMBNAIL_SIZE[0] - image.width) // 2
                    - self.TREE_IMAGE_INSET
                )
                centered_image.paste(
                    image,
                    (
                        image_left,
                        (self.THUMBNAIL_SIZE[1] - image.height) // 2
                    ),
                    image
                )
                image = centered_image
            photo = ImageTk.PhotoImage(image)
        except (OSError, ValueError):
            return ""

        self.thumbnail_images[thumbnail_path] = photo
        return photo

    @staticmethod
    def format_datetime(value):
        """Format an ISO timestamp for display, preserving invalid text."""

        if not value:
            return ""

        try:
            date_time = datetime.fromisoformat(value)
        except ValueError:
            return value

        return date_time.strftime(MainWindow.DATETIME_FORMAT)

    def new_set(self):
        """Open the creation form and persist its submitted save set."""

        if not self.ensure_paths_configured():
            return

        win = CreateSetWindow(
            self,
            self.config_data
        )

        self.wait_window(win)

        if not win.result:
            return

        self.manager.create_set(
            win.result["name"],
            win.result["thumbnail"],
            win.result["keep"],
            description=win.result["description"]
        )

        self.refresh()

    def new_empty_set(self):
        """Create a save set without copying files from source directories."""

        if not self.ensure_library_configured():
            return

        win = CreateSetWindow(
            self,
            self.config_data,
            show_keep_option=False
        )

        self.wait_window(win)

        if not win.result:
            return

        self.manager.create_empty_set(
            win.result["name"],
            win.result["thumbnail"],
            description=win.result["description"]
        )

        self.refresh()

    def copy_selected_set(self, set_id=None):
        """Duplicate the selected set and its saved files after confirmation."""

        if not self.ensure_library_configured():
            return

        selected = self.tree.selection()
        set_id = set_id or (selected[0] if selected else None)
        if not set_id:
            return

        save_set = next(
            (
                save_set
                for save_set in self.manager.get_all_sets()
                if save_set.id == set_id
            ),
            None
        )

        if not save_set:
            return

        win = CreateSetWindow(
            self,
            self.config_data,
            show_keep_option=False,
            save_set=save_set,
            copy_mode=True
        )

        self.wait_window(win)

        if not win.result:
            return

        self.manager.copy_set(
            save_set.id,
            win.result["name"],
            win.result["description"],
            win.result["thumbnail"]
        )
        self.refresh()

    def double_click_activate(self, event):
        """Activate the row under a double-click."""

        item = self.tree.identify_row(event.y)

        if not item:
            return

        self.tree.selection_set(item)
        self.activate()

    def show_context_menu(self, event):
        """Show row actions at the location of a right-click."""

        item = self.tree.identify_row(event.y)

        if not item:
            return

        self.tree.selection_set(item)
        self.tree.focus(item)

        menu = tk.Menu(self, tearoff=False)
        menu.add_command(
            label=_("Satz aktivieren"),
            command=self.activate
        )
        menu.add_command(
            label=_("Satz synchronisieren"),
            command=lambda set_id=item: self.update_set(set_id),
            state=tk.NORMAL if item in self.active_set_ids else tk.DISABLED
        )
        menu.add_command(
            label=_("Satz bearbeiten"),
            command=lambda set_id=item: self.edit_set(set_id)
        )
        menu.add_command(
            label=_("Satz kopieren"),
            command=lambda set_id=item: self.copy_selected_set(set_id)
        )
        menu.add_separator()
        menu.add_command(
            label=_("Löschen"),
            command=self.delete
        )

        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()

    def edit_set(self, set_id):
        """Edit a save set's name, description, and thumbnail."""

        save_set = next(
            (
                save_set
                for save_set in self.manager.get_all_sets()
                if save_set.id == set_id
            ),
            None
        )

        if not save_set:
            return

        win = CreateSetWindow(
            self,
            self.config_data,
            show_keep_option=False,
            save_set=save_set
        )

        self.wait_window(win)

        if not win.result:
            return

        self.manager.update_set_details(
            set_id,
            win.result["name"],
            win.result["description"],
            win.result["thumbnail"]
        )
        self.refresh()

    def activate(self):
        """Activate the selected row and show the centered result message."""

        if not self.ensure_paths_configured():
            return

        selected = self.tree.selection()

        if not selected:
            return

        self.manager.activate_set(
            selected[0]
        )

        self.refresh()

        self.show_message(
            _("Fertig"),
            _("Speicherstand aktiviert.")
        )

    def update_selected_set(self):
        """Synchronize the selected set only when it is active."""

        selected = self.tree.selection()
        if not selected or selected[0] not in self.active_set_ids:
            return

        self.update_set(selected[0])

    def update_set(self, set_id):
        """Synchronize a selected active set from current source saves."""

        if (
                set_id not in self.active_set_ids
                or set_id not in self.tree.selection()
        ):
            return

        if not self.ensure_paths_configured():
            return

        if not self.manager.update_set(set_id):
            self.show_message(
                _("Hinweis"),
                _("Speicherstand konnte nicht aktualisiert werden.")
            )
            return

        self.refresh()
        self.show_message(
            _("Fertig"),
            _("Speicherstand aktualisiert.")
        )

    def show_message(self, title, message):
        """Show a modal message centered over the main window."""

        popup = tk.Toplevel(self)
        popup.title(title)
        popup.transient(self)

        ttk.Label(
            popup,
            text=message
        ).pack(padx=30, pady=(20, 10))

        ttk.Button(
            popup,
            text=_("OK"),
            command=popup.destroy
        ).pack(pady=(0, 20))

        popup.update_idletasks()

        x = self.winfo_rootx() + (
            self.winfo_width() - popup.winfo_width()
        ) // 2
        y = self.winfo_rooty() + (
            self.winfo_height() - popup.winfo_height()
        ) // 2

        popup.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        popup.grab_set()
        popup.focus_force()
        self.wait_window(popup)

    def delete(self):
        """Confirm and delete the selected save set."""

        if not self.ensure_paths_configured():
            return

        selected = self.tree.selection()

        if not selected:
            return

        if self.confirm_delete():

            self.manager.delete_set(
                selected[0]
            )

            self.refresh()

    def clear_source_save_files(self):
        """Delete all .save files from the configured source folders."""

        if not self.ensure_paths_configured():
            return

        if not self.confirm_clear_sources():
            return

        if not self.manager.clear_source_save_files():
            self.show_message(
                _("Hinweis"),
                _("Keine Quellordner gefunden.")
            )
            return

        self.refresh()
        self.show_message(
            _("Fertig"),
            _("Alle .save-Dateien im Quellordner wurden gelöscht.")
        )

    def ensure_paths_configured(self):
        """Require a usable library and source directory before actions."""

        library_path = self.config_data.get("library_path", "").strip()
        save_paths = [
            self.config_data.get(config_key, "").strip()
            for config_key in SaveManager.SAVE_LOCATIONS.values()
        ]

        library_valid = bool(library_path) and (
            not os.path.exists(library_path)
            or os.path.isdir(library_path)
        )
        source_valid = any(
            os.path.isdir(save_path)
            for save_path in save_paths
            if save_path
        )

        if library_valid and source_valid:
            return True

        self.show_message(
            _("Hinweis"),
            _("Bitte legen Sie die Speicherpfade in den Einstellungen fest.")
        )
        self.settings()
        return False

    def ensure_library_configured(self):
        """Require only a usable library path for empty-set creation."""

        library_path = self.config_data.get("library_path", "").strip()
        if library_path and (
                not os.path.exists(library_path)
                or os.path.isdir(library_path)
        ):
            return True

        self.show_message(
            _("Hinweis"),
            _("Bitte legen Sie den Bibliothekspfad in den Einstellungen fest.")
        )
        self.settings()
        return False

    def confirm_delete(self):
        """Return the user's answer from a centered delete confirmation."""

        popup = tk.Toplevel(self)
        popup.title(_("Löschen"))
        popup.transient(self)

        result = tk.BooleanVar(popup, value=False)

        ttk.Label(
            popup,
            text=_("Wirklich löschen?")
        ).pack(padx=30, pady=(20, 10))

        buttons = ttk.Frame(popup)
        buttons.pack(pady=(0, 20))

        ttk.Button(
            buttons,
            text=_("Ja"),
            command=lambda: self.finish_confirmation(popup, result, True)
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons,
            text=_("Nein"),
            command=lambda: self.finish_confirmation(popup, result, False)
        ).pack(side="left", padx=5)

        popup.update_idletasks()

        x = self.winfo_rootx() + (
            self.winfo_width() - popup.winfo_width()
        ) // 2
        y = self.winfo_rooty() + (
            self.winfo_height() - popup.winfo_height()
        ) // 2

        popup.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        popup.grab_set()
        popup.focus_force()
        self.wait_window(popup)

        return result.get()

    def confirm_clear_sources(self):
        """Confirm the deletion of .save files from all configured sources."""

        popup = tk.Toplevel(self)
        popup.title(_("Saves löschen"))
        popup.transient(self)

        result = tk.BooleanVar(popup, value=False)

        ttk.Label(
            popup,
            text=_("Alle .save-Dateien aus den Quellen löschen?")
        ).pack(padx=30, pady=(20, 10))

        buttons = ttk.Frame(popup)
        buttons.pack(pady=(0, 20))

        ttk.Button(
            buttons,
            text=_("Ja"),
            command=lambda: self.finish_confirmation(popup, result, True)
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons,
            text=_("Nein"),
            command=lambda: self.finish_confirmation(popup, result, False)
        ).pack(side="left", padx=5)

        popup.update_idletasks()

        x = self.winfo_rootx() + (
            self.winfo_width() - popup.winfo_width()
        ) // 2
        y = self.winfo_rooty() + (
            self.winfo_height() - popup.winfo_height()
        ) // 2

        popup.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        popup.grab_set()
        popup.focus_force()
        self.wait_window(popup)

        return result.get()

    @staticmethod
    def finish_confirmation(popup, result, confirmed):
        """Store a confirmation result and close its modal popup."""

        result.set(confirmed)
        popup.destroy()

    def settings(self):
        """Open the centered settings window."""

        SettingsWindow(
            self,
            self.config_data
        )

    def change_language(self, event=None):
        """Persist the selected language and refresh visible main-window text."""

        selected_label = self.language_var.get()
        selected_language = next(
            language
            for language, label in self.LANGUAGES.items()
            if label == selected_label
        )

        set_language(selected_language)
        self.config_data["language"] = selected_language
        ConfigManager.save(self.config_data)
        self.refresh_language()

    def refresh_language(self):
        """Update headings, buttons, title, and translated active-state values."""

        self.title(_("BAD Save Switch"))

        headings = {
            "id": _("ID"),
            "name": _("Name"),
            "description": _("Beschreibung"),
            "created": _("Erstellt"),
            "modified": _("Geändert"),
            "active": _("Aktiv")
        }

        for column, heading in headings.items():
            self.tree.heading(column, text=heading)

        self.tree.heading("#0", text=_("Thumbnail"))

        button_labels = {
            "new": _("Aus Spielstand erstellen"),
            "activate": _("Satz aktivieren"),
            "update": _("Satz synchronisieren"),
            "delete": _("Löschen"),
            "clear_sources": _("Saves löschen"),
            "new_empty": _("Leerer Satz"),
            "copy": _("Satz kopieren"),
            "settings": _("Einstellungen")
        }

        for name, label in button_labels.items():
            self.action_buttons[name].configure(text=label)

        self.refresh()