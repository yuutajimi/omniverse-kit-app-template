import omni.kit.app
import omni.usd
import carb.events
from pxr import Usd, UsdGeom, Gf
from typing import List, Optional, Callable

from .path_navigator import PathNavigator
from ..utils import transform as transform_utils # 提供されたtransform.py を利用

class Animator:
    def __init__(self, agent_prim: Usd.Prim, path_points: List[Gf.Vec3d], speed: float = 1.0):
        if not agent_prim or not agent_prim.IsValid():
            raise ValueError("Agent prim is not valid.")
        if not path_points:
            raise ValueError("Path points cannot be empty.")

        self._agent_prim: Usd.Prim = agent_prim
        self._agent_xform: Optional[transform_utils.Transform] = None # 提供されたTransformクラスのインスタンス
        try:
            self._agent_xform = transform_utils.Transform(self._agent_prim)
        except Exception as e:
            print(f"Error initializing Transform for agent {agent_prim.GetPath()}: {e}")
            # Xformableが正しく設定されていない場合など

        self._path_navigator: PathNavigator = PathNavigator(path_points)
        self._speed: float = abs(speed)  # Ensure speed is positive
        self._is_animating: bool = False
        self._update_sub: Optional[carb.events.ISubscription] = None
        self._on_complete_callback: Optional[Callable[[], None]] = None

        # 初期位置にエージェントを配置 (オプション)
        initial_pos = self._path_navigator.evaluate_current_position()
        if self._agent_xform:
            self._agent_xform.position = initial_pos
        else:
            # Fallback if custom Transform class failed
            try:
                xformable_prim = UsdGeom.Xformable(self._agent_prim)
                translate_op = xformable_prim.GetOrderedXformOps_op("xformOp:translate") # 既存のtranslate opを探す
                if not translate_op:
                     translate_op = xformable_prim.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble) # なければ追加
                if translate_op:
                    translate_op.Set(initial_pos)
            except Exception as e_fallback:
                 print(f"Fallback: Error setting initial position for {agent_prim.GetPath()}: {e_fallback}")


    def start_animation(self, on_complete_callback: Optional[Callable[[], None]] = None):
        if self._is_animating:
            print("Animation is already running.")
            return
        if not self._agent_xform and not UsdGeom.Xformable(self._agent_prim).GetPrim().IsValid() : # Xformableではない場合
            print(f"Error: Agent prim {self._agent_prim.GetPath()} is not Xformable or Transform util failed.")
            return
        if self._speed <= 0:
            print("Error: Speed must be positive to start animation.")
            if on_complete_callback: # 速度ゼロでも完了コールバックは呼ぶ
                on_complete_callback()
            return

        self._is_animating = True
        self._on_complete_callback = on_complete_callback
        self._last_time = omni.kit.app.get_app().get_update_time() # デルタタイム計算用

        # Omniverseのアップデートイベントにサブスクライブしてアニメーションループを開始
        app_update = omni.kit.app.get_app().get_update_event_stream()
        self._update_sub = app_update.create_subscription_to_pop(
            self._on_update, name="WarehousePocAnimatorUpdate"
        )
        print(f"Animator started for {self._agent_prim.GetPath()}.")

    def _on_update(self, e: carb.events.IEvent):
        if not self._is_animating:
            return

        current_time = omni.kit.app.get_app().get_update_time()
        delta_time = current_time - self._last_time
        self._last_time = current_time

        if delta_time <= 0: # デルタタイムが0以下の場合は何もしない
            return

        distance_to_move = self._speed * delta_time
        self._path_navigator.move_forward(distance_to_move)
        current_position = self._path_navigator.evaluate_current_position()

        if self._agent_xform:
            self._agent_xform.position = current_position
        else: # Fallback
             try:
                xformable_prim = UsdGeom.Xformable(self._agent_prim)
                translate_op = xformable_prim.GetOrderedXformOps_op("xformOp:translate")
                if translate_op:
                    translate_op.Set(current_position)
             except Exception as e_fallback_update:
                 print(f"Fallback: Error setting position for {self._agent_prim.GetPath()}: {e_fallback_update}")


        # アニメーション完了チェック
        # PathNavigatorが終点に到達したかを判定するフラグやメソッドがPathNavigatorにあるとより良い
        # ここでは、PathNavigatorのインデックスが最後のポイントに達したら完了とみなす
        if self._path_navigator._current_index >= len(self._path_navigator.points) - 1 and \
           self._path_navigator._current_progress >= 1.0: # 最後のセグメントの終端にほぼ到達
            self.stop_animation()
            if self._on_complete_callback:
                self._on_complete_callback()

    def stop_animation(self):
        if not self._is_animating:
            return
        self._is_animating = False
        if self._update_sub:
            self._update_sub.unsubscribe()
            self._update_sub = None
        print(f"Animator stopped for {self._agent_prim.GetPath()}.")

    def cleanup(self):
        self.stop_animation() # 念のため停止
        self._on_complete_callback = None # コールバック参照をクリア
        print(f"Animator cleaned up for {self._agent_prim.GetPath()}.")