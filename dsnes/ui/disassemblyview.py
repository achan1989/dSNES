# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

import dsnes
from dsnes.ui import events


class DisassemblyView(ttk.Frame):
    def __init__(self, app, master=None):
        super().__init__(master)
        self.app = app
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(1, weight=0)

        self.dasm = dasm = ttk.Treeview(self)
        dasm.grid(column=0, row=0, sticky="nsew")
        dasm["show"] = "tree"  # Hides column headers.
        dasm["selectmode"] = "browse"
        dasm["padding"] = 0
        dasm.column("#0", stretch=True)

        # Map displayed id to to displayed index/actual index/item.
        self.item_lookup = {}
        # Map actual index to displayed id/index/item.
        self.display_lookup = {}

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
        dasm.bind("<<TreeviewSelect>>", self.handle_selection_change)
        app.root.bind(
            events.ANALYSIS_UPDATED, self.handle_analysis_updated, add=True)
        app.root.bind(
            events.FOLLOW, self.handle_follow, add=True)
        app.root.bind(
            events.RETURN, self.handle_return, add=True)

    def handle_dasm_click(self, evt):
        # Prevent resizing columns.
        if self.dasm.identify_region(evt.x, evt.y) == "separator":
            return "break"

    def handle_selection_change(self, *args):
        selection = self.dasm.selection()
        assert len(selection) == 1
        selected_id = selection[0]
        disp_idx, orig_index, _ = self.item_lookup[selected_id]
        self.app.session.line_number = orig_index
        print("<<TreeviewSelect>> id={}, disp_idx={}, orig_idx={}".format(
            selected_id, disp_idx, orig_index))

    def handle_analysis_updated(self, *args):
        print(events.ANALYSIS_UPDATED)
        dasm = self.dasm
        old_items = self.dasm.get_children()
        if old_items:
            dasm.delete(*old_items)
        self.item_lookup.clear()
        self.display_lookup.clear()
        dasm_lines = self.app.session.current_analysis.get_disassembly_lines()
        curr_selected_idx = self.app.session.line_number

        for idx, item in enumerate(dasm_lines):
            self.add_item(item, idx, idx==curr_selected_idx)
        identity, _, _ = self.display_lookup[curr_selected_idx]
        dasm.selection_set(identity)
        dasm.focus_set()
        dasm.focus(identity)
        dasm.see(identity)

        # Resize the column to fit the widest item.
        # This lets the Treeview work properly with the horizontal scrollbar.
        col_width = 0
        for item in dasm.get_children():
            # Need extra mmmmm due to padding weirdness.
            text = dasm.item(item, option="text") + "mmmmm"
            width = self.font.measure(text)
            if col_width < width:
                dasm.column("#0", width=width, minwidth=width)
                col_width = width

    def handle_follow(self, *args):
        print(events.FOLLOW)
        selection = self.dasm.selection()
        assert len(selection) == 1
        selected_id = selection[0]
        _, orig_index, _ = self.item_lookup[selected_id]

        calls = self.app.session.get_calls_from_line(orig_index)
        if len(calls) == 0:
            print("No jump/call from this line")
        elif len(calls) > 1:
            print("More than one jump/call destination from this line")
        else:
            target, state = calls[0]
            self.app.session.follow_call(target, state)
            self.app.root.event_generate(events.ANALYSIS_UPDATED)

    def handle_return(self, *args):
        print(events.RETURN)
        try:
            self.app.session.jump_back()
        except dsnes.interactive.NoOperation:
            pass
        else:
            self.app.root.event_generate(events.ANALYSIS_UPDATED)

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
        self.item_lookup[identity] = (display_index, orig_index, item)
        self.display_lookup[orig_index] = (identity, display_index, item)

    def add_pre_comment(self, item, orig_index):
        lines = item.text.split("\n")
        first = True
        for line in lines:
            text = " " + line
            identity = self.dasm.insert(parent="", index="end", text=text)
            display_index = self.dasm.index(identity)
            self.item_lookup[identity] = (display_index, orig_index, item)
            # This points to the first line of the multi-line entry.
            if first:
                self.display_lookup[orig_index] = \
                    (identity, display_index, item)
                first = False

    def add_error(self, item, orig_index):
        error_msg = "!!!{}!!!".format(item.msg)
        text = " {addr}{pad:<12}  {msg:^73}   {state}".format(
            addr=format_address(item.addr),
            pad="",
            msg=error_msg,
            state=item.state.encode())
        identity = self.dasm.insert(parent="", index="end", text=text)
        display_index = self.dasm.index(identity)
        self.item_lookup[identity] = (display_index, orig_index, item)
        self.display_lookup[orig_index] = (identity, display_index, item)

    def add_disassembly(self, item, orig_index):
        text = (" {addr}:{raw:<11}  {asm:<15s}   {target:<18s}  "
                "{comment:<35s}   {state}".format(
                    addr=format_address(item.operation.addr),
                    raw=" ".join([format(n, "02x")
                                  for n in item.operation.raw]),
                    asm=item.operation.asm_str,
                    target=item.target_str,
                    comment=item.comment,
                    state=item.operation.state.encode()))
        identity = self.dasm.insert(parent="", index="end", text=text)
        display_index = self.dasm.index(identity)
        self.item_lookup[identity] = (display_index, orig_index, item)
        self.display_lookup[orig_index] = (identity, display_index, item)

def format_address(addr):
    if addr < 0 or addr > 0xFFFFFF:
        raise ValueError("Address out of range")
    pbr = (addr & 0xff0000) >> 16
    pc = addr & 0xFFFF
    return "{:02x}:{:04x}".format(pbr, pc)
