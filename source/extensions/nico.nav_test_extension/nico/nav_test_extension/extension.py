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

import omni.ext
from .control_panel import ControlPanelWindow
import omni.timeline as timeline
from . import nav_sample

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
        print("[nico.nav_test_extension] Extension startup")
        self._control_panel = ControlPanelWindow(title="ControlPanel", width=500, height=500)

        timeline_interface = timeline.get_timeline_interface()
        self._play_event_sub = (
            timeline_interface
                .get_timeline_event_stream()
                .create_subscription_to_pop_by_type(
                    timeline.TimelineEventType.PLAY,
                    self._on_timeline_play
                )
        )
        self._stop_event_sub = (
            timeline_interface
                .get_timeline_event_stream()
                .create_subscription_to_pop_by_type(
                    timeline.TimelineEventType.STOP,
                    self._on_timeline_stop
                )
        )


    def on_shutdown(self):
        """This is called every time the extension is deactivated. It is used
        to clean up the extension state."""
        print("[nico.nav_test_extension] Extension shutdown")
        if self._control_panel:
            self._control_panel.destroy()
        self._control_panel = None

        self._play_event_sub = None
        self._stop_event_sub = None


    def _on_timeline_play(self, event):
        print("aaaaaaa Play")
        nav_sample.run()


    def _on_timeline_stop(self, event):
        print("aaaaaa Stop")
