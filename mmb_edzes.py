import csv
import sqlite3
import statistics
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

ADATBAZIS = 'edzesek.db'
EXPORT_FAJL = 'edzesek_export.csv'
TIPUSOK = ['Futás', 'Kerékpár', 'Úszás', 'Gyaloglás']
SZINEK = {'Futás': '#e4572e', 'Kerékpár': '#2e86ab', 'Úszás': '#17bebb', 'Gyaloglás': '#76b041'}


def mmb_tempo(tav, perc):
    if tav <= 0:
        return 0
    return perc / tav


def mmb_tempo_szoveg(tempo):
    perc = int(tempo)
    mp = round((tempo - perc) * 60)
    if mp == 60:
        perc += 1
        mp = 0
    return f'{perc}:{mp:02d} perc/km'


class MMBEdzesApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Edzésnapló')
        self.root.geometry('780x590')
        self.root.resizable(False, False)
        self.adatbazis_letrehozas()
        self.menu_keszites()
        self.felulet_keszites()
        self.lista_frissites()

    def adatbazis_letrehozas(self):
        with sqlite3.connect(ADATBAZIS) as conn:
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS edzesek (datum TEXT, tipus TEXT, tav REAL, ido REAL)')
            conn.commit()

    def menu_keszites(self):
        menusor = tk.Menu(self.root)

        fajl = tk.Menu(menusor, tearoff=0)
        fajl.add_command(label='Exportálás CSV-be', command=self.csv_mentes)
        fajl.add_separator()
        fajl.add_command(label='Kilépés', command=self.root.destroy)
        menusor.add_cascade(label='Fájl', menu=fajl)

        sugo = tk.Menu(menusor, tearoff=0)
        sugo.add_command(label='Használat', command=self.hasznalat)
        sugo.add_command(label='Névjegy', command=self.nevjegy)
        menusor.add_cascade(label='Súgó', menu=sugo)

        self.root.config(menu=menusor)

    def felulet_keszites(self):
        bevitel = ttk.LabelFrame(self.root, text='Új edzés')
        bevitel.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='we')

        ttk.Label(bevitel, text='Dátum').grid(row=0, column=0, padx=5, pady=(5, 0))
        self.datum = tk.StringVar(value=datetime.now().strftime('%Y.%m.%d'))
        ttk.Entry(bevitel, textvariable=self.datum, width=12).grid(row=1, column=0, padx=5, pady=5)

        ttk.Label(bevitel, text='Típus').grid(row=0, column=1, padx=5, pady=(5, 0))
        self.tipus = tk.StringVar(value=TIPUSOK[0])
        tipus_lista = ttk.Combobox(bevitel, textvariable=self.tipus, values=TIPUSOK, state='readonly', width=12)
        tipus_lista.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(bevitel, text='Táv (km)').grid(row=0, column=2, padx=5, pady=(5, 0))
        self.tav = tk.StringVar()
        self.tav_mezo = ttk.Entry(bevitel, textvariable=self.tav, width=10)
        self.tav_mezo.grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(bevitel, text='Idő (perc)').grid(row=0, column=3, padx=5, pady=(5, 0))
        self.ido = tk.StringVar()
        ttk.Entry(bevitel, textvariable=self.ido, width=10).grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(bevitel, text='Mentés', command=self.mentes).grid(row=1, column=4, padx=15, pady=5)

        szuro_keret = ttk.Frame(self.root)
        szuro_keret.grid(row=1, column=0, padx=10, sticky='w')
        ttk.Label(szuro_keret, text='Szűrés:').pack(side='left')
        self.szuro = tk.StringVar(value='Mind')
        szuro_lista = ttk.Combobox(szuro_keret, textvariable=self.szuro, values=['Mind'] + TIPUSOK,
                                   state='readonly', width=12)
        szuro_lista.pack(side='left', padx=5)
        szuro_lista.bind('<<ComboboxSelected>>', lambda e: self.lista_frissites())

        oszlopok = [('datum', 'Dátum', 90), ('tipus', 'Típus', 90), ('tav', 'Táv (km)', 70),
                    ('ido', 'Idő (perc)', 70), ('tempo', 'Tempó', 110)]
        self.tablazat = ttk.Treeview(self.root, columns=[o[0] for o in oszlopok], show='headings', height=11)
        for nev, felirat, szelesseg in oszlopok:
            self.tablazat.heading(nev, text=felirat)
            self.tablazat.column(nev, width=szelesseg, anchor='center')
        self.tablazat.grid(row=2, column=0, padx=10, pady=5)
        self.tablazat.bind('<Double-1>', self.torles)

        stat_keret = ttk.LabelFrame(self.root, text='Statisztika')
        stat_keret.grid(row=2, column=1, padx=10, pady=5, sticky='nwe')
        self.statisztika = ttk.Label(stat_keret, text='', justify='left', font='Arial 10')
        self.statisztika.pack(padx=10, pady=10, anchor='w')

        self.rajzlap = tk.Canvas(self.root, width=760, height=170, bg='white')
        self.rajzlap.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.root.bind('<Return>', lambda e: self.mentes())

    def mentes(self):
        try:
            datetime.strptime(self.datum.get(), '%Y.%m.%d')
        except ValueError:
            messagebox.showerror('Hiba', 'A dátumot így add meg: ÉÉÉÉ.HH.NN')
            return
        try:
            tav = float(self.tav.get().replace(',', '.'))
            ido = float(self.ido.get().replace(',', '.'))
        except ValueError:
            messagebox.showerror('Hiba', 'A táv és az idő csak szám lehet!')
            return
        if tav <= 0 or ido <= 0:
            messagebox.showwarning('Figyelem', 'A táv és az idő legyen nagyobb nullánál!')
            return

        with sqlite3.connect(ADATBAZIS) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO edzesek VALUES (?, ?, ?, ?)', (self.datum.get(), self.tipus.get(), tav, ido))
            conn.commit()

        self.tav.set('')
        self.ido.set('')
        self.tav_mezo.focus()
        self.lista_frissites()

    def edzesek_lekerdezese(self):
        with sqlite3.connect(ADATBAZIS) as conn:
            cursor = conn.cursor()
            if self.szuro.get() == 'Mind':
                cursor.execute('SELECT ROWID, * FROM edzesek ORDER BY datum')
            else:
                cursor.execute('SELECT ROWID, * FROM edzesek WHERE tipus = ? ORDER BY datum', (self.szuro.get(),))
            return cursor.fetchall()

    def lista_frissites(self):
        for sor in self.tablazat.get_children():
            self.tablazat.delete(sor)

        edzesek = self.edzesek_lekerdezese()
        for azon, datum, tipus, tav, ido in edzesek:
            tempo = mmb_tempo_szoveg(mmb_tempo(tav, ido))
            self.tablazat.insert('', 'end', iid=azon, values=(datum, tipus, f'{tav:g}', f'{ido:g}', tempo))

        self.statisztika_frissites(edzesek)
        self.grafikon_rajzolas(edzesek)

    def statisztika_frissites(self, edzesek):
        if not edzesek:
            self.statisztika.config(text='Még nincs rögzített edzés.')
            return

        tavok = [e[3] for e in edzesek]
        tempok = [mmb_tempo(e[3], e[4]) for e in edzesek]
        tipusok = [e[2] for e in edzesek]
        szoras = statistics.stdev(tavok) if len(tavok) > 1 else 0

        szoveg = f'Edzések száma: {len(edzesek)}\n'
        szoveg += f'Összes táv: {sum(tavok):.1f} km\n'
        szoveg += f'Átlagos táv: {statistics.mean(tavok):.2f} km\n'
        szoveg += f'Táv mediánja: {statistics.median(tavok):.2f} km\n'
        szoveg += f'Táv szórása: {szoras:.2f} km\n'
        szoveg += f'Átlagos tempó: {mmb_tempo_szoveg(statistics.mean(tempok))}\n'
        szoveg += f'Leggyakoribb: {statistics.mode(tipusok)}'
        self.statisztika.config(text=szoveg)

    def grafikon_rajzolas(self, edzesek):
        self.rajzlap.delete('all')
        utolsok = edzesek[-10:]
        if not utolsok:
            self.rajzlap.create_text(380, 85, text='Nincs megjeleníthető adat', font='Arial 11')
            return

        self.rajzlap.create_text(10, 8, text='Az utolsó 10 edzés távja (km)', anchor='nw', font='Arial 9 bold')
        legnagyobb = max(e[3] for e in utolsok)
        szelesseg = 60

        for i, edzes in enumerate(utolsok):
            magassag = edzes[3] / legnagyobb * 110
            x = 40 + i * (szelesseg + 12)
            self.rajzlap.create_rectangle(x, 150 - magassag, x + szelesseg, 150, fill=SZINEK[edzes[2]], outline='')
            self.rajzlap.create_text(x + szelesseg / 2, 147 - magassag, text=f'{edzes[3]:g}', anchor='s')
            self.rajzlap.create_text(x + szelesseg / 2, 160, text=edzes[1][5:], font='Arial 8')

        atlag = statistics.mean([e[3] for e in utolsok])
        y = 150 - atlag / legnagyobb * 110
        self.rajzlap.create_line(30, y, 750, y, dash=(4, 3), fill='gray')
        self.rajzlap.create_text(750, y - 2, text=f'átlag {atlag:.1f}', anchor='se', fill='gray', font='Arial 8')

    def torles(self, event):
        sor = self.tablazat.identify_row(event.y)
        if not sor:
            return
        if messagebox.askyesno('Törlés', 'Biztosan törlöd a kijelölt edzést?'):
            with sqlite3.connect(ADATBAZIS) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM edzesek WHERE ROWID = ?', (sor,))
                conn.commit()
            self.lista_frissites()

    def csv_mentes(self):
        edzesek = self.edzesek_lekerdezese()
        with open(EXPORT_FAJL, 'w', newline='', encoding='utf-8') as fajl:
            writer = csv.writer(fajl, delimiter=';')
            writer.writerow(['Dátum', 'Típus', 'Táv (km)', 'Idő (perc)', 'Tempó'])
            for azon, datum, tipus, tav, ido in edzesek:
                writer.writerow([datum, tipus, tav, ido, mmb_tempo_szoveg(mmb_tempo(tav, ido))])
        messagebox.showinfo('Exportálás', f'{len(edzesek)} edzés mentve ide: {EXPORT_FAJL}')

    def hasznalat(self):
        messagebox.showinfo('Használat', 'Töltsd ki a mezőket, majd nyomd meg a Mentés gombot vagy az Entert.\n'
                                         'Egy edzést dupla kattintással lehet törölni.\n'
                                         'A szűrővel csak egy sportág edzései látszanak.')

    def nevjegy(self):
        messagebox.showinfo('Névjegy', 'Edzésnapló\nKészítette: Mester Miklós Bence\n2026')