# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import argparse

from asciimatics.screen import Screen
from asciimatics.scene import Scene
import asciimatics.exceptions

import dsnes


SHOW_FOREVER = -1


def start():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "project", nargs="?", default=None, help="Optional project to load")
    args = parser.parse_args()

    session = dsnes.interactive.Session()
    if args.project:
        session.to_load = args.project
        start_scene_name = dsnes.ui.PROJECT_LOADING_PAGE
    else:
        start_scene_name = dsnes.ui.START_PAGE

    def ui(screen, start_scene_name=None, last_scene=None):
        scenes = [
            Scene([dsnes.ui.StartPage(screen, session)],
                  duration=SHOW_FOREVER, name=dsnes.ui.START_PAGE),
            Scene([dsnes.ui.LoadingPage(screen, session)],
                  duration=SHOW_FOREVER, name=dsnes.ui.PROJECT_LOADING_PAGE)
        ]
        start_scene = None
        if last_scene:
            start_scene = last_scene
        elif start_scene_name:
            for scene in scenes:
                if scene.name == start_scene_name:
                    start_scene = scene
                    break
            if not start_scene:
                raise RuntimeError(
                    "No scene matches name {!r}".format(start_scene_name))
        screen.play(scenes, stop_on_resize=True, start_scene=start_scene)

    last_scene = None
    while True:
        try:
            Screen.wrapper(ui, arguments=[start_scene_name, last_scene])
            break
        except asciimatics.exceptions.ResizeScreenError as ex:
            last_scene = ex.scene
        except Exception as ex:
            import traceback
            traceback.print_exc()
            import pdb
            pdb.post_mortem()
            break
