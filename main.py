import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import file_io

FILE_TYPES = [("Fișiere text", "*.txt"), ("Toate fișierele", "*.*")]


def main():
    # Fereastra principală a aplicației
    root = tk.Tk()
    root.title("Fără titlu - Notepad")
    root.geometry("800x600")

    # Bara de derulare verticală, lipită de marginea din dreapta
    scrollbar = tk.Scrollbar(root)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Zona de text, care ocupă tot restul ferestrei
    text_area = tk.Text(root, yscrollcommand=scrollbar.set)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Legăm bara de derulare de zona de text
    scrollbar.config(command=text_area.yview)

    # Fișierul deschis acum (None = încă nesalvat) și terminația lui de linie
    current_path = None
    current_newline = "\r\n"

    def update_title():
        if current_path is None:
            root.title("Fără titlu - Notepad")
        else:
            root.title(f"{current_path.name} - Notepad")

    def open_file():
        nonlocal current_path, current_newline
        filename = filedialog.askopenfilename(filetypes=FILE_TYPES)
        if not filename:
            return  # utilizatorul a apăsat Cancel

        try:
            text, newline = file_io.read_file(filename)
        except (OSError, UnicodeDecodeError) as error:
            messagebox.showerror("Eroare", f"Nu am putut deschide fișierul:\n{error}")
            return

        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", text)
        current_path = Path(filename)
        current_newline = newline
        update_title()

    def save_to(path):
        nonlocal current_path
        # "end-1c" = tot textul, fără "\n"-ul pe care Tkinter îl adaugă la final
        text = text_area.get("1.0", "end-1c")
        try:
            file_io.write_file(path, text, current_newline)
        except OSError as error:
            messagebox.showerror("Eroare", f"Nu am putut salva fișierul:\n{error}")
            return

        current_path = Path(path)
        update_title()

    def save_file_as():
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=FILE_TYPES
        )
        if not filename:
            return  # utilizatorul a apăsat Cancel
        save_to(filename)

    def save_file():
        if current_path is None:
            save_file_as()
        else:
            save_to(current_path)

    # Meniul de sus, cu submeniul File
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open...", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_command(label="Save As...", command=save_file_as)
    menubar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menubar)

    # Pornim bucla aplicației (ține fereastra deschisă)
    root.mainloop()


if __name__ == "__main__":
    main()
