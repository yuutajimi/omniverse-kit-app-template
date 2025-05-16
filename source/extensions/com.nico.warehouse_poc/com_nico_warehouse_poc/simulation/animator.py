import omni.kit.app
import omni.usd
import carb.events
from pxr import Usd, UsdGeom, Gf
from typing import List, Optional, Callable

from .path_navigator import PathNavigator
from ..utils import transform as transform_utils

class Animator:
    def __init__(self, agent_prim: Usd.Prim, path_points: List[Gf.Vec3d], speed: float = 1.0):
        if not agent_prim or not agent_prim.IsValid():
            raise ValueError("Animator: Agent prim is not valid.")
        if not path_points: # PathNavigator will raise error if points are empty
            raise ValueError("Animator: Path points cannot be empty.")

        self._agent_prim: Usd.Prim = agent_prim
        self._agent_xform: Optional[transform_utils.Transform] = None
        self._is_transform_util_valid = False

        try:
            self._agent_xform = transform_utils.Transform(self._agent_prim)
            self._is_transform_util_valid = True # Assume success if no exception
        except Exception as e:
            print(f"Animator: Error initializing Transform util for {agent_prim.GetPath()}: {e}. Will use fallback.")
            self._is_transform_util_valid = False


        self._path_navigator: PathNavigator = PathNavigator(path_points)
        self._speed: float = abs(speed)
        self._is_animating: bool = False
        self._update_sub: Optional[carb.events.ISubscription] = None
        self._on_complete_callback: Optional[Callable[[], None]] = None
        self._last_time: float = 0.0

        self._set_initial_position()

    def _set_initial_position(self):
        initial_pos = self._path_navigator.evaluate_current_position()
        if self._is_transform_util_valid and self._agent_xform:
            self._agent_xform.position = initial_pos
        else:
            try:
                xform_api = UsdGeom.XformCommonAPI(self._agent_prim)
                if xform_api: # XformCommonAPI is easier for simple translations
                    xform_api.SetTranslate(initial_pos)
                else: # Fallback to Xformable if XformCommonAPI is not suitable/present
                    xformable_prim = UsdGeom.Xformable(self._agent_prim)
                    translate_op = xformable_prim.GetTranslateOp()
                    if not translate_op:
                        translate_op = xformable_prim.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble)
                    if translate_op:
                        translate_op.Set(initial_pos)
            except Exception as e_fallback:
                print(f"Animator Fallback: Error setting initial position for {self._agent_prim.GetPath()}: {e_fallback}")

    def start_animation(self, on_complete_callback: Optional[Callable[[], None]] = None):
        if self._is_animating:
            print("Animator: Animation is already running.")
            return

        if not UsdGeom.Xformable(self._agent_prim).GetPrim().IsValid():
            print(f"Animator Error: Agent prim {self._agent_prim.GetPath()} is not Xformable.")
            if on_complete_callback:
                 on_complete_callback() # Still call callback to signal failure/no-op
            return

        if self._speed <= 1e-6: # Effectively zero speed
            print("Animator: Speed is zero or too low. Animation will not run, calling complete.")
            if on_complete_callback:
                on_complete_callback()
            return

        self._is_animating = True
        self._on_complete_callback = on_complete_callback
        self._last_time = omni.kit.app.get_app().get_time_since_start_ms()

        app_update = omni.kit.app.get_app().get_update_event_stream()
        self._update_sub = app_update.create_subscription_to_pop(
            self._on_update, name="WarehousePocAnimatorUpdate"
        )
        print(f"Animator: Started for {self._agent_prim.GetPath()}.")

    def _on_update(self, e: carb.events.IEvent):
        if not self._is_animating:
            return

        current_time = omni.kit.app.get_app().get_time_since_start_ms()
        delta_time = current_time - self._last_time
        self._last_time = current_time

        if delta_time <= 0:
            return

        distance_to_move = self._speed * delta_time
        self._path_navigator.move_forward(distance_to_move)
        current_position = self._path_navigator.evaluate_current_position()

        if self._is_transform_util_valid and self._agent_xform:
            self._agent_xform.position = current_position
        else: # Fallback
            try:
                xform_api = UsdGeom.XformCommonAPI(self._agent_prim)
                if xform_api:
                    xform_api.SetTranslate(current_position)
                else:
                    xformable_prim = UsdGeom.Xformable(self._agent_prim)
                    translate_op = xformable_prim.GetTranslateOp()
                    if translate_op: # Assuming op exists if initial setup worked
                        translate_op.Set(current_position)
            except Exception as e_fallback_update:
                print(f"Animator Fallback: Error setting update position for {self._agent_prim.GetPath()}: {e_fallback_update}")

        if self._path_navigator.is_finished:
            self.stop_animation() # Stop first
            if self._on_complete_callback:
                self._on_complete_callback() # Then call callback

    def stop_animation(self):
        if not self._is_animating:
            return # Already stopped or never started
        self._is_animating = False
        if self._update_sub:
            self._update_sub.unsubscribe()
            self._update_sub = None
        print(f"Animator: Stopped for {self._agent_prim.GetPath()}.")

    def cleanup(self):
        self.stop_animation()
        self._on_complete_callback = None
        print(f"Animator: Cleaned up for {self._agent_prim.GetPath()}.")