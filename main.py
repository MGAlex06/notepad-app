import tkinter as tk
from tkinter import filedialog, messagebox

import file_io
import search
from document import Document

FILE_TYPES = [("Fișiere text", "*.txt"), ("Toate fișierele", "*.*")]


def main():
    # Fereastra principală a aplicației
    root = tk.Tk()
    root.title("Fără titlu - Notepad")
    root.geometry("800x600")

    # Bara de stare de jos. O împachetăm prima, ca să rămână vizibilă
    # chiar și când fereastra e micșorată.
    status_bar = tk.Label(root, anchor="w", relief=tk.SUNKEN, padx=5)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Documentul (zona de text cu bara de derulare), care ocupă tot restul ferestrei
    doc = Document(root)
    doc.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def update_title():
        root.title(f"{doc.display_name()} - Notepad")

    def update_status(event=None):
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

        try:
            doc.load(filename)
        except OSError as error:
            messagebox.showerror("Eroare", f"Nu am putut deschide fișierul:\n{error}")
            return

        update_title()
        update_status()

    def save_to(path):
        try:
            doc.save(path)
        except UnicodeEncodeError:
            messagebox.showerror(
                "Eroare",
                "Textul conține caractere care nu pot fi salvate în "
                f"{doc.encoding.get()}.\n"
                "Alege altă codificare din meniul Codificare.",
            )
            return
        except OSError as error:
            messagebox.showerror("Eroare", f"Nu am putut salva fișierul:\n{error}")
            return

        update_title()

    def save_file_as():
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=FILE_TYPES
        )
        if not filename:
            return  # utilizatorul a apăsat Cancel
        save_to(filename)

    def save_file():
        if doc.path is None:
            save_file_as()
        else:
            save_to(doc.path)

    def find_and_select(query, match_case, parent):
        """Caută `query` de la cursor (cu reluare de la început) și selectează potrivirea.

        `parent` e fereastra peste care apare mesajul "Nu găsesc".
        """
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
        text_area.see(match_start)  # derulăm ca potrivirea să fie vizibilă
        update_status()

    def as_one_undo_step(action):
        """Rulează `action` astfel încât un singur Ctrl+Z să anuleze tot ce face."""
        text_area = doc.text_area
        # Tkinter pune singur separatoare între ștergeri și inserări;
        # le oprim temporar și punem noi câte unul la început și la final.
        text_area.config(autoseparators=False)
        text_area.edit_separator()
        action()
        text_area.edit_separator()
        text_area.config(autoseparators=True)

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

    # Meniul de sus, cu submeniul File
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open...", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_command(label="Save As...", command=save_file_as)
    menubar.add_cascade(label="File", menu=file_menu)

    # Meniul Codificare: alegi cu ce codificare se salvează fișierul.
    # Butonul radio bifat urmează automat codificarea documentului.
    encoding_menu = tk.Menu(menubar, tearoff=0)
    for name in file_io.ENCODINGS:
        encoding_menu.add_radiobutton(
            label=name, value=name, variable=doc.encoding, command=update_status
        )
    menubar.add_cascade(label="Codificare", menu=encoding_menu)
    root.config(menu=menubar)

    # Actualizăm bara de stare după fiecare tastă și fiecare click
    doc.text_area.bind("<KeyRelease>", update_status)
    doc.text_area.bind("<ButtonRelease-1>", update_status)
    update_status()  # o dată la pornire, ca bara să nu fie goală

    # Ctrl+F deschide căutarea. O legăm pe zona de text și returnăm "break",
    # pentru că Tkinter folosește deja Ctrl+F acolo (mută cursorul un caracter).
    # <Control-F> e varianta cu Caps Lock pornit.
    doc.text_area.bind("<Control-f>", open_find_window)
    doc.text_area.bind("<Control-F>", open_find_window)

    # Ctrl+H deschide înlocuirea. Tot "break", pentru că în zona de text
    # Tkinter folosește Ctrl+H ca Backspace.
    doc.text_area.bind("<Control-h>", open_replace_window)
    doc.text_area.bind("<Control-H>", open_replace_window)

    # Pornim bucla aplicației (ține fereastra deschisă)
    root.mainloop()


if __name__ == "__main__":
    main()
