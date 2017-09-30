# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from dsnes.ui import events


class DisassemblyView(ttk.Frame):
    def __init__(self, app, master=None):
        super().__init__(master)
        self.app = app
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.dasm = dasm = ttk.Treeview(self)
        dasm.grid(column=0, row=0, sticky="nsew")
        columns = ("address", "raw", "asm", "guide", "comment", "state")
        dasm["columns"] = columns
        dasm["show"] = "tree"  # Hides column headers.
        dasm["selectmode"] = "browse"
        dasm["padding"] = 0

        style = ttk.Style()
        self.font = tkfont.Font(name="DasmFont", font="TkFixedFont", size=12)
        style.configure("Monospace.Treeview", font=self.font)
        dasm["style"] = "Monospace.Treeview"

        # Hide the empty "item" column.
        dasm.column("#0", width=0, stretch=False)
        # Columns stay at their given size, except for the comment, which
        # changes based on the size of the window.
        for col in columns:
            dasm.column(col, stretch=False, width=1)
            dasm.heading(col, text=col)
        dasm.column("comment", stretch=True)

        vscroll = ttk.Scrollbar(self, orient="vertical", command=dasm.yview)
        vscroll.grid(column=1, row=0, sticky="ns")
        dasm['yscrollcommand'] = vscroll.set

        hscroll = ttk.Scrollbar(self, orient="horizontal", command=dasm.xview)
        hscroll.grid(column=0, row=1, sticky="ew")
        dasm['xscrollcommand'] = hscroll.set

        example_item = ["1f:bdb1", ":22 63 f9 1f", "jsl $123456", "[[some_label]]", "; Inline comment goes here, can be long", "p=mxe b=0 d=0"]
        dasm.insert("", "end", values=example_item)

        # Set column width to fit the width of the text.
        # TODO: re-visit this when populating with real data.
        # TODO: need to set the columns to the widest across all items.
        # TODO: needs padding.
        for idx, txt in enumerate(example_item):
            width = self.font.measure(txt)
            if dasm.column(idx, option="width") < width:
                dasm.column(idx, width=width, minwidth=width)

        dasm.bind("<Button-1>", self.handle_dasm_click)
        app.root.bind(
            events.ANALYSIS_UPDATED, self.handle_analysis_updated, add=True)

    def handle_dasm_click(self, evt):
        # Prevent resizing columns.
        if self.dasm.identify_region(evt.x, evt.y) == "separator":
            return "break"

    def handle_analysis_updated(self, *args):
        print(events.ANALYSIS_UPDATED)
        self.dasm.delete(self.dasm.get_children())
        dasm_lines = self.app.session.current_analysis.get_disassembly_lines()

        for item in dasm_lines:
            print(item)
