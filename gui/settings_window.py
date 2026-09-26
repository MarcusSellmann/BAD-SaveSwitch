"""Dialog for configuring save, library, and thumbnail directories."""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from core.config_manager import ConfigManager
from core.localization import _


class SettingsWindow(tk.Toplevel):
    """Edit application paths and persist them through ConfigManager."""

    def __init__(self, parent, config):
        """Initialize path variables and build the centered settings form."""

        super().__init__(parent)

        self.title(_("Einstellungen"))
        self.geometry("700x420")
        self.transient(parent)

        self.config_data = config

        self.season1_2_local_dir_var = tk.StringVar(
            value=config.get("Season1_2_local_directory", "")
        )

        self.season1_2_appdata_dir_var = tk.StringVar(
            value=config.get("Season1_2_appdata_directory", "")
        )

        self.season3_local_dir_var = tk.StringVar(
            value=config.get("Season3_local_directory", "")
        )

        self.season3_appdata_dir_var = tk.StringVar(
            value=config.get("Season3_appdata_directory", "")
        )

        self.library_var = tk.StringVar(
            value=config["library_path"]
        )

        self.thumb_var = tk.StringVar(
            value=config["thumbnail_path"]
        )

        self.build()
        self.center_on_parent(parent)

    def center_on_parent(self, parent):
        """Position the settings dialog at the center of its parent."""

        self.update_idletasks()

        x = parent.winfo_rootx() + (
            parent.winfo_width() - self.winfo_width()
        ) // 2
        y = parent.winfo_rooty() + (
            parent.winfo_height() - self.winfo_height()
        ) // 2

        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def browse(self, var):
        """Open a directory chooser and restore focus to this dialog."""

        path = filedialog.askdirectory(
            parent=self
        )

        self.lift()
        self.focus_force()

        if path:
            var.set(path)

    def build(self):
        """Build entries and browse/save controls for all configurable paths."""

        labels = [
            (_("Season1_2 lokales Verzeichnis"), self.season1_2_local_dir_var),
            (_("Season1_2 AppData-Verzeichnis"), self.season1_2_appdata_dir_var),
            (_("Season3 lokales Verzeichnis"), self.season3_local_dir_var),
            (_("Season3 AppData-Verzeichnis"), self.season3_appdata_dir_var),
            (_("Bibliothek"), self.library_var),
            (_("Thumbnails"), self.thumb_var)
        ]

        for row, (text, var) in enumerate(labels):

            ttk.Label(
                self,
                text=text
            ).grid(row=row, column=0, padx=10, pady=10)

            ttk.Entry(
                self,
                textvariable=var,
                width=60
            ).grid(row=row, column=1)

            ttk.Button(
                self,
                text=_("..."),
                command=lambda v=var:
                self.browse(v)
            ).grid(row=row, column=2)

        ttk.Button(
            self,
            text=_("Speichern"),
            command=self.save
        ).grid(row=7, column=1, pady=15)

    def save(self):
        """Copy form values into the shared config and save them to disk."""

        self.config_data["Season1_2_local_directory"] = self.season1_2_local_dir_var.get()
        self.config_data["Season1_2_appdata_directory"] = self.season1_2_appdata_dir_var.get()
        self.config_data["Season3_local_directory"] = self.season3_local_dir_var.get()
        self.config_data["Season3_appdata_directory"] = self.season3_appdata_dir_var.get()
        self.config_data["library_path"] = self.library_var.get()
        self.config_data["thumbnail_path"] = self.thumb_var.get()

        ConfigManager.save(self.config_data)

        self.destroy()