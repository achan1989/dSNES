# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk

class ResizeDialog(simpledialog.Dialog):
    """A version of simpledialog.Dialog with better resize behaviour."""

    def __init__(self, parent, title=None):
        tk.Toplevel.__init__(self, parent)

        self.withdraw() # remain invisible for now
        # If the master is not viewable, don't
        # make the child transient, or else it
        # would be opened withdrawn
        if parent.winfo_viewable():
            self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = ttk.Frame(self)
        body.grid(column=0, row=0, sticky="nesw", padx=5, pady=5)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.initial_focus = self.body(body)

        box = self.buttonbox()
        box.grid(column=0, row=1, sticky="ew")
        self.rowconfigure(1, weight=0)

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                      parent.winfo_rooty()+50))

        self.deiconify() # become visible now

        self.initial_focus.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def buttonbox(self):
        box = ttk.Frame(self)

        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side="right", padx=10, pady=10)
        w = ttk.Button(
            box, text="OK", width=10, command=self.ok, default="active")
        w.pack(side="right", padx=10, pady=10)

        self.bind("<Escape>", self.cancel)

        return box


class TextDialog(ResizeDialog):
    """Like simpledialog.askstring(), but multi-line."""
    def __init__(self, title, prompt, initialvalue=None, parent=None):
        if not parent:
            parent = tk._default_root

        self.prompt = prompt
        self.initialvalue = initialvalue
        super().__init__(parent, title)

    def body(self, master):
        w = tk.Label(master, text=self.prompt, justify="left")
        w.grid(column=0, row=0, padx=5, sticky="w")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=0)

        self.text = tk.Text(master, width=80, height=15, wrap=None, undo=True)
        self.text.grid(column=0, row=1, padx=5, sticky="nesw")
        master.rowconfigure(1, weight=1)

        if self.initialvalue is not None:
            self.text.insert(1.0, self.initialvalue)

        return self.text

    def getresult(self):
        return self.text.get(1.0, "end")

    def validate(self):
        self.result = self.getresult()
        return 1
