# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from pxr import Usd, UsdGeom, UsdSkel, UsdPhysics, UsdShade, UsdSkel, Sdf, Gf, Tf
import omni.ext
import omni.kit
import carb.events
import omni.usd

import omni.kit.commands
import omni.kit.menu.utils
from omni.kit.menu.utils import MenuItemDescription

import asyncio

from .scripts.GameWorkflow import GameWorkflow


# Functions and vars are available to other extensions as usual in python:
# `ytajimi.test_extension1.some_public_function(x)`
def some_public_function(x: int):
    """This is a public function that can be called from other extensions."""
    print(f"[ytajimi.test_extension1] some_public_function was called with {x}")
    return x**x


# Any class derived from `omni.ext.IExt` in the top level module (defined in
# `python.modules` of `extension.toml`) will be instantiated when the extension
# gets enabled, and `on_startup(ext_id)` will be called. Later when the
# extension gets disabled on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    """This is a blank extension template."""
    # ext_id is the current extension id. It can be used with the extension
    # manager to query additional information, like where this extension is
    # located on the filesystem.
    def on_startup(self, _ext_id):
        """This is called every time the extension is activated."""
        print("[ytajimi.test_extension1] Extension startup")

        # Initialize menu.
        self._init_menu()

    def on_shutdown(self):
        """This is called every time the extension is deactivated. It is used
        to clean up the extension state."""
        print("[ytajimi.test_extension1] Extension shutdown")

        # Term menu.
        self._term_menu()

        self._menu_exit()


    _gameWorkflow = None

    # Menu list.
    _menu_list = None
    _sub_menu_list = None

    # Menu name.
    _menu_name = "Game"

    # ------------------------------------------.
    # Initialize menu.
    # ------------------------------------------.
    def _init_menu (self):
        async def _rebuild_menus ():
            await omni.kit.app.get_app().next_update_async()
            omni.kit.menu.utils.rebuild_menus()

        def menu_select (mode):
            if mode == 1:
                self._menu_start()

            if mode == 2:
                self._menu_exit()

        self._sub_menu_list = [
            MenuItemDescription(name="Start/Reset", onclick_fn=lambda: menu_select(1)),
            MenuItemDescription(name="Exit", onclick_fn=lambda: menu_select(2)),
        ]

        self._menu_list = [
            MenuItemDescription(name="Ball", sub_menu=self._sub_menu_list),
        ]

        # Rebuild with additional menu items.
        omni.kit.menu.utils.add_menu_items(self._menu_list, self._menu_name)
        asyncio.ensure_future(_rebuild_menus())

    # ------------------------------------------.
    # Term menu.
    # It seems that the additional items in the top menu will not be removed.
    # ------------------------------------------.
    def _term_menu (self):
        async def _rebuild_menus ():
            await omni.kit.app.get_app().next_update_async()
            omni.kit.menu.utils.rebuild_menus()

        # Remove and rebuild the added menu items.
        omni.kit.menu.utils.remove_menu_items(self._menu_list, self._menu_name)
        asyncio.ensure_future(_rebuild_menus())

    # ------------------------------------------.
    # Start from menu.
    # ------------------------------------------.
    def _menu_start (self):
        if self._gameWorkflow != None:
            self._gameWorkflow.GameExit()
            self._gameWorkflow = None

        self._gameWorkflow = GameWorkflow()
        self._gameWorkflow.GameStart()

    # ------------------------------------------.
    # Edit from menu.
    # ------------------------------------------.
    def _menu_exit (self):
        if self._gameWorkflow == None:
            return
        self._gameWorkflow.GameExit()
