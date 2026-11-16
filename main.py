import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import file_io
import search
import session
from document import Document, format_timestamp

FILE_TYPES = [("Fișiere text", "*.txt"), ("Toate fișierele", "*.*")]

# Scurtăturile care funcționează acum, afișate în Ajutor → Scurtături.
# Primele nouă le legăm noi în add_tab; restul vin gata făcute din Tkinter.
SHORTCUTS = [
    ("Ctrl+N", "Filă nouă"),
    ("Ctrl+W", "Închide fila"),
    ("Ctrl+O", "Deschide"),
    ("Ctrl+S", "Salvează"),
    ("Ctrl+Shift+S", "Salvează ca"),
    ("Ctrl+F", "Caută"),
    ("Ctrl+H", "Înlocuiește"),
    ("Ctrl+G", "Salt la linie"),
    ("F5", "Inserează data și ora"),
    ("Ctrl+Z", "Anulează"),
    ("Ctrl+Y", "Refă"),
    ("Ctrl+X", "Taie"),
    ("Ctrl+C", "Copiază"),
    ("Ctrl+V", "Lipește"),
    ("Ctrl+A", "Selectează tot"),
]


def make_x_image(color):
    """O imagine 12x12, transparentă, cu un X de culoarea `color`."""
    image = tk.PhotoImage(width=12, height=12)
    # Colorăm pixel cu pixel cele două diagonale ale X-ului
    for i in range(2, 10):
        image.put(color, to=(i, i, i + 1, i + 1))  # diagonala \
        image.put(color, to=(i, 11 - i, i + 1, 12 - i))  # diagonala /
    return image


