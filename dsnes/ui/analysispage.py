# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import threading
import types

from asciimatics.scene import Scene
from asciimatics.widgets import Button, Frame, Label, Layout
from asciimatics.exceptions import NextScene

import dsnes
from .widgets import BetterFrame


def AnalysisPage(screen, session):
    menu_height = 10
    view_height = screen.height - menu_height

    page = types.SimpleNamespace()
    page.screen = screen
    page.prompt_frame = PromptFrame(page, view_height, screen.width, session)
    page.view_frame = ViewFrame(page, view_height, screen.width, session)
    page.menu_frame = MenuFrame(page, menu_height, screen.width, session)
    
    return Scene(
        [page.prompt_frame, page.view_frame, page.menu_frame],
        duration=dsnes.ui.SHOW_FOREVER, name=dsnes.ui.ANALYSIS_PAGE)


class PromptFrame(BetterFrame):

    def __init__(self, page, height, width, session):
        super().__init__(
            page.screen, height, width, y=0,
            on_load=None, has_border=True)

        self.page = page
        self.session = session

        layout = Layout([1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(
            Label("Select an operation in the menu below to begin."),
            1)
        self.fix()


class ViewFrame(BetterFrame):

    def __init__(self, page, height, width, session):
        super().__init__(
            page.screen, height, width, y=0,
            hidden=True, on_load=None, has_border=True)

        self.page = page
        self.session = session

        layout = Layout([1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Label("Analysis output goes here..."), 1)
        self.fix()


class MenuFrame(BetterFrame):

    def __init__(self, page, height, width, session):
        super().__init__(
            page.screen, height, width, y=page.screen.height-height,
            on_load=None, has_border=True)

        self.page = page
        self.session = session

        layout = Layout([1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Label("Analysis menu goes here..."), 1)
        layout.add_widget(Button("Toggle", on_click=self.toggle_view), 1)
        self.fix()

    def toggle_view(self):
        page = self.page
        if page.prompt_frame.is_hidden:
            page.prompt_frame.show()
            page.view_frame.hide()
        else:
            page.view_frame.show()
            page.prompt_frame.hide()
