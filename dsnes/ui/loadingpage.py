# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import threading

from asciimatics.scene import Scene
from asciimatics.widgets import Button, Frame, Label, Layout
from asciimatics.exceptions import NextScene

import dsnes
from .widgets import EventFrame


def LoadingPage(screen, session):
    return Scene(
        [LoadingPageFrame(screen, session)],
        duration=dsnes.ui.SHOW_FOREVER, name=dsnes.ui.PROJECT_LOADING_PAGE)


class LoadingPageFrame(EventFrame):

    def __init__(self, screen, session):
        super().__init__(
            screen, screen.height, screen.width,
            on_load=self.on_load, has_border=False)

        self.screen = screen
        self.session = session

        layout = Layout([1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Label("Loading..."), 1)
        self.fix()

    def on_load(self):
        # Load project in a background thread, it's very slow.
        def in_background():
            try:
                self.session.load_project()
                def in_gui():
                    raise NextScene(dsnes.ui.ANALYSIS_PAGE)
            except Exception as ex:
                ex_closure = ex
                def in_gui():
                    raise ex_closure

            self.do_in_gui(in_gui)

        t = threading.Thread(
            target=in_background, name="project_loader", daemon=True)
        t.start()
