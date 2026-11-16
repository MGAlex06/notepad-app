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

        # Bara de derulare orizontală. O creăm acum, dar o afișăm doar
        # când încadrarea textului e oprită (vezi set_word_wrap).
        self.xscrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)

        # Zona de text, care ocupă tot restul.
        # undo=True pornește Ctrl+Z (anulează) și Ctrl+Y (refă).
        # wrap=tk.WORD rupe rândurile lungi la cuvinte, ca Notepad.
        self.text_area = tk.Text(
            self.frame,
            yscrollcommand=self.scrollbar.set,
            xscrollcommand=self.xscrollbar.set,
            undo=True,
            wrap=tk.WORD,
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Legăm barele de derulare de zona de text
        self.scrollbar.config(command=self.text_area.yview)
        self.xscrollbar.config(command=self.text_area.xview)

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

    def set_word_wrap(self, enabled):
        """Pornește (True) sau oprește (False) încadrarea textului în fereastră."""
        if enabled:
            self.text_area.config(wrap=tk.WORD)
            self.xscrollbar.pack_forget()  # ascundem bara orizontală
        else:
            # Rândurile nu se mai rup, deci avem nevoie de bara orizontală.
            # before=self.text_area o pune sub zona de text, nu lângă ea.
            self.text_area.config(wrap=tk.NONE)
            self.xscrollbar.pack(side=tk.BOTTOM, fill=tk.X, before=self.text_area)

    def is_modified(self):
        """True dacă textul s-a schimbat de la ultima deschidere sau salvare."""
        # Tkinter ține singur acest „steag”: îl pune pe True la orice modificare
        return self.text_area.edit_modified()

    def is_blank(self):
        """True dacă documentul e gol și n-a fost niciodată salvat."""
        return self.path is None and self.get_text() == ""

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
        # Textul tocmai a fost încărcat, deci nu are modificări nesalvate
        self.text_area.edit_modified(False)

    def save(self, path):
        """Salvează documentul în `path`, cu terminația și codificarea lui.

        Poate arunca UnicodeEncodeError (caractere care nu încap în codificare)
        sau OSError (fișierul nu poate fi scris). În ambele cazuri `path` nu se schimbă.
        """
        file_io.write_file(path, self.get_text(), self.newline, self.encoding.get())
        self.path = Path(path)
        # Tot ce era în document e acum salvat pe disc
        self.text_area.edit_modified(False)
