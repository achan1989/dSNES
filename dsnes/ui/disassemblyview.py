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
        dasm["show"] = "tree"  # Hides column headers.
        dasm["selectmode"] = "browse"
        dasm["padding"] = 0

        # Map displayed item/index to actual item/index (for multi-line items).
        self.item_lookup = {}

        style = ttk.Style()
        self.font = tkfont.Font(name="DasmFont", font="TkFixedFont", size=12)
        style.configure("Monospace.Treeview", font=self.font)
        dasm["style"] = "Monospace.Treeview"

        vscroll = ttk.Scrollbar(self, orient="vertical", command=dasm.yview)
        vscroll.grid(column=1, row=0, sticky="ns")
        dasm['yscrollcommand'] = vscroll.set

        hscroll = ttk.Scrollbar(self, orient="horizontal", command=dasm.xview)
        hscroll.grid(column=0, row=1, sticky="ew")
        dasm['xscrollcommand'] = hscroll.set

        dasm.bind("<Button-1>", self.handle_dasm_click)
        app.root.bind(
            events.ANALYSIS_UPDATED, self.handle_analysis_updated, add=True)

    def handle_dasm_click(self, evt):
        # Prevent resizing columns.
        if self.dasm.identify_region(evt.x, evt.y) == "separator":
            return "break"

    def handle_analysis_updated(self, *args):
        print(events.ANALYSIS_UPDATED)
        dasm = self.dasm
        old_items = self.dasm.get_children()
        if old_items:
            dasm.delete(*old_items)
        self.item_lookup.clear()
        dasm_lines = self.app.session.current_analysis.get_disassembly_lines()
        curr_idx = self.app.session.line_number

        for idx, item in enumerate(dasm_lines):
            self.add_item(item, idx, idx==curr_idx)

    def add_item(self, item, orig_index, is_selected):
        kind = item.kind
        if kind == "label":
            self.add_label(item, orig_index)
        elif kind == "pre-comment":
            self.add_pre_comment(item, orig_index)
        elif kind == "error":
            self.add_error(item, orig_index)
        elif kind == "disassembly":
            self.add_disassembly(item, orig_index)
        else:
            raise ValueError("Unexpected item kind {!r}".format(kind))

    def add_label(self, item, orig_index):
        text = item.text + ":"
        identity = self.dasm.insert(parent="", index="end", text=text)
        display_index = self.dasm.index(identity)
        self.item_lookup[display_index] = (orig_index, item)

    def add_pre_comment(self, item, orig_index):
        lines = item.text.split("\n")
        for line in lines:
            text = " " + line
            identity = self.dasm.insert(parent="", index="end", text=text)
            display_index = self.dasm.index(identity)
            self.item_lookup[display_index] = (orig_index, item)

    def add_error(self, item, orig_index):
        error_msg = "!!!{}!!!".format(item.msg)
        text = " {addr}{pad:<12}  {msg:^73}   {state}".format(
            addr=format_address(item.addr),
            pad="",
            msg=error_msg,
            state=item.state.encode())
        identity = self.dasm.insert(parent="", index="end", text=text)
        display_index = self.dasm.index(identity)
        self.item_lookup[display_index] = (orig_index, item)

    def add_disassembly(self, item, orig_index):
        text = " {addr}:{raw:<11}  {asm:<15s}   {target:<18s}  {comment:<35s}   {state}".format(
            addr=format_address(item.operation.addr),
            raw=" ".join([format(n, "02x") for n in item.operation.raw]),
            asm=item.operation.asm_str,
            target=item.target_str,
            comment=item.comment,
            state=item.operation.state.encode())
        identity = self.dasm.insert(parent="", index="end", text=text)
        display_index = self.dasm.index(identity)
        self.item_lookup[display_index] = (orig_index, item)

def format_address(addr):
    if addr < 0 or addr > 0xFFFFFF:
        raise ValueError("Address out of range")
    pbr = (addr & 0xff0000) >> 16
    pc = addr & 0xFFFF
    return "{:02x}:{:04x}".format(pbr, pc)
