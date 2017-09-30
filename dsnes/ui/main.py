# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

import dsnes
from dsnes.ui import events


MENU_FILE = "File"
MENU_ITEM_OPEN_PROJECT = "Open Project..."
MENU_ITEM_EXIT = "Exit"

MENU_SEARCH = "Search"
MENU_ITEM_GOTO = "Goto..."


class MainWindow:
    def __init__(self):
        self.session = dsnes.interactive.Session()

        self.root = root = tk.Tk()
        root.title("dSNES")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        root.minsize(300, 150)

        root.option_add('*tearOff', tk.FALSE)
        self.menu_bar = menu_bar = tk.Menu(root)
        root["menu"] = menu_bar

        self.menu_file = menu_file = tk.Menu(menu_bar)
        menu_file.add_command(
            label=MENU_ITEM_OPEN_PROJECT, accelerator="Ctrl+O",
            command=self.on_open_project_menu)
        root.bind(
            "<Control-o>", lambda _e: menu_file.invoke(MENU_ITEM_OPEN_PROJECT))
        menu_file.add_separator()
        menu_file.add_command(label=MENU_ITEM_EXIT, command=self.root.destroy)
        menu_bar.add_cascade(label=MENU_FILE, menu=menu_file)

        self.menu_search = menu_search = tk.Menu(menu_bar)
        menu_search.add_command(
            label=MENU_ITEM_GOTO, accelerator="Ctrl+G",
            command=self.on_goto)
        root.bind("<Control-g>", lambda _e: menu_search.invoke(MENU_ITEM_GOTO))
        menu_bar.add_cascade(label=MENU_SEARCH, menu=menu_search)

        self.mainframe = mainframe = ttk.Frame(root)
        mainframe.grid(column=0, row=0, sticky="nesw")
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        self.dasm_view = dasm_view = dsnes.ui.DisassemblyView(
            app=self, master=mainframe)
        dasm_view.columnconfigure(0, weight=1)
        dasm_view.rowconfigure(0, weight=1)

        self.progress_bar = progress_bar = ttk.Progressbar(
            mainframe, orient="horizontal", mode="indeterminate")
        progress_bar.columnconfigure(0, weight=1)
        progress_bar.rowconfigure(0, weight=1)

        root.bind(events.PROJECT_CLOSED, self.handle_project_closed, add=True)
        root.bind(events.PROJECT_LOADING, self.handle_project_loading, add=True)
        root.bind(events.PROJECT_LOADED, self.handle_project_loaded, add=True)
        root.event_generate(events.PROJECT_CLOSED)

    def run(self):
        return self.root.mainloop()

    def handle_project_closed(self, *args):
        print(events.PROJECT_CLOSED)
        self.menu_bar.entryconfig(MENU_SEARCH, state="disabled")
        self.menu_search.entryconfig(MENU_ITEM_GOTO, state="disabled")
        self.menu_file.entryconfig(MENU_ITEM_OPEN_PROJECT, state="normal")
        self.hide_dasm_view()
        self.hide_progress_bar()

    def handle_project_loading(self, *args):
        print(events.PROJECT_LOADING)
        self.menu_file.entryconfig(MENU_ITEM_OPEN_PROJECT, state="disabled")
        self.hide_dasm_view()
        self.show_progress_bar()

    def handle_project_loaded(self, *args):
        print(events.PROJECT_LOADED)
        self.menu_bar.entryconfig(MENU_SEARCH, state="normal")
        self.menu_search.entryconfig(MENU_ITEM_GOTO, state="normal")
        self.menu_file.entryconfig(MENU_ITEM_OPEN_PROJECT, state="normal")
        self.hide_progress_bar()
        self.show_dasm_view()

    def show_dasm_view(self):
        self.dasm_view.grid(column=0, row=0, sticky="nesw")

    def hide_dasm_view(self):
        self.dasm_view.grid_remove()

    def show_progress_bar(self):
        self.progress_bar.grid(column=0, row=0, sticky="ew")
        self.progress_bar.start()

    def hide_progress_bar(self):
        self.progress_bar.grid_remove()
        self.progress_bar.stop()

    def start_background_task(self, task_fn, name=None):
        """Perform a task in a background thread.

        The task must be contained within a function that takes no parameters.
        The task will be executed in a background thread, and must not interact
        with Tk objects.
        The task must return a result function that takes no parameters.

        The result function will be executed in the GUI thread, and can be used
        to interact with TK objects (e.g. to update the GUI with the results of
        the background task).
        """
        def wrap_task(result_queue):
            result = None
            error = None
            try:
                result = task_fn()
            except Exception as ex:
                ex_closure = ex
                def error():
                    raise ex_closure
            else:
                if result and callable(result):
                    result_queue.put_nowait(result)
                else:
                    def error():
                        raise TypeError(
                            "Background task named {!r} returned a "
                            "non-callable result {!r}".format(name, result))
            if error:
                result_queue.put_nowait(error)

        result_queue = queue.Queue()
        t = threading.Thread(
            target=wrap_task, name=name, args=(result_queue,), daemon=True)
        t.start()
        self.root.after(200, self._check_background_tasks, result_queue)

    def _check_background_tasks(self, result_queue):
        """Periodic check to see if background tasks have completed."""
        try:
            result_fn = result_queue.get_nowait()
        except queue.Empty:
            self.root.after(200, self._check_background_tasks, result_queue)
        else:
            result_fn()

    def on_open_project_menu(self, *args):
        dir_path = tk.filedialog.askdirectory(
            parent=self.root,
            title="Choose a Project Directory",
            mustexist=True)
        if dir_path != "":
            self.root.event_generate(events.PROJECT_LOADING)
            def task():
                try:
                    self.session.load_project(dir_path)
                    def in_gui():
                        self.root.event_generate(events.PROJECT_LOADED)
                except Exception as ex:
                    ex_closure = ex
                    def in_gui():
                        self.root.event_generate(events.PROJECT_CLOSED)
                        messagebox.showerror(
                            message="Couldn't load project.\n\n{}".format(
                                ex_closure))
                return in_gui
            self.start_background_task(task, name="project_loader")

    def on_goto(self, *args):
        address = tk.simpledialog.askinteger(
            title="dSNES", prompt="New analysis at address:",
            initialvalue="0x",
            minvalue=0, maxvalue=0xffffff)
        self.session.new_analysis(address)
        self.root.event_generate(events.ANALYSIS_UPDATED)


def start():
    MainWindow().run()
