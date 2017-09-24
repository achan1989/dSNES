# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog

import dsnes


class MainWindow:
    def __init__(self):
        self.session = dsnes.interactive.Session()
        self.root = root = tk.Tk()
        self.mainframe = mainframe = ttk.Frame(root)

        root.option_add('*tearOff', tk.FALSE)
        self.menu_bar = menu_bar = tk.Menu(root)
        root["menu"] = menu_bar

        self.menu_file = menu_file = tk.Menu(menu_bar)
        menu_file.add_command(
            label="Open Project", command=self.on_open_project_menu)
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="File", menu=menu_file)

    def run(self):
        return self.root.mainloop()

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

    def on_open_project_menu(self):
        dir_path = tk.filedialog.askdirectory(
            parent=self.root,
            title="Choose a Project Directory",
            mustexist=True)
        if dir_path != "":
            self.menu_file.entryconfig("Open Project", state="disabled")
            def task():
                self.session.load_project(dir_path)
                def in_gui():
                    self.menu_file.entryconfig("Open Project", state="normal")
                    # TODO: load widget?
                return in_gui
            self.start_background_task(task, name="project_loader")


def start():
    MainWindow().run()
