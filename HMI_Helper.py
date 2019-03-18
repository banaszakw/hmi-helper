#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Created on Mon Feb 19 13:30:01 2018

@author: banaszakw
"""
import collections
import functools
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

LABELS_NAME = {'cancel': "Anuluj",
               'copy': "Kopiuj",
               'cut': "Wytnij",
               'delete': "Usuń",
               'dupllist': "Lista duplikatów:",
               'err': "Błąd",
               'insert': "Wstaw tekst:",
               'notsearched': "nie szukano",
               'paste': "Wklej",
               'selall': "Zaznacz wszystko",
               'softdupl': "Duplikaty \"miękkie\":",
               'sort': "Sortuj",
               'sorted': "Posortowana lista słów:",
               'strictdupl': "Duplikaty ścisłe:",
               'tosearchsoft': "Szukaj również \"miękkich\" duplikatów"}
ERRORS_MSG = {'input': "W tekście znajdują się niedozwolone znaki lub nie "
                       "wprowadzono żadnego tekstu"}


class AppCore:
    """ Model """
    PATT = re.compile(r"^[\|\s\wĄĆĘŁŃÓŚŻŹąćęłńóśżź]+$")
    SEP = '|'

    def __init__(self):
        self._sortedinput = None  # type List
        self._strict_dupl = None  # type List
        self._soft_dupl = None  # type List
        self.all_dupl = None  # type List

    def teststr(self, s):
        """Sprawdza, czy w tekscie znajduja sie tylko dozwolone znaki i czy
        tekst nie jest pusty.
        """
        if re.search(self.PATT, s.strip()):
            return True
        return False

    def sort_ascend(self, alist):
        """Sortuje listę alfabetycznie, według klucza: najpierw małe litery,
        potem duże.
        """
        sortedlist = sorted(alist,
                            key=lambda w: (w.upper(), w.swapcase()))
        return sortedlist

    def sort_input(self, s):
        """Usuwa znak konca linii, dzieli tekst wg separatora, usuwa spacje,
        slowa skladajace sie ze spacji, puste slowa, zwraca posortowana liste.
        """
        slist = [w.strip() for w in s.splitlines()[0].split(self.SEP)]
        slist = list(filter(None, slist))
        return self.sort_ascend(slist)

    def search_strict_dupl(self, alist):
        """Zwraca posortowaną liste zduplikowanych slow. Przy szukaniu
        duplikatow ma znaczenie rozmiar liter. Szuka tylko `ścisłych duplikatów`.
        """
        duplset = set([x for x in alist if alist.count(x) > 1])
        dupllist = list(duplset)
        return self.sort_ascend(dupllist)

    def search_soft_dupl(self, alist):
        """Zwraca posortowana liste zduplikowanych slow. Szuka TYLKO
        duplikatow rozniacych sie rozmiarem liter. Szuka tylko `miękkich
        duplikatów`.
        """
        dupldict = collections.defaultdict(set)
        for w in alist:
            dupldict[w.lower()].add(w)
        softdupl = [v for k, v in dupldict.items() if len(v) > 1]
        r = functools.reduce(lambda a, b: a | b,
                             softdupl, set())  # pusty set reduce initial val
        return self.sort_ascend(list(r))

    @property
    def sortedinput(self):
        return self._sortedinput

    @sortedinput.setter
    def sortedinput(self, s):
        self._sortedinput = self.sort_input(s)

    @property
    def strict_dupl(self):
        return self.search_strict_dupl(self._sortedinput)

    @property
    def soft_dupl(self):
        return self.search_soft_dupl(self._sortedinput)

    def search_all_dupl(self, alist):
        """Zwraca posortowana liste zduplikowanych slow. Znajduje duplikaty
        ROWNIEZ rozniące się rozmiarem, czyli znajduje wszystkie duplikaty.
        """
        dupldict = collections.defaultdict(list)
        for w in alist:
            dupldict[w.lower()].append(w)
        all_dupl = [v for k, v in dupldict.items() if len(v) > 1]
        r = functools.reduce(lambda a, b: a+b, all_dupl, list())
        all_dupl = self.sort_ascend(set(r))
        self.all_dupl = all_dupl
        return all_dupl


class AppControl:
    """ Controller """

    def __init__(self):
        self.model = AppCore()
        self.create_gui()

    def create_gui(self):
        self.view = AppGui()
        self.view.register(self)
        self.view.mainloop()

    def run(self):
        outmsg = []
        outtext = []
        input_text = self.view.input_text
        if not self.model.teststr(input_text):
            self.view.showerr()
            return
        self.model.sortedinput = input_text
        sortedinput = self.model.sortedinput
        self.view.fill_listbox(sortedinput)
        strict_dupl = self.model.strict_dupl
        outtext += strict_dupl
        outmsg.append(len(strict_dupl))
        self.view.highlight_elem(strict_dupl, 'strict')
        if self.view.to_search_soft:
            softdupl = self.model.soft_dupl
            self.view.highlight_elem(softdupl, 'soft')
            outtext += softdupl
            outmsg.append(len(softdupl))
        self.view.set_statusmsg(*outmsg)
        outtext = self.model.sort_ascend(outtext)
        self.view.insert_output(outtext)


class AppGui:
    """ View """

    bgcol = {'strict': '#6FF', 'soft': '#CFF'}

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(os.path.splitext(os.path.basename(__file__))[0])
        self.controller = None
        self.selected = None
        self.lbls = LABELS_NAME
        self.errmsg = ERRORS_MSG
        self._to_search_soft = tk.BooleanVar()
        self.create_gui()
        self.create_popup_menu()

    def register(self, controller):
        self.controller = controller

    def mainloop(self):
        self.root.mainloop()

    @property
    def input_text(self):
        return self.scrolltext.get('1.0', tk.END)

    @property
    def to_search_soft(self):
        return self._to_search_soft.get()

    def create_inputfield(self):
        frame = ttk.Frame(self.root, padding=5)
        ttk.Label(frame, text=self.lbls['insert']).pack(fill=tk.X, pady=(10, 0))
        self.scrolltext = tk.scrolledtext.ScrolledText(frame,
                                                       height=10, wrap=tk.WORD)
        self.scrolltext.pack(expand=1, fill=tk.BOTH)
        frame.pack(expand=1, fill=tk.BOTH, side=tk.TOP)
        self.scrolltext.bind("<Button-3>", self.show_popup_menu)
        self.scrolltext.bind("<Control-a>", self.select_all)

    def create_listbox(self):
        frame = ttk.Frame(self.root, padding=5)
        ttk.Label(frame,
                  text=self.lbls['sorted']).pack(fill=tk.X, pady=(10, 0))
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(frame)
        self.listbox.pack(expand=1, fill=tk.BOTH, side=tk.TOP)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        frame.pack(expand=1, fill=tk.BOTH, side=tk.TOP)

    def create_outputfield(self):
        frame = ttk.Frame(self.root, padding=5)
        ttk.Label(frame,
                  text=self.lbls['dupllist']).pack(fill=tk.X, pady=(10, 0))
        self.scrolltext_out = tk.scrolledtext.ScrolledText(frame,
                                                           height=10,
                                                           wrap=tk.WORD)
        self.scrolltext_out.pack(expand=1, fill=tk.BOTH)
        frame.pack(expand=1, fill=tk.BOTH, side=tk.TOP)
        self.scrolltext_out.bind("<Button-3>", self.show_popup_menu)

    def create_statusbar(self):
        self.statusmsg0 = tk.StringVar()
        self.statusmsg1 = tk.StringVar()

        frame = ttk.Frame(self.root, padding=5)

        ttk.Label(frame,
                  text=self.lbls['strictdupl']).pack(side=tk.LEFT, padx=(0, 5))
        self.statusbar0 = ttk.Label(frame,
                                    borderwidth=1,
                                    background=self.bgcol['strict'],
                                    relief=tk.SUNKEN,
                                    textvariable=self.statusmsg0, width=10)
        self.statusbar0.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(frame,
                  text=self.lbls['softdupl']).pack(side=tk.LEFT, padx=(0, 5))
        self.statusbar1 = ttk.Label(frame,
                                    borderwidth=1,
                                    background=self.bgcol['soft'],
                                    relief=tk.SUNKEN,
                                    textvariable=self.statusmsg1, width=10)
        self.statusbar1.pack(fill=tk.Y, side=tk.LEFT, padx=(0, 20))
        frame.pack(expand=0, fill=tk.BOTH, side=tk.TOP)

    def create_button(self):
        frame = ttk.Frame(self.root, padding=5)
        # self.to_search_soft = tk.BooleanVar(value=False)
        ch = ttk.Checkbutton(frame,
                             text=self.lbls['tosearchsoft'],
                             variable=self._to_search_soft)
        ch.pack(side=tk.LEFT)
        ttk.Button(frame,
                   command=self._quit,
                   text=self.lbls['cancel'],
                   width=10).pack(side=tk.RIGHT)
        ttk.Button(frame,
                   command=self.run,
                   text=self.lbls['sort'],
                   width=10).pack(side=tk.RIGHT)
        frame.pack(expand=0, fill=tk.BOTH, side=tk.TOP)

    def create_gui(self):
        self.create_inputfield()
        self.create_listbox()
        self.create_outputfield()
        self.create_statusbar()
        self.create_button()

    def create_popup_menu(self):
        self.popup_menu = tk.Menu(self.root, tearoff=0)

        self.popup_menu.add_command(label=self.lbls['cut'],
                                    accelerator="Ctrl+X",
                                    command=lambda: self.cut(self.selected))
        self.popup_menu.add_command(label=self.lbls['copy'],
                                    accelerator="Ctrl+C",
                                    command=lambda: self.copy(self.selected))
        self.popup_menu.add_command(label=self.lbls['paste'],
                                    accelerator="Ctrl+V",
                                    command=lambda: self.mypaste(self.selected))
        self.popup_menu.add_command(label=self.lbls['delete'],
                                    accelerator="Delete",
                                    command=lambda: self.cut(self.selected))
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label=self.lbls['selall'],
                                    accelerator="Ctrl+A",
                                    command=lambda:
                                        self.select_all(self.selected))

    def cut(self, event=None):
        event.event_generate("<<Cut>>")
        return "break"

    def copy(self, event=None):
        event.event_generate("<<Copy>>")
        return "break"

    def mypaste(self, event=None):
        # https://stackoverflow.com/a/46636970
        try:
            event.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass
        event.insert(tk.INSERT, event.clipboard_get())
        event.event_generate("<<Paste>>")
        return "break"

    def show_popup_menu(self, event):
        self.selected = event.widget
        self.popup_menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def select_all(self, event=None):
        # event.tag_add(tk.SEL, '1.0', tk.END)
        self.scrolltext.tag_add(tk.SEL, '1.0', tk.END)
        return "break"

    def fill_listbox(self, alist):
        self.listbox.delete(0, tk.END)
        for elem in alist:
            self.listbox.insert(tk.END, elem)

    def highlight_elem(self, iterable, elem_type):
        for i in range(self.listbox.size()):
            if self.listbox.get(i) in iterable:
                self.listbox.itemconfig(i, background=self.bgcol[elem_type])  # '#FFCCCB'

    def insert_output(self, out):
        self.scrolltext_out.delete('0.0', tk.END)
        self.scrolltext_out.insert(tk.END, '\n'.join(out))

    def showerr(self):
        msg = self.errmsg['input']
        messagebox.showerror(title=self.lbls['err'], message=msg)

    def set_statusmsg(self, msg0, msg1=None):
        if msg1 is None:
            msg1 = self.lbls['notsearched']
        self.statusmsg0.set(msg0)
        self.statusmsg1.set(msg1)

    def run(self):
        self.controller.run()

    def _quit(self):
        self.root.quit()
        self.root.destroy()


def main():
    AppControl()


if __name__ == "__main__":
    main()
