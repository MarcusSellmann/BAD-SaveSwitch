"""Runtime localization with gettext and built-in English fallbacks."""

import gettext
import os
from pathlib import Path


LOCALE_DIRECTORY = Path(__file__).resolve().parent.parent / "locales"
_translation = gettext.NullTranslations()
_current_language = "en"
BUILTIN_TRANSLATIONS = {
    "en": {
        "BAD Save Switch": "BAD Save Switch",
        "Thumbnail": "Thumbnail",
        "ID": "ID",
        "Name": "Name",
        "Beschreibung": "Description",
        "Erstellt": "Created",
        "Geändert": "Modified",
        "Aktiv": "Active",
        "Ja": "Yes",
        "Nein": "No",
        "Aus Spielstand erstellen": "Create from savegame",
        "Leerer Satz": "Empty Set",
        "Satz kopieren": "Copy set",
        "Kopie erstellen": "Create copy",
        "Satz aktivieren": "Activate set",
        "Satz synchronisieren": "Synchronize set",
        "Satz bearbeiten": "Edit set",
        "Löschen": "Delete",
        "Saves löschen": "Delete source saves",
        "Einstellungen": "Settings",
        "Fertig": "Done",
        "Speicherstand aktiviert.": "Save set activated.",
        "OK": "OK",
        "Wirklich löschen?": "Really delete?",
        "Alle .save-Dateien aus den Quellen löschen?": "Delete all .save files from the sources?",
        "Keine Quellordner gefunden.": "No source folders were found.",
        "Alle .save-Dateien im Quellordner wurden gelöscht.": "All .save files from the source folders were deleted.",
        "Hinweis": "Information",
        "Speicherstand aktualisiert.": "Save set updated.",
        "Speicherstand konnte nicht aktualisiert werden.": "The save set could not be updated.",
        "Kein aktiver Speicherstand vorhanden.": "No active save set exists.",
        "Bitte legen Sie die Speicherpfade in den Einstellungen fest.": "Please configure the save paths in Settings.",
        "Bitte legen Sie den Bibliothekspfad in den Einstellungen fest.": "Please configure the library path in Settings.",
        "Neuer Satz": "New Save Set",
        "Name:": "Name:",
        "Beschreibung:": "Description:",
        "Thumbnail:": "Thumbnail:",
        "Aktive Saves behalten": "Keep active saves",
        "Erstellen": "Create",
        "Fehler": "Error",
        "Name fehlt": "Name is required",
        "Das ausgewählte Thumbnail wurde nicht gefunden.": "The selected thumbnail was not found.",
        "Season1_2 lokales Verzeichnis": "Season1_2 local directory",
        "Season1_2 AppData-Verzeichnis": "Season1_2 AppData directory",
        "Season3 lokales Verzeichnis": "Season3 local directory",
        "Season3 AppData-Verzeichnis": "Season3 AppData directory",
        "Bibliothek": "Library",
        "Thumbnails": "Thumbnails",
        "Speichern": "Save"
    }
}


def set_language(language):
    """Select the active language and load its optional gettext catalog."""

    global _translation, _current_language

    _current_language = language
    os.environ["SAVEGAME_MANAGER_LANGUAGE"] = language

    _translation = gettext.translation(
        "savegame_manager",
        localedir=LOCALE_DIRECTORY,
        languages=[language],
        fallback=True
    )


def get_current_language():
    """Return the language code currently used by the UI."""

    return _current_language


def translate(message: str) -> str:
    """Translate a source message, falling back to the source text."""

    if _current_language in BUILTIN_TRANSLATIONS:
        return BUILTIN_TRANSLATIONS[_current_language].get(message, message)

    return str(_translation.gettext(message))


set_language(os.environ.get("SAVEGAME_MANAGER_LANGUAGE", "en"))
_ = translate
