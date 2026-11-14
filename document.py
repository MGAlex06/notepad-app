import tkinter as tk
from pathlib import Path

import file_io


class Document:
    """Un document deschis: zona de text, bara de derulare și datele fișierului.

    Ține tot ce aparține unui singur fișier, ca mai târziu să putem avea
    mai multe documente deschise în același timp.
    """

    def __init__(self, parent):
        # Un Frame (o „cutie”) care ține împreună zona de text și bara de derulare
        self.frame = tk.Frame(parent)

        # Bara de derulare verticală, lipită de marginea din dreapta
        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Zona de text, care ocupă tot restul.
        # undo=True pornește Ctrl+Z (anulează) și Ctrl+Y (refă).
        self.text_area = tk.Text(
            self.frame, yscrollcommand=self.scrollbar.set, undo=True
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Legăm bara de derulare de zona de text
        self.scrollbar.config(command=self.text_area.yview)

        # Selecția rămâne colorată chiar și când focusul e în altă fereastră
        # (de exemplu în fereastra de căutare)
        self.text_area.config(
            inactiveselectbackground=self.text_area.cget("selectbackground")
        )

        # Fișierul documentului (None = încă nesalvat) și terminația lui de linie
        self.path = None
        self.newline = "\r\n"
        # Codificarea cu care salvăm. E o variabilă Tkinter, ca butoanele radio
        # din meniul Codificare să arate și să schimbe singure valoarea ei.
        self.encoding = tk.StringVar(master=parent, value=file_io.DEFAULT_ENCODING)

    def display_name(self):
        """Numele afișat în titlul ferestrei."""
        if self.path is None:
            return "Fără titlu"
        return self.path.name

    def get_text(self):
        """Tot textul din document."""
        # "end-1c" = tot textul, fără "\n"-ul pe care Tkinter îl adaugă la final
        return self.text_area.get("1.0", "end-1c")

    def load(self, path):
        """Încarcă fișierul `path` în document.

        Dacă fișierul nu poate fi citit, aruncă OSError și documentul rămâne neschimbat.
        """
        text, newline, encoding = file_io.read_file(path)

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", text)
        # Golim istoricul Undo, ca Ctrl+Z să nu „anuleze” deschiderea fișierului
        self.text_area.edit_reset()
        self.path = Path(path)
        self.newline = newline
        self.encoding.set(encoding)

    def save(self, path):
        """Salvează documentul în `path`, cu terminația și codificarea lui.

        Poate arunca UnicodeEncodeError (caractere care nu încap în codificare)
        sau OSError (fișierul nu poate fi scris). În ambele cazuri `path` nu se schimbă.
        """
        file_io.write_file(path, self.get_text(), self.newline, self.encoding.get())
        self.path = Path(path)
