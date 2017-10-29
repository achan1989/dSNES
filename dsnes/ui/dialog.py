# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import tkinter as tk
from tkinter import simpledialog, messagebox
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


class QueryStringValidated(simpledialog._QueryString):
    """Like simpledialog._QueryString, but with custom validation."""
    def __init__(self, title, prompt, validate_fn, parent=None, **kwargs):
        self.validate_fn = validate_fn
        super().__init__(title, prompt, parent=parent, **kwargs)

    def validate(self):
        try:
            result = self.getresult()
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                self.errormessage + "\nPlease try again",
                parent = self
            )
            return 0

        valid, fail_msg = self.validate_fn(result)
        if not valid:
            messagebox.showwarning(
                "Invalid value",
                fail_msg,
                parent = self
            )
            return 0

        self.result = result
        return 1


class LabelDialog(ResizeDialog):
    """Dialog for modifying a line's labels."""
    def __init__(self, title, prompt, get_labels_fn, validate_fn, add_fn,
                 remove_fn, parent=None, default_new_value=None):
        if not parent:
            parent = tk._default_root

        self.prompt = prompt
        self.get_labels_fn = get_labels_fn
        self.validate_fn = validate_fn
        self.add_fn = add_fn
        self.remove_fn = remove_fn
        self.labels = tk.Variable()
        self.label_listbox = None
        self.made_changes = False
        self.default_new_value = default_new_value
        super().__init__(parent, title)

    def body(self, master):
        w = tk.Label(master, text=self.prompt, justify="left")
        w.grid(column=0, row=0, padx=5, sticky="w")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=0)

        self.label_listbox = label_listbox = tk.Listbox(
            master, listvariable=self.labels, selectmode="extended")
        self.update_list()
        label_listbox.grid(column=0, row=1, padx=5, sticky="nesw")
        master.rowconfigure(1, weight=1)

        list_controls = ttk.Frame(master)
        list_controls.grid(column=0, row=2, sticky="ew")
        master.rowconfigure(2, weight=0)

        w = ttk.Button(list_controls, text="+", width=3, command=self.on_add)
        w.pack(side="left")
        w = ttk.Button(list_controls, text="-", width=3, command=self.on_remove)
        w.pack(side="left")

        return label_listbox

    def buttonbox(self):
        box = ttk.Frame(self)

        w = ttk.Button(box, text="Done", width=10, command=self.cancel)
        w.pack(side="right", padx=10, pady=10)

        self.bind("<Escape>", self.cancel)

        return box

    def update_list(self):
        self.labels.set(self.get_labels_fn())
        n = len(self.labels.get())
        if n <= 6:
            height = 6
        else:
            height = n + 1
        self.label_listbox["height"] = height

    def on_add(self, *args):
        label_dialog = QueryStringValidated(
            title="dSNES", prompt="New label:", validate_fn=self.validate_fn,
            initialvalue=self.default_new_value)
        new_label = label_dialog.result

        if new_label is not None:
            self.add_fn(new_label)
            self.made_changes = True
            self.update_list()

    def on_remove(self, *args):
        selected = self.label_listbox.curselection()
        if not selected:
            return

        labels = self.labels.get()
        for idx in selected:
            label = labels[idx]
            self.remove_fn(label)
            self.made_changes = True

        self.update_list()
