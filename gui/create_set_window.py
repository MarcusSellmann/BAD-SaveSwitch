"""Dialog for creating a named save-set snapshot."""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from core.localization import _


class CreateSetWindow(tk.Toplevel):
    """Collect save-set metadata and creation options from the user."""

    def __init__(
            self,
            parent,
            config,
            show_keep_option=True,
            save_set=None,
            copy_mode=False
        ):
        """Initialize the form using configured thumbnail defaults."""

        super().__init__(parent)

        self.copy_mode = copy_mode
        self.title(
            _("Satz kopieren") if copy_mode
            else _("Satz bearbeiten") if save_set
            else _("Neuer Satz")
        )
        self.geometry("500x300")
        self.transient(parent)
        self.main_window = parent

        self.result = None
        self.config_data = config
        self.save_set = save_set
        self.show_keep_option = show_keep_option and save_set is None

        self.name_var = tk.StringVar(
            value=(
                f"{save_set.name} - Kopie"
                if save_set and copy_mode
                else save_set.name if save_set else ""
            )
        )
        self.description_var = tk.StringVar(
            value=save_set.description if save_set else ""
        )

        self.keep_var = tk.BooleanVar(
            value=True
        )

        thumbnail_path = config.get("thumbnail_path", "")
        default_thumbnail = os.path.join(
            thumbnail_path,
            "default.png"
        )

        self.thumb_var = tk.StringVar(
            value=(
                save_set.thumbnail
                if save_set
                else "default.png" if os.path.isfile(default_thumbnail) else ""
            )
        )

        self.build()
        self.update_idletasks()
        self.geometry(f"500x{self.winfo_reqheight()}")
        self.center_on_parent(parent)

    def center_on_parent(self, parent):
        """Position the dialog at the center of its parent window."""

        self.update_idletasks()

        x = parent.winfo_rootx() + (
            parent.winfo_width() - self.winfo_width()
        ) // 2
        y = parent.winfo_rooty() + (
            parent.winfo_height() - self.winfo_height()
        ) // 2

        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def build(self):
        """Build metadata, thumbnail, retention, and submit controls."""

        ttk.Label(
            self,
            text=_("Name:")
        ).pack(pady=5)

        ttk.Entry(
            self,
            textvariable=self.name_var
        ).pack(fill="x", padx=20)

        ttk.Label(
            self,
            text=_("Beschreibung:")
        ).pack(pady=5)

        ttk.Entry(
            self,
            textvariable=self.description_var
        ).pack(fill="x", padx=20)

        ttk.Label(
            self,
            text=_("Thumbnail:")
        ).pack(pady=5)

        thumbs = []

        thumb_path = self.config_data.get(
            "thumbnail_path",
            ""
        )

        if os.path.exists(thumb_path):

            thumbs = [
                f
                for f in os.listdir(thumb_path)
                if f.lower().endswith(
                    (
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".webp"
                    )
                )
            ]

        combo = ttk.Combobox(
            self,
            textvariable=self.thumb_var,
            values=thumbs
        )

        combo.pack(
            fill="x",
            padx=20
        )

        if self.show_keep_option:
            ttk.Checkbutton(
                self,
                text=_("Aktive Saves behalten"),
                variable=self.keep_var
            ).pack(
                pady=15
            )

        ttk.Button(
            self,
            text=(
                _("Kopie erstellen") if self.copy_mode
                else _("Speichern") if self.save_set
                else _("Erstellen")
            ),
            command=self.create
        ).pack(pady=(12, 8))

    def create(self):
        """Validate the form and expose its values to the main window."""

        if not self.name_var.get():

            messagebox.showerror(
                _("Fehler"),
                _("Name fehlt"),
                parent=self.main_window
            )

            return

        thumb = ""

        if self.thumb_var.get():

            thumb = os.path.join(
                self.config_data.get("thumbnail_path", ""),
                self.thumb_var.get()
            )

            if not os.path.isfile(thumb) and not (
                    self.save_set
                    and self.thumb_var.get() == self.save_set.thumbnail
            ):
                messagebox.showerror(
                    _("Fehler"),
                    _("Das ausgewählte Thumbnail wurde nicht gefunden."),
                    parent=self.main_window
                )
                return

        self.result = {
            "name": self.name_var.get(),
            "description": self.description_var.get(),
            "thumbnail": thumb or self.thumb_var.get(),
            "keep": self.keep_var.get()
        }

        self.destroy()