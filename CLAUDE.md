# Notepad App

Aplicație de tip Notepad pentru Windows, construită ca proiect de învățare cu ajutor AI.

## Stack
- Python 3.12 (mediul virtual este în .venv)
- Tkinter pentru interfață
- pytest pentru teste
- PyInstaller pentru .exe, la final

## Reguli de lucru
- Lucrează la o singură funcție pe rând. Nu adăuga funcții pe care nu le-am cerut.
- Înainte de a scrie cod, spune în 2-3 propoziții ce urmează să faci.
- După fiecare modificare, explică simplu ce face codul, pe înțelesul unui începător.
- Păstrează codul simplu și ușor de citit. Preferă claritatea în fața trucurilor.
- Nu instala pachete noi fără să-mi spui de ce sunt necesare.
- Nu face commit singur. Spune-mi când e momentul și ce mesaj propui.

## Reguli de cod
- Cod doar pentru Windows.
- Citește și scrie fișiere cu encoding="utf-8" explicit.
- Deschide fișierele cu newline="" ca să păstrezi terminațiile de linie.
- Folosește pathlib pentru căi de fișiere.
- Pune logica (fișiere, codificări) separat de interfață, ca să poată fi testată.

## Structura proiectului
- main.py: pornește aplicația
- Fișiere noi doar când e nevoie, cu justificare.

## Comenzi
- Rulare: python main.py
- Teste: pytest