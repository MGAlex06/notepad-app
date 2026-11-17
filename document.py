import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path

import file_io
import markdown
from strings import t

# Spațiul liber (în pixeli) din stânga și din dreapta numerelor de linie
GUTTER_PADDING = 6

# Modul Markdown: pauza (ms) după ultima modificare înainte de recolorare
MARKDOWN_DELAY_MS = 200
# Peste atâtea caractere nu mai colorăm, ca interfața să nu se blocheze
MARKDOWN_MAX_CHARS = 200_000

# Mărimea fontului (în puncte) pentru zoom
DEFAULT_FONT_SIZE = 10  # Courier New 10, ca fontul implicit al lui Tkinter
MIN_FONT_SIZE = 6
MAX_FONT_SIZE = 40


def next_font_size(current, step, minimum, maximum):
    """Mărimea după un pas de zoom (+1 / -1), ținută între minimum și maximum."""
    return max(minimum, min(maximum, current + step))


def gutter_width(line_count, digit_width, padding):
    """Lățimea în pixeli a coloanei de numere: cifrele ultimei linii + margini.

    Exemplu: 9 linii → 1 cifră, 10 linii → 2 cifre, 100 linii → 3 cifre.
    """
    digits = len(str(max(line_count, 1)))  # un document gol are tot linia 1
    return digits * digit_width + 2 * padding


