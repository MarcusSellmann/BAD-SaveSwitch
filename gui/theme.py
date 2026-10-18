"""Shared dark color palette and ttk styles for application windows."""

import tkinter as tk
from tkinter import ttk

from core.localization import _


BACKGROUND = "#242830"
FOREGROUND = "#F4F6F8"
MUTED_FOREGROUND = "#A4ACB8"
ACCENT = "#31B7C7"
FIELD_BACKGROUND = "#303641"
CONTROL_BACKGROUND = "#343B46"
TREE_BACKGROUND = "#2D333D"
BORDER = "#454D59"
DISABLED_BACKGROUND = "#2A2F37"


def apply_theme(root):
    """Apply the application palette to the root and shared ttk widgets."""

    root.configure(background=BACKGROUND)
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        ".",
        background=BACKGROUND,
        foreground=FOREGROUND
    )
    style.configure("TFrame", background=BACKGROUND)
    style.configure(
        "TLabel",
        background=BACKGROUND,
        foreground=FOREGROUND
    )
    style.configure(
        "TButton",
        background=CONTROL_BACKGROUND,
        foreground=FOREGROUND,
        bordercolor=BORDER,
        lightcolor=CONTROL_BACKGROUND,
        darkcolor=CONTROL_BACKGROUND,
        padding=(10, 6)
    )
    style.map(
        "TButton",
        background=[
            ("disabled", DISABLED_BACKGROUND),
            ("pressed", "#208B98"),
            ("active", ACCENT)
        ],
        foreground=[
            ("disabled", MUTED_FOREGROUND),
            ("active", BACKGROUND)
        ]
    )
    style.configure(
        "TEntry",
        fieldbackground=FIELD_BACKGROUND,
        foreground=FOREGROUND,
        insertcolor=FOREGROUND,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER
    )
    style.configure(
        "TCombobox",
        fieldbackground=FIELD_BACKGROUND,
        background=CONTROL_BACKGROUND,
        foreground=FOREGROUND,
        arrowcolor=FOREGROUND,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER
    )
    style.map(
        "TCombobox",
        fieldbackground=[
            ("readonly", FIELD_BACKGROUND),
            ("disabled", DISABLED_BACKGROUND)
        ],
        foreground=[
            ("readonly", FOREGROUND),
            ("disabled", MUTED_FOREGROUND)
        ],
        selectbackground=[("readonly", FIELD_BACKGROUND)],
        selectforeground=[("readonly", FOREGROUND)]
    )
    style.configure(
        "TCheckbutton",
        background=BACKGROUND,
        foreground=FOREGROUND
    )
    style.map(
        "TCheckbutton",
        background=[("active", BACKGROUND)],
        foreground=[("disabled", MUTED_FOREGROUND)]
    )
    style.configure(
        "Treeview",
        background=TREE_BACKGROUND,
        fieldbackground=TREE_BACKGROUND,
        foreground=FOREGROUND,
        bordercolor=BORDER
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", BACKGROUND)]
    )
    style.configure(
        "Treeview.Heading",
        background=CONTROL_BACKGROUND,
        foreground=FOREGROUND,
        bordercolor=BORDER,
        relief="flat"
    )
    style.map(
        "Treeview.Heading",
        background=[("active", ACCENT)],
        foreground=[("active", BACKGROUND)]
    )
    style.configure(
        "TScrollbar",
        background=CONTROL_BACKGROUND,
        troughcolor=BACKGROUND,
        bordercolor=BACKGROUND,
        arrowcolor=FOREGROUND
    )
    style.configure("TSeparator", background=BORDER)

    root.option_add("*TCombobox*Listbox.background", FIELD_BACKGROUND)
    root.option_add("*TCombobox*Listbox.foreground", FOREGROUND)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", BACKGROUND)


def show_themed_message(parent: tk.Misc, title: str, message: str):
    """Show a modal message dialog using the shared application palette."""

    popup = tk.Toplevel(parent)
    popup.configure(background=BACKGROUND)
    popup.title(title)
    popup.transient(parent.winfo_toplevel())

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
    x = parent.winfo_rootx() + (
        parent.winfo_width() - popup.winfo_width()
    ) // 2
    y = parent.winfo_rooty() + (
        parent.winfo_height() - popup.winfo_height()
    ) // 2
    popup.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    popup.grab_set()
    popup.focus_force()
    parent.wait_window(popup)