def main():
    # Fereastra principală a aplicației
    root = tk.Tk()
    root.title("Fără titlu - Notepad")
    root.geometry("800x600")

    # Bara de stare de jos. O împachetăm prima, ca să rămână vizibilă
    # chiar și când fereastra e micșorată.
    status_bar = tk.Label(root, anchor="w", relief=tk.SUNKEN, padx=5)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Butonul X de pe file. ttk.Notebook nu are așa ceva, așa că:
    # 1. desenăm două imagini mici cu un X (gri normal, roșu sub mouse);
    # 2. facem din ele un „element” de stil numit "close";
    # 3. îl punem în desenul fiecărei file, în dreapta numelui.
    close_image = make_x_image("#808080")
    close_image_hover = make_x_image("#c42b1c")

    style = ttk.Style(root)
    # "active" = mouse-ul e deasupra filei. padding = spațiu în stânga X-ului.
    style.element_create(
        "close", "image", close_image, ("active", close_image_hover),
        padding=(6, 0, 0, 0), sticky="",
    )
    style.layout("Closable.TNotebook.Tab", [
        ("Notebook.tab", {"sticky": "nswe", "children": [
            ("Notebook.padding", {"side": "top", "sticky": "nswe", "children": [
                ("Notebook.focus", {"side": "top", "sticky": "nswe", "children": [
                    ("Notebook.label", {"side": "left", "sticky": ""}),
                    ("close", {"side": "left", "sticky": ""}),
                ]}),
            ]}),
        ]}),
    ])

    # Filele: un Notebook care ocupă tot restul ferestrei.
    # Fiecare filă conține frame-ul unui Document.
    notebook = ttk.Notebook(root, style="Closable.TNotebook")
    notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Ținem minte ce Document e în fiecare filă.
    # Cheia e numele frame-ului, adică ce returnează notebook.select().
    documents = {}

    # Încadrarea textului (View → Încadrare text): o singură setare
    # pentru toate filele. True = pornită, ca la Notepad.
    word_wrap = tk.BooleanVar(master=root, value=True)
    # Numerele de linie (View → Numere de linie): tot o setare pentru toate filele
    line_numbers = tk.BooleanVar(master=root, value=True)

    def current_doc():
        """Documentul din fila activă."""
        return documents[notebook.select()]

    def update_title():
        root.title(f"{current_doc().display_name()} - Notepad")

    def update_tab_title(doc):
        notebook.tab(doc.frame, text=doc.display_name())

    def update_status(event=None):
        doc = current_doc()
        # Poziția cursorului vine ca text, de forma "linie.coloană", ex. "3.7"
        line, column = doc.text_area.index(tk.INSERT).split(".")
        # Coloana din Tkinter începe de la 0; o afișăm de la 1, ca Notepad
        column = int(column) + 1
        char_count = len(doc.get_text())
        status_bar.config(
            text=f"Ln {line}, Col {column} | {char_count} caractere"
            f" | {doc.encoding.get()}"
        )

    def open_file():
        filename = filedialog.askopenfilename(filetypes=FILE_TYPES)
        if not filename:
            return  # utilizatorul a apăsat Cancel

        # Dacă fila curentă e goală și nesalvată, o folosim pe ea.
        # Altfel facem un document nou, pe care îl punem într-o filă
        # doar dacă fișierul s-a încărcat cu succes.
        reuse_current = current_doc().is_blank()
        if reuse_current:
            doc = current_doc()
        else:
            doc = Document(notebook)

        try:
            doc.load(filename)
        except OSError as error:
            if not reuse_current:
                doc.frame.destroy()  # documentul nou nu mai e necesar
            messagebox.showerror("Eroare", f"Nu am putut deschide fișierul:\n{error}")
            return

        if reuse_current:
            update_tab_title(doc)
            update_title()
            update_status()
        else:
            add_tab(doc)  # selectarea filei noi actualizează titlul și bara de stare

    def save_to(doc, path):
        """Salvează `doc` în `path`. Returnează True dacă a reușit."""
        try:
            doc.save(path)
        except UnicodeEncodeError:
            messagebox.showerror(
                "Eroare",
                "Textul conține caractere care nu pot fi salvate în "
                f"{doc.encoding.get()}.\n"
                "Alege altă codificare din meniul Codificare.",
            )
            return False
        except OSError as error:
            messagebox.showerror("Eroare", f"Nu am putut salva fișierul:\n{error}")
            return False

        update_tab_title(doc)
        update_title()
        return True

    def save_file_as(doc):
        """Întreabă unde să salveze `doc`. Returnează True dacă s-a salvat."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=FILE_TYPES
        )
        if not filename:
            return False  # utilizatorul a apăsat Cancel
        return save_to(doc, filename)

    def save_file(doc):
        """Salvează `doc` (cu Save As dacă n-are încă fișier). True dacă a reușit."""
        if doc.path is None:
            return save_file_as(doc)
        return save_to(doc, doc.path)

    def find_and_select(query, match_case, parent):
        """Caută `query` de la cursor (cu reluare de la început) și selectează potrivirea.

        `parent` e fereastra peste care apare mesajul "Nu găsesc".
        """
        doc = current_doc()
        text_area = doc.text_area
        text = doc.get_text()
        # Câte caractere sunt înainte de cursor = de unde începem căutarea
        start = len(text_area.get("1.0", tk.INSERT))

        position = search.find_next_wrap(text, query, start, match_case)
        if position is None:
            messagebox.showinfo("Notepad", f'Nu găsesc "{query}"', parent=parent)
            return

        # Transformăm poziția (un număr) în indici Tkinter
        match_start = f"1.0 + {position} chars"
        match_end = f"1.0 + {position + len(query)} chars"

        text_area.tag_remove("sel", "1.0", tk.END)  # ștergem selecția veche
        text_area.tag_add("sel", match_start, match_end)  # selectăm potrivirea
        text_area.mark_set(tk.INSERT, match_end)  # următoarea căutare pornește de aici
        # see() arată doar un caracter: întâi sfârșitul, apoi începutul,
        # ca să se vadă tot cuvântul (sau măcar începutul, dacă nu încape).
        text_area.see(match_end)
        text_area.see(match_start)
        update_status()

    def as_one_undo_step(action):
        """Rulează `action` astfel încât un singur Ctrl+Z să anuleze tot ce face."""
        text_area = current_doc().text_area
        # Tkinter pune singur separatoare între ștergeri și inserări;
        # le oprim temporar și punem noi câte unul la început și la final.
        text_area.config(autoseparators=False)
        text_area.edit_separator()
        action()
        text_area.edit_separator()
        text_area.config(autoseparators=True)
        # Textul s-a schimbat din cod, nu de la tastatură: redesenăm numerele
        current_doc().schedule_line_numbers()

    def insert_timestamp(event=None):
        """F5: inserează data și ora la cursor (înlocuiește selecția, dacă există)."""
        text_area = current_doc().text_area
        stamp = format_timestamp(datetime.now())

        def insert_stamp():
            if text_area.tag_ranges("sel"):  # e ceva selectat: îl înlocuim
                start = text_area.index("sel.first")
                text_area.delete("sel.first", "sel.last")
                text_area.mark_set(tk.INSERT, start)
            text_area.insert(tk.INSERT, stamp)

        as_one_undo_step(insert_stamp)  # un singur Ctrl+Z anulează tot
        text_area.see(tk.INSERT)  # derulăm ca textul nou să se vadă
        update_title()
        update_status()
        return "break"

    # Fereastra de căutare (None = nu e deschisă)
    find_window = None
    find_entry = None  # câmpul de text din fereastra de căutare

    def open_find_window(event=None):
        nonlocal find_window, find_entry

        # Dacă fereastra e deja deschisă, doar o aducem în față
        if find_window is not None:
            find_window.lift()
            find_entry.focus_set()
            return "break"

        find_window = tk.Toplevel(root)
        find_window.title("Caută")
        find_window.transient(root)  # stă mereu deasupra ferestrei principale
        find_window.resizable(False, False)

        tk.Label(find_window, text="Caută:").grid(row=0, column=0, padx=5, pady=5)
        find_entry = tk.Entry(find_window, width=30)
        find_entry.grid(row=0, column=1, padx=5, pady=5)

        match_case = tk.BooleanVar(value=False)
        tk.Checkbutton(
            find_window, text="Potrivire majuscule", variable=match_case
        ).grid(row=1, column=1, sticky="w", padx=5)

        def close():
            nonlocal find_window, find_entry
            find_window.destroy()
            find_window = None
            find_entry = None

        def do_find():
            find_and_select(find_entry.get(), match_case.get(), find_window)

        tk.Button(find_window, text="Caută următorul", command=do_find).grid(
            row=0, column=2, padx=5, pady=5, sticky="ew"
        )
        tk.Button(find_window, text="Închide", command=close).grid(
            row=1, column=2, padx=5, pady=5, sticky="ew"
        )

        # Butonul X din colț face același lucru ca "Închide"
        find_window.protocol("WM_DELETE_WINDOW", close)

        find_entry.focus_set()
        return "break"

    # Fereastra de înlocuire (None = nu e deschisă)
    replace_window = None
    replace_find_entry = None  # câmpul "Caută" din fereastra de înlocuire

    def open_replace_window(event=None):
        nonlocal replace_window, replace_find_entry

        # Dacă fereastra e deja deschisă, doar o aducem în față
        if replace_window is not None:
            replace_window.lift()
            replace_find_entry.focus_set()
            return "break"

        replace_window = tk.Toplevel(root)
        replace_window.title("Înlocuiește")
        replace_window.transient(root)  # stă mereu deasupra ferestrei principale
        replace_window.resizable(False, False)

        tk.Label(replace_window, text="Caută:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        replace_find_entry = tk.Entry(replace_window, width=30)
        replace_find_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(replace_window, text="Înlocuiește cu:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )
        replacement_entry = tk.Entry(replace_window, width=30)
        replacement_entry.grid(row=1, column=1, padx=5, pady=5)

        match_case = tk.BooleanVar(value=False)
        tk.Checkbutton(
            replace_window, text="Potrivire majuscule", variable=match_case
        ).grid(row=2, column=1, sticky="w", padx=5)

        def close():
            nonlocal replace_window, replace_find_entry
            replace_window.destroy()
            replace_window = None
            replace_find_entry = None

        def do_find():
            find_and_select(replace_find_entry.get(), match_case.get(), replace_window)

        def do_replace():
            doc = current_doc()
            text_area = doc.text_area
            query = replace_find_entry.get()
            replacement = replacement_entry.get()

            # Înlocuim doar dacă e ceva selectat și selecția e chiar o potrivire.
            # Altfel nu dăm eroare: doar căutăm următoarea potrivire.
            if text_area.tag_ranges("sel"):
                text = doc.get_text()
                sel_start = len(text_area.get("1.0", "sel.first"))
                sel_length = len(text_area.get("sel.first", "sel.last"))

                if sel_length == len(query) and search.is_match_at(
                    text, query, sel_start, match_case.get()
                ):
                    def replace_selection():
                        # Ținem minte unde începe selecția, apoi o înlocuim
                        start_index = text_area.index("sel.first")
                        text_area.delete("sel.first", "sel.last")
                        text_area.insert(start_index, replacement)
                        # Cursorul după înlocuire: de aici continuă căutarea
                        text_area.mark_set(
                            tk.INSERT, f"{start_index} + {len(replacement)} chars"
                        )

                    as_one_undo_step(replace_selection)

            do_find()

        def do_replace_all():
            doc = current_doc()
            text_area = doc.text_area
            query = replace_find_entry.get()
            text = doc.get_text()
            cursor = len(text_area.get("1.0", tk.INSERT))

            new_text, count, new_cursor = search.replace_all(
                text, query, replacement_entry.get(), match_case.get(), cursor
            )

            if count > 0:
                top = text_area.yview()[0]  # cât era derulat textul (0 = sus, 1 = jos)

                def rewrite_text():
                    text_area.delete("1.0", "end-1c")
                    text_area.insert("1.0", new_text)

                as_one_undo_step(rewrite_text)

                # Punem cursorul și derularea înapoi cât mai aproape de unde erau
                text_area.mark_set(tk.INSERT, f"1.0 + {new_cursor} chars")
                text_area.yview_moveto(top)
                update_status()

            messagebox.showinfo(
                "Notepad", f"Am înlocuit {count} potriviri.", parent=replace_window
            )

        tk.Button(replace_window, text="Caută următorul", command=do_find).grid(
            row=0, column=2, padx=5, pady=5, sticky="ew"
        )
        tk.Button(replace_window, text="Înlocuiește", command=do_replace).grid(
            row=1, column=2, padx=5, pady=5, sticky="ew"
        )
        tk.Button(replace_window, text="Înlocuiește tot", command=do_replace_all).grid(
            row=2, column=2, padx=5, pady=5, sticky="ew"
        )
        tk.Button(replace_window, text="Închide", command=close).grid(
            row=3, column=2, padx=5, pady=5, sticky="ew"
        )

        # Butonul X din colț face același lucru ca "Închide"
        replace_window.protocol("WM_DELETE_WINDOW", close)

        replace_find_entry.focus_set()
        return "break"

    # Fereastra "Salt la linie" (None = nu e deschisă)
    goto_window = None
    goto_entry = None  # câmpul pentru numărul liniei

    def open_goto_window(event=None):
        nonlocal goto_window, goto_entry

        # Dacă fereastra e deja deschisă, doar o aducem în față
        if goto_window is not None:
            goto_window.lift()
            goto_entry.focus_set()
            return "break"

        goto_window = tk.Toplevel(root)
        goto_window.title("Salt la linie")
        goto_window.transient(root)  # stă mereu deasupra ferestrei principale
        goto_window.resizable(False, False)

        tk.Label(goto_window, text="Număr linie:").grid(row=0, column=0, padx=5, pady=5)
        goto_entry = tk.Entry(goto_window, width=15)
        goto_entry.grid(row=0, column=1, padx=5, pady=5)

        def close():
            nonlocal goto_window, goto_entry
            goto_window.destroy()
            goto_window = None
            goto_entry = None

        def do_goto(event=None):
            # Fila activă acum, la apăsarea lui "Salt"
            text_area = current_doc().text_area
            # "end-1c" = ultimul caracter real; partea dinainte de "." e numărul
            # ultimei linii. Sunt linii adevărate (cele din bara de stare), nu
            # rândurile de pe ecran, deci încadrarea textului nu contează.
            line_count = int(text_area.index("end-1c").split(".")[0])

            line = search.parse_line_number(goto_entry.get(), line_count)
            if line is None:
                messagebox.showinfo(
                    "Notepad",
                    f"Numărul liniei trebuie să fie între 1 și {line_count}.",
                    parent=goto_window,
                )
                return

            # Ștergem selecția veche, ca să nu rămână ceva selectat în alt loc
            text_area.tag_remove("sel", "1.0", tk.END)
            text_area.mark_set(tk.INSERT, f"{line}.0")  # coloana 0 = începutul liniei
            text_area.see(f"{line}.0")  # derulăm ca linia să se vadă
            update_status()
            close()
            text_area.focus_set()  # cursorul clipește în text, pe linia nouă

        tk.Button(goto_window, text="Salt", command=do_goto).grid(
            row=0, column=2, padx=5, pady=5, sticky="ew"
        )
        tk.Button(goto_window, text="Închide", command=close).grid(
            row=1, column=2, padx=5, pady=5, sticky="ew"
        )

        # Enter în câmp face același lucru ca butonul "Salt"
        goto_entry.bind("<Return>", do_goto)
        # Butonul X din colț face același lucru ca "Închide"
        goto_window.protocol("WM_DELETE_WINDOW", close)

        goto_entry.focus_set()
        return "break"

    def add_tab(doc):
        """Pune `doc` într-o filă nouă, îi leagă tastele și o face fila activă."""
        notebook.add(doc.frame, text=doc.display_name())
        documents[str(doc.frame)] = doc
        doc.set_word_wrap(word_wrap.get())  # fila nouă primește setarea curentă
        doc.set_line_numbers(line_numbers.get())

        text_area = doc.text_area
        # Actualizăm bara de stare după fiecare tastă și fiecare click
        text_area.bind("<KeyRelease>", update_status)
        text_area.bind("<ButtonRelease-1>", update_status)

        # Scurtăturile le legăm pe zona de text și returnăm "break", ca
        # Tkinter să nu mai facă și acțiunea lui implicită (de exemplu Ctrl+F
        # mută cursorul un caracter, iar Ctrl+H e Backspace).
        # Varianta cu literă mare e pentru când Caps Lock e pornit.
        text_area.bind("<Control-f>", open_find_window)
        text_area.bind("<Control-F>", open_find_window)
        text_area.bind("<Control-h>", open_replace_window)
        text_area.bind("<Control-H>", open_replace_window)
        text_area.bind("<Control-g>", open_goto_window)
        text_area.bind("<Control-G>", open_goto_window)
        text_area.bind("<F5>", insert_timestamp)
        text_area.bind("<Control-n>", new_tab)
        text_area.bind("<Control-N>", new_tab)
        text_area.bind("<Control-w>", close_tab)
        text_area.bind("<Control-W>", close_tab)
        text_area.bind("<Control-o>", open_shortcut)
        text_area.bind("<Control-O>", open_shortcut)
        text_area.bind("<Control-s>", save_shortcut)
        text_area.bind("<Control-S>", save_shortcut)
        # Cu Caps Lock, Ctrl+S dă tot "S" mare, ca și Ctrl+Shift+S.
        # Legăm Save As explicit cu Shift: Tkinter alege bind-ul cel mai
        # precis, deci Ctrl+Shift+S → Save As, iar Caps Lock + Ctrl+S → Save.
        text_area.bind("<Control-Shift-S>", save_as_shortcut)
        text_area.bind("<Control-Shift-s>", save_as_shortcut)

        notebook.select(doc.frame)

    def new_tab(event=None):
        """Ctrl+N: deschide o filă nouă, goală."""
        add_tab(Document(notebook))
        return "break"

    def confirm_save(doc):
        """Dacă `doc` are modificări, întreabă dacă le salvăm.

        Returnează True dacă putem merge mai departe (Da + salvat, sau Nu)
        și False dacă trebuie să ne oprim (Anulare, sau salvarea n-a reușit).
        """
        if not doc.is_modified():
            return True
        # Da = True, Nu = False, Anulare = None
        answer = messagebox.askyesnocancel(
            "Notepad", f'Salvezi modificările din "{doc.display_name()}"?'
        )
        if answer is None:
            return False  # Anulare
        if answer and not save_file(doc):
            return False  # salvarea n-a reușit: nu pierdem textul
        return True

    def close_doc(doc):
        """Închide fila lui `doc`, după ce întreabă de salvare."""
        if not confirm_save(doc):
            return  # fila rămâne deschisă

        del documents[str(doc.frame)]
        notebook.forget(doc.frame)
        doc.frame.destroy()

        # Aplicația rămâne mereu cu cel puțin o filă
        if not notebook.tabs():
            new_tab()

    def close_tab(event=None):
        """Ctrl+W: închide fila curentă."""
        close_doc(current_doc())
        return "break"

    def open_shortcut(event=None):
        """Ctrl+O: deschide un fișier."""
        open_file()
        return "break"

    def save_shortcut(event=None):
        """Ctrl+S: salvează fila activă."""
        save_file(current_doc())
        return "break"

    def save_as_shortcut(event=None):
        """Ctrl+Shift+S: salvează fila activă sub alt nume."""
        save_file_as(current_doc())
        return "break"

    # Indexul filei al cărei X a fost apăsat (None = niciunul)
    pressed_close_index = None

    def on_tab_press(event):
        """Click apăsat pe Notebook: dacă e pe un X, ținem minte fila."""
        nonlocal pressed_close_index
        if notebook.identify(event.x, event.y) == "close":
            pressed_close_index = notebook.index(f"@{event.x},{event.y}")
            # "break": fila nu devine activă doar pentru că am apăsat X-ul
            return "break"

    def on_tab_release(event):
        """Click eliberat: închidem fila doar dacă mouse-ul e tot pe X-ul ei."""
        nonlocal pressed_close_index
        index = pressed_close_index
        pressed_close_index = None
        if index is None:
            return  # apăsarea n-a fost pe un X

        if (
            notebook.identify(event.x, event.y) == "close"
            and notebook.index(f"@{event.x},{event.y}") == index
        ):
            # notebook.tabs() dă numele frame-urilor, adică cheile din documents
            close_doc(documents[str(notebook.tabs()[index])])

    def on_tab_changed(event):
        """Când se schimbă fila activă, totul trece pe documentul ei."""
        if not notebook.select():
            return  # nu mai e nicio filă (doar o clipă, la închiderea ultimei)

        doc = current_doc()
        update_title()
        update_status()
        # Butoanele radio din Codificare arată acum codificarea acestui document
        for index in range(len(file_io.ENCODINGS)):
            encoding_menu.entryconfig(index, variable=doc.encoding)
        doc.text_area.focus_set()

    def toggle_word_wrap():
        """View → Încadrare text: aplică noua setare tuturor filelor deschise."""
        # Bifa a schimbat deja singură valoarea lui word_wrap
        for doc in documents.values():
            doc.set_word_wrap(word_wrap.get())

    def toggle_line_numbers():
        """View → Numere de linie: aplică noua setare tuturor filelor deschise."""
        for doc in documents.values():
            doc.set_line_numbers(line_numbers.get())

    # Fereastra cu scurtături (None = nu e deschisă)
    shortcuts_window = None

    def show_shortcuts():
        """Ajutor → Scurtături: o fereastră mică cu lista din SHORTCUTS."""
        nonlocal shortcuts_window

        # Dacă fereastra e deja deschisă, doar o aducem în față
        if shortcuts_window is not None:
            shortcuts_window.lift()
            shortcuts_window.focus_set()
            return

        window = tk.Toplevel(root)
        shortcuts_window = window
        window.title("Scurtături de la tastatură")
        window.transient(root)  # stă deasupra ferestrei principale
        window.resizable(False, False)

        # Câte un rând pentru fiecare scurtătură: tasta în stânga, ce face în dreapta
        for row, (keys, description) in enumerate(SHORTCUTS):
            tk.Label(window, text=keys, font=("Segoe UI", 9, "bold")).grid(
                row=row, column=0, padx=(10, 20), pady=2, sticky="w"
            )
            tk.Label(window, text=description).grid(
                row=row, column=1, padx=(0, 10), pady=2, sticky="w"
            )

        def close():
            nonlocal shortcuts_window
            window.destroy()
            shortcuts_window = None

        tk.Button(window, text="Închide", width=10, command=close).grid(
            row=len(SHORTCUTS), column=0, columnspan=2, pady=10
        )

        # Butonul X din colț face același lucru ca "Închide"
        window.protocol("WM_DELETE_WINDOW", close)

    # Meniul de sus, cu submeniul File.
    # `accelerator` doar afișează scurtătura în dreapta; tasta în sine
    # funcționează prin bind-urile din add_tab.
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Filă nouă", command=new_tab, accelerator="Ctrl+N")
    file_menu.add_command(label="Închide fila", command=close_tab, accelerator="Ctrl+W")
    file_menu.add_separator()
    file_menu.add_command(label="Open...", command=open_shortcut, accelerator="Ctrl+O")
    file_menu.add_command(label="Save", command=save_shortcut, accelerator="Ctrl+S")
    file_menu.add_command(
        label="Save As...", command=save_as_shortcut, accelerator="Ctrl+Shift+S"
    )
    menubar.add_cascade(label="File", menu=file_menu)

    # Meniul Editare: căutare, înlocuire și salt la linie.
    # Folosim aceleași funcții ca scurtăturile din add_tab.
    edit_menu = tk.Menu(menubar, tearoff=0)
    edit_menu.add_command(
        label="Caută...", command=open_find_window, accelerator="Ctrl+F"
    )
    edit_menu.add_command(
        label="Înlocuiește...", command=open_replace_window, accelerator="Ctrl+H"
    )
    edit_menu.add_command(
        label="Salt la linie...", command=open_goto_window, accelerator="Ctrl+G"
    )
    edit_menu.add_separator()
    edit_menu.add_command(
        label="Dată și oră", command=insert_timestamp, accelerator="F5"
    )
    menubar.add_cascade(label="Editare", menu=edit_menu)

    # Meniul Codificare: alegi cu ce codificare se salvează fișierul.
    # Variabila butoanelor radio o setăm în on_tab_changed, pe documentul activ.
    encoding_menu = tk.Menu(menubar, tearoff=0)
    for name in file_io.ENCODINGS:
        encoding_menu.add_radiobutton(label=name, value=name, command=update_status)
    menubar.add_cascade(label="Codificare", menu=encoding_menu)

    # Meniul View: opțiunea bifabilă de încadrare a textului
    view_menu = tk.Menu(menubar, tearoff=0)
    view_menu.add_checkbutton(
        label="Încadrare text", variable=word_wrap, command=toggle_word_wrap
    )
    view_menu.add_checkbutton(
        label="Numere de linie", variable=line_numbers, command=toggle_line_numbers
    )
    menubar.add_cascade(label="View", menu=view_menu)

    # Meniul Ajutor, ultimul din bară
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="Scurtături de la tastatură...", command=show_shortcuts)
    menubar.add_cascade(label="Ajutor", menu=help_menu)
    root.config(menu=menubar)

    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
    notebook.bind("<ButtonPress-1>", on_tab_press)
    notebook.bind("<ButtonRelease-1>", on_tab_release)

    def on_close():
        """Butonul X al ferestrei: întreabă de salvare, salvează sesiunea, închide."""
        active_doc = current_doc()

        # Întrebăm pentru fiecare filă modificată, în ordinea filelor
        for tab in notebook.tabs():
            doc = documents[str(tab)]
            if doc.is_modified():
                notebook.select(doc.frame)  # arătăm fila despre care întrebăm
                if not confirm_save(doc):
                    return  # Anulare: aplicația rămâne deschisă

        # Ținem minte doar filele care au un fișier pe disc.
        # Citim căile abia acum, ca un „Salvează ca” de mai sus să fie inclus.
        files = []
        for tab in notebook.tabs():
            doc = documents[str(tab)]
            if doc.path is not None:
                files.append(str(doc.path))

        active = None
        if active_doc.path is not None:
            active = str(active_doc.path)

        try:
            session.save_session(
                session.session_path(),
                files,
                active,
                root.winfo_width(),
                root.winfo_height(),
            )
        except OSError:
            pass  # dacă sesiunea nu se poate scrie, închidem oricum

        root.destroy()

    def restore_session():
        """La pornire: redeschide filele din sesiunea trecută (sau o filă goală)."""
        data = session.load_session(session.session_path())
        if data is None:
            new_tab()  # nu există sesiune validă: o filă goală
            return

        root.geometry(f"{data['width']}x{data['height']}")

        for path in data["files"]:
            doc = Document(notebook)
            try:
                doc.load(path)
            except OSError:
                # Fișierul nu mai există sau nu se poate citi: îl sărim
                doc.frame.destroy()
                continue
            add_tab(doc)

        if not notebook.tabs():
            new_tab()  # niciun fișier nu s-a putut deschide
            return

        # Activăm fila din sesiune; dacă nu mai există, rămâne prima filă
        notebook.select(notebook.tabs()[0])
        if data["active"] is not None:
            for tab in notebook.tabs():
                doc = documents[str(tab)]
                if doc.path == Path(data["active"]):
                    notebook.select(doc.frame)
                    break

    root.protocol("WM_DELETE_WINDOW", on_close)
    restore_session()

    # Pornim bucla aplicației (ține fereastra deschisă)
    root.mainloop()


if __name__ == "__main__":
    main()