def format_timestamp(moment):
    """Data și ora ca text, de forma "HH:MM ZZ.LL.AAAA" (ex. "14:49 16.11.2026").

    `moment` e un obiect datetime. %H, %M, %d, %m pun mereu două cifre (09:05).
    """
    return moment.strftime("%H:%M %d.%m.%Y")


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

        # Fontul documentului: o copie a fontului implicit (Courier New).
        # Îl folosesc și textul, și numerele de linie, așa că la zoom
        # schimbăm mărimea într-un singur loc și cresc amândouă.
        self.font = tkfont.Font(root=self.frame, font="TkFixedFont")
        self.font.config(size=DEFAULT_FONT_SIZE)

        # Zona de text, care ocupă tot restul.
        # undo=True pornește Ctrl+Z (anulează) și Ctrl+Y (refă).
        # wrap=tk.WORD rupe rândurile lungi la cuvinte, ca Notepad.
        self.text_area = tk.Text(
            self.frame,
            font=self.font,
            yscrollcommand=self._on_yscroll,
            xscrollcommand=self.xscrollbar.set,
            undo=True,
            wrap=tk.WORD,
        )

        # Coloana cu numere de linie: un Canvas pe care desenăm numerele.
        # Nu e zonă de text, deci nu atinge textul și nici istoricul Undo.
        self.gutter = tk.Canvas(
            self.frame, highlightthickness=0, bd=0, bg="#f0f0f0", width=0
        )
        # Linia subțire dintre numere și text
        self.separator = tk.Frame(self.frame, width=1, bg="#c0c0c0")
        self._redraw_pending = False  # True = redesenarea e deja programată

        self.set_line_numbers(True)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Când se schimbă textul sau mărimea, redesenăm numerele.
        # add="+" = adăugăm legătura fără s-o ștergem pe cea din main.py.
        for event in ("<KeyPress>", "<<Paste>>", "<<Cut>>", "<<Undo>>",
                      "<<Redo>>", "<Configure>"):
            self.text_area.bind(event, self.schedule_line_numbers, add="+")

        # Modul Markdown: colorăm textul cu etichete (tag-uri) Tkinter.
        # Variabila Tkinter e a acestui document, ca bifa din View să arate
        # starea filei active (la fel ca meniul Codificare).
        self.markdown_mode = tk.BooleanVar(master=parent, value=False)
        self._markdown_job = None  # recolorarea programată (None = niciuna)
        self._setup_markdown_tags()
        # Când se schimbă textul, recolorăm (după o scurtă pauză)
        for event in ("<KeyPress>", "<<Paste>>", "<<Cut>>", "<<Undo>>", "<<Redo>>"):
            self.text_area.bind(event, self.schedule_markdown, add="+")

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
            return t("app.untitled")  # în limba curentă
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
        # Rândurile s-au rupt altfel, deci numerele își schimbă locul
        self.schedule_line_numbers()

    def set_line_numbers(self, enabled):
        """Arată (True) sau ascunde (False) coloana cu numere de linie."""
        if enabled:
            # after=self.scrollbar: bara verticală e mereu prima împachetată,
            # deci gutter-ul ajunge mereu în stânga, lângă text
            self.gutter.pack(side=tk.LEFT, fill=tk.Y, after=self.scrollbar)
            self.separator.pack(side=tk.LEFT, fill=tk.Y, after=self.gutter)
            self.schedule_line_numbers()
        else:
            self.gutter.pack_forget()
            self.separator.pack_forget()

    def set_font_size(self, size):
        """Zoom: schimbă mărimea fontului (textul și numerele de linie)."""
        # Tkinter reașază singur textul (și rupe din nou rândurile, cu Word Wrap)
        self.font.config(size=size)
        # Fonturile etichetelor Markdown cresc și ele, ca să rămână la fel de mari
        self.bold_font.config(size=size)
        self.italic_font.config(size=size)
        self.schedule_line_numbers()  # lățimea coloanei și pozițiile numerelor

    def _setup_markdown_tags(self):
        """Creează fonturile și etichetele (culorile) pentru modul Markdown."""
        # Copii ale fontului textului, doar îngroșate sau înclinate
        self.bold_font = self.font.copy()
        self.bold_font.config(weight="bold")
        self.italic_font = self.font.copy()
        self.italic_font.config(slant="italic")

        styles = {
            "quote": {"foreground": "#6a737d"},
            "list": {"foreground": "#b35c00"},
            "link": {"foreground": "#0b6bcb", "underline": True},
            "italic": {"font": self.italic_font},
            "bold": {"font": self.bold_font},
            "code": {"foreground": "#a31515", "background": "#f0f0f0"},
            "heading": {"foreground": "#1f4e9c", "font": self.bold_font},
            "code_block": {"foreground": "#a31515", "background": "#f0f0f0"},
        }
        # Eticheta creată mai târziu „câștigă” când două se suprapun,
        # deci le creăm în ordinea din markdown.KINDS
        for kind in markdown.KINDS:
            self.text_area.tag_configure(f"md_{kind}", **styles[kind])
        # Selecția trebuie să rămână vizibilă și peste fundalul codului
        self.text_area.tag_raise("sel")

    def schedule_markdown(self, event=None):
        """Cere recolorarea peste MARKDOWN_DELAY_MS, nu la fiecare tastă.

        Dacă mai vine o tastă înainte de termen, anulăm programarea veche
        și o pornim din nou, deci colorăm o singură dată, după pauză.
        """
        self.cancel_markdown()
        self._markdown_job = self.text_area.after(
            MARKDOWN_DELAY_MS, self.apply_markdown
        )

    def cancel_markdown(self):
        """Anulează recolorarea programată (de exemplu la închiderea filei)."""
        if self._markdown_job is not None:
            self.text_area.after_cancel(self._markdown_job)
            self._markdown_job = None

    def set_markdown(self, enabled):
        """Pornește (True) sau oprește (False) modul Markdown și recolorează."""
        self.markdown_mode.set(enabled)
        self.apply_markdown()

    def apply_markdown(self):
        """Pune din nou culorile Markdown (sau le șterge, dacă modul e oprit).

        Etichetele doar colorează: nu schimbă textul, nu intră în istoricul
        Undo și nu pun steagul „modificat”.
        """
        self._markdown_job = None
        # Fila a fost închisă între timp
        if not self.text_area.winfo_exists():
            return

        # Ștergem culorile vechi
        for kind in markdown.KINDS:
            self.text_area.tag_remove(f"md_{kind}", "1.0", tk.END)

        if not self.markdown_mode.get():
            return
        text = self.get_text()
        if len(text) > MARKDOWN_MAX_CHARS:
            return  # fișier prea mare: rămâne fără culori

        lines = text.split("\n")
        for span in markdown.find_spans(text):
            # Coloanele vin numărate ca în Python; le traducem pentru Tkinter
            # (un emoji ocupă două poziții în Tkinter, vezi markdown.tk_column)
            start_col = markdown.tk_column(lines[span.start_line - 1], span.start_col)
            end_col = markdown.tk_column(lines[span.end_line - 1], span.end_col)
            self.text_area.tag_add(
                f"md_{span.kind}",
                f"{span.start_line}.{start_col}",
                f"{span.end_line}.{end_col}",
            )

    def _on_yscroll(self, *args):
        """Textul s-a derulat: mutăm bara de derulare și redesenăm numerele."""
        self.scrollbar.set(*args)
        self.schedule_line_numbers()

    def schedule_line_numbers(self, event=None):
        """Cere redesenarea numerelor, după ce Tkinter termină ce are de făcut.

        La o tastă, textul încă nu s-a schimbat când ajungem aici, așa că
        redesenăm „mai târziu” (after_idle). Dacă vin multe cereri deodată,
        redesenăm o singură dată.
        """
        if not self._redraw_pending:
            self._redraw_pending = True
            self.text_area.after_idle(self.redraw_line_numbers)

    def redraw_line_numbers(self):
        """Desenează numerele liniilor reale vizibile acum pe ecran."""
        self._redraw_pending = False
        # Fila a fost închisă între timp, sau numerele sunt ascunse
        if not self.gutter.winfo_exists() or not self.gutter.winfo_manager():
            return

        # Câte linii are documentul → cât de lată e coloana
        line_count = int(self.text_area.index("end-1c").split(".")[0])
        width = gutter_width(line_count, self.font.measure("0"), GUTTER_PADDING)
        if int(self.gutter.cget("width")) != width:
            self.gutter.config(width=width)

        self.gutter.delete("all")  # ștergem numerele vechi

        # Prima linie reală care se vede (poate fi doar coada ei, cu Word Wrap)
        first_line = int(self.text_area.index("@0,0").split(".")[0])
        line = first_line
        while line <= line_count:
            # dlineinfo dă poziția PRIMULUI rând vizual al liniei, deci o linie
            # ruptă de Word Wrap primește un singur număr. None = nu se vede.
            info = self.text_area.dlineinfo(f"{line}.0")
            if info is None:
                if line > first_line:
                    break  # am trecut de marginea de jos
                line += 1  # începutul liniei e deasupra ecranului: fără număr
                continue
            y = info[1]
            self.gutter.create_text(
                width - GUTTER_PADDING, y, anchor="ne",
                text=str(line), font=self.font, fill="#808080",
            )
            line += 1

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
        self.schedule_line_numbers()
        # Un fișier .md / .markdown pornește singur modul Markdown
        if markdown.is_markdown_path(path):
            self.markdown_mode.set(True)
        self.apply_markdown()  # culorile textului nou (sau ștergerea celor vechi)

    def save(self, path):
        """Salvează documentul în `path`, cu terminația și codificarea lui.

        Poate arunca UnicodeEncodeError (caractere care nu încap în codificare)
        sau OSError (fișierul nu poate fi scris). În ambele cazuri `path` nu se schimbă.
        """
        file_io.write_file(path, self.get_text(), self.newline, self.encoding.get())
        # Calea s-a schimbat? (Salvează ca, sau prima salvare a unei file noi)
        path_changed = Path(path) != self.path
        self.path = Path(path)
        # Tot ce era în document e acum salvat pe disc
        self.text_area.edit_modified(False)
        # Doar la o cale nouă .md pornim modul Markdown; o salvare obișnuită
        # (Ctrl+S pe același fișier) nu schimbă bifa
        if path_changed and markdown.is_markdown_path(path):
            self.set_markdown(True)
