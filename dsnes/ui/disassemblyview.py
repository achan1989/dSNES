# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk


class DisassemblyView(ttk.Treeview):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        columns = ("address", "raw", "asm", "guide", "comment", "state")
        self["columns"] = columns
        self["show"] = "headings"
        self["selectmode"] = "browse"
        self["padding"] = 0

        style = ttk.Style()
        self.font = tkfont.Font(font="TkFixedFont", size=12)
        style.configure("Monospace.Treeview", font=self.font)
        self["style"] = "Monospace.Treeview"

        for col in columns:
            self.column(col, stretch=True)
            self.heading(col, text=col)

        self.insert("", "end", values=["1f:bdb1", ":22 63 f9 1f", "jsl $123456", "[[some_label]]", "; Inline comment goes here, can be long", "p=mxe b=0 d=0"])

        self.bind("<Button-1>", self.handle_click)

    def handle_click(self, evt):
        # Prevent resizing columns.
        if self.identify_region(evt.x, evt.y) == "separator":
            return "break"
