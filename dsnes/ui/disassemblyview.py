# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

import dsnes
from dsnes.ui import events


MENU_SEARCH = "Search"
MENU_ITEM_GOTO = "Goto..."
MENU_ITEM_FOLLOW = "Follow jump/call"
MENU_ITEM_RETURN = "Undo follow"


class DisassemblyView(ttk.Frame):
    def __init__(self, app, master=None):
        super().__init__(master)
        self.app = app
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(1, weight=0)

        root = app.root

        self.menu_search = menu_search = tk.Menu(app.menu_bar)
        menu_search.add_command(
            label=MENU_ITEM_FOLLOW, accelerator="Right",
            command=self.on_follow)
        root.bind("<Right>", lambda _e: menu_search.invoke(MENU_ITEM_FOLLOW))
        menu_search.add_command(
            label=MENU_ITEM_RETURN, accelerator="Left",
            command=self.on_return)
        root.bind("<Left>", lambda _e: menu_search.invoke(MENU_ITEM_RETURN))
        menu_search.add_separator()
        menu_search.add_command(
            label=MENU_ITEM_GOTO, accelerator="Ctrl+G",
            command=self.on_goto)
        root.bind("<Control-g>", lambda _e: menu_search.invoke(MENU_ITEM_GOTO))
        app.menu_bar.add_cascade(label=MENU_SEARCH, menu=menu_search)

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
        dasm.bind("<Home>", self.handle_dasm_home)
        dasm.bind("<End>", self.handle_dasm_end)
        dasm.bind("<<TreeviewSelect>>", self.handle_selection_change)
        root.bind(
            events.PROJECT_CLOSED, self.handle_project_closed, add=True)
        root.bind(
            events.PROJECT_LOADED, self.handle_project_loaded, add=True)
        root.bind(
            events.ANALYSIS_UPDATED, self.handle_analysis_updated, add=True)
        root.bind(
            events.FOLLOW, self.handle_follow, add=True)
        root.bind(
            events.RETURN, self.handle_return, add=True)

    def get_selected(self):
        selection = self.dasm.selection()
        assert len(selection) == 1
        selected_id = selection[0]
        display_index, orig_index, item = self.item_lookup[selected_id]
        return selected_id, display_index, orig_index, item

    def handle_project_closed(self, *args):
        print(events.PROJECT_CLOSED + " dasmview")
        menu_bar = self.app.menu_bar
        menu_search = self.menu_search

        menu_bar.entryconfig(MENU_SEARCH, state="disabled")
        menu_search.entryconfig(MENU_ITEM_GOTO, state="disabled")
        menu_search.entryconfig(MENU_ITEM_FOLLOW, state="disabled")
        menu_search.entryconfig(MENU_ITEM_RETURN, state="disabled")

    def handle_project_loaded(self, *args):
        print(events.PROJECT_LOADED + " dasmview")
        menu_bar = self.app.menu_bar
        menu_search = self.menu_search

        menu_bar.entryconfig(MENU_SEARCH, state="normal")
        menu_search.entryconfig(MENU_ITEM_GOTO, state="normal")

    def handle_dasm_click(self, evt):
        # Prevent resizing columns.
        if self.dasm.identify_region(evt.x, evt.y) == "separator":
            return "break"

    def handle_dasm_home(self, evt):
        items = self.dasm.get_children()
        if not items:
            return
        self.dasm.selection_set(items[0])

    def handle_dasm_end(self, evt):
        items = self.dasm.get_children()
        if not items:
            return
        self.dasm.selection_set(items[-1])

    def handle_selection_change(self, *args):
        selected_id, display_index, orig_index, item = self.get_selected()
        self.app.session.line_number = orig_index
        self.dasm.focus_set()
        self.dasm.focus(selected_id)
        self.dasm.see(selected_id)
        print(
            "<<TreeviewSelect>> id={}, display_index={}, orig_index={}".format(
                selected_id, display_index, orig_index))

        # Can we follow a jump/call?
        calls = self.app.session.get_calls_from_line(orig_index)
        if len(calls) == 0:
            follow_state = "disabled"
        else:
            follow_state = "normal"
        self.menu_search.entryconfig(MENU_ITEM_FOLLOW, state=follow_state)

    def handle_analysis_updated(self, *args):
        print(events.ANALYSIS_UPDATED + " dasmview")
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

        menu_search = self.menu_search
        if self.app.session.current_analysis:

            if self.app.session.can_jump_back():
                back_state = "normal"
            else:
                back_state = "disabled"
            menu_search.entryconfig(MENU_ITEM_RETURN, state=back_state)
        else:
            menu_search.entryconfig(MENU_ITEM_RETURN, state="disabled")

    def on_follow(self, *args):
        self.app.root.event_generate(events.FOLLOW)

    def on_return(self, *args):
        self.app.root.event_generate(events.RETURN)

    def on_goto(self, *args):
        address = tk.simpledialog.askinteger(
            title="dSNES", prompt="New analysis at address:",
            initialvalue="0x",
            minvalue=0, maxvalue=0xffffff)
        if address is not None:
            self.app.session.new_analysis(address)
            self.app.root.event_generate(events.ANALYSIS_UPDATED)

    def handle_follow(self, *args):
        print(events.FOLLOW + " dasmview")
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
        print(events.RETURN + " dasmview")
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
