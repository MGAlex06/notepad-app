import tkinter as tk


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

    # Pornim bucla aplicației (ține fereastra deschisă)
    root.mainloop()


if __name__ == "__main__":
    main()
