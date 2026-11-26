# Edzésnapló

## Hallgató

Mester Miklós Bence (E9QJVM)

## Feladat leírása

Edzésnapló program, amibe fel lehet vinni az edzéseket (futás, kerékpár, úszás, gyaloglás).
Meg kell adni a dátumot, a sportágat, a távot és az időt, ebből a program kiszámolja a tempót.
Az edzések SQLite adatbázisba kerülnek, a program statisztikát számol belőlük, és az utolsó
10 edzés távját oszlopdiagramon kirajzolja. Lehet sportágra szűrni, törölni, és CSV-be exportálni.

Indítás: `python main.py`

## Modulok és függvények

Tanult modulok:

- tkinter: Tk, Menu, StringVar, Canvas (create_rectangle, create_text, create_line, delete), bind, mainloop
- tkinter.ttk: Label, Entry, Button, Combobox, Frame, LabelFrame, Treeview
- tkinter.messagebox: showinfo, showerror, showwarning, askyesno
- sqlite3: connect, cursor, execute, fetchall, commit
- datetime: now, strftime, strptime
- csv: writer, writerow

Bemutatandó modul:

- statistics: mean (átlag), median (medián), stdev (szórás), mode (leggyakoribb érték)

Saját modul:

- mmb_edzes.py
  - mmb_tempo(tav, perc): tempó kiszámolása perc/km-ben
  - mmb_tempo_szoveg(tempo): a tempót perc:mp formában adja vissza

## Osztály

MMBEdzesApp (mmb_edzes.py), metódusai:

- adatbazis_letrehozas: tábla létrehozása, ha még nincs
- menu_keszites: Fájl és Súgó menü
- felulet_keszites: beviteli mezők, szűrő, táblázat, statisztika, rajzlap
- mentes: új edzés ellenőrzése és mentése
- edzesek_lekerdezese: edzések lekérése az adatbázisból
- lista_frissites: táblázat, statisztika és grafikon frissítése
- statisztika_frissites: statisztika kiszámolása
- grafikon_rajzolas: oszlopdiagram rajzolása
- torles: edzés törlése
- csv_mentes: exportálás CSV fájlba
- hasznalat, nevjegy: súgó ablakok

## Eseménykezelés

- Mentés gomb vagy Enter: edzés mentése
- dupla kattintás egy soron: törlés
- szűrő kiválasztása: lista frissítése
- menüpontok: exportálás, kilépés, súgó

## Szükséges modulok

tkinter, sqlite3, statistics, datetime, csv
