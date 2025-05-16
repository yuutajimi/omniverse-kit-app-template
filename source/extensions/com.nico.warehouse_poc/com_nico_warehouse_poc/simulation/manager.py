import omni.usd
import omni.kit.commands
from pxr import Gf, UsdGeom, Usd
from typing import Dict, Any, List, Optional

from .path_finder import PathFinder
from .path_navigator import PathNavigator # PathNavigator をインポート
from .animator import Animator # Animator をインポート
from .data_exporter import DataExporter
from ..utils import usdutils, omath # ユーティリティをインポート
from ..core import settings # 設定を読み込むため

# PoC用の設定を定義 (本来は settings.py や外部ファイルから読み込む)
POC_SETTINGS = {
    "Layout_A": {
        "Scenario_1": {
            "start_prim_path": "/World/Layout_A/StartPoints/Start_1", # 開始地点を示すプリムのパス
            "end_prim_path": "/World/Layout_A/EndPoints/End_1",     # 目標地点を示すプリムのパス
            "agent_prim_path": "/World/Agents/SimpleAgent_A",       # 動かすエージェントのプリムパス
            "agent_speed": 2.0,  # units per second
            "output_filename_template": "results/layout_A_scenario_1_results.yaml"
        },
        # 他のシナリオ...
    },
    # 他のレイアウト...
}

class SimulationManager:
    def __init__(self):
        print("SimulationManager initialized.")
        self._path_finder: Optional[PathFinder] = None
        self._animator: Optional[Animator] = None
        self._data_exporter: DataExporter = DataExporter()
        self._current_stage: Optional[Usd.Stage] = None

        try:
            self._path_finder = PathFinder.create() # NavMeshの準備
        except RuntimeError as e:
            print(f"Error initializing PathFinder: {e}")
            self._path_finder = None # エラー時はNoneにしておく

        # アニメーションループのためのイベントサブスクリプション (Animator側で管理する方が良い場合もある)
        # self._event_subs: List[carb.events.ISubscription] = []
        # self._setup_update_event()


    def _get_prim_world_position(self, prim_path: str) -> Optional[Gf.Vec3d]:
        """指定されたプリムのワールド座標を取得する"""
        if not self._current_stage:
            self._current_stage = usdutils.get_stage()
            if not self._current_stage:
                print(f"Error: Stage not found to get prim position for {prim_path}")
                return None

        prim = self._current_stage.GetPrimAtPath(prim_path)
        if not prim.IsValid():
            print(f"Error: Prim not found at {prim_path}")
            return None
        try:
            # UsdGeom.Xformable を使ってワールド座標を取得
            xformable = UsdGeom.Xformable(prim)
            world_transform: Gf.Matrix4d = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
            translation: Gf.Vec3d = world_transform.ExtractTranslation()
            return translation
        except Exception as e:
            print(f"Error getting world position for {prim_path}: {e}")
            return None


    def run_poc_simulation(self, layout_id: str, scenario_id: str):
        """
        PoC仕様に基づいたシミュレーションを実行する。
        パラメータは内部のPOC_SETTINGSから取得する。
        """
        print(f"Attempting to run PoC simulation for Layout: {layout_id}, Scenario: {scenario_id}")
        if not self._path_finder:
            print("Error: PathFinder is not initialized. Cannot run simulation.")
            return

        self._current_stage = usdutils.get_stage() # 最新のステージを取得
        if not self._current_stage:
            print("Error: USD Stage not found.")
            return

        # 1. シナリオ設定の取得
        scenario_config = POC_SETTINGS.get(layout_id, {}).get(scenario_id)
        if not scenario_config:
            print(f"Error: Configuration not found for Layout '{layout_id}', Scenario '{scenario_id}'")
            return

        start_prim_path = scenario_config.get("start_prim_path")
        end_prim_path = scenario_config.get("end_prim_path")
        agent_prim_path = scenario_config.get("agent_prim_path")
        agent_speed = scenario_config.get("agent_speed", 1.0)
        output_filename = scenario_config.get("output_filename_template", "sim_results.yaml")

        if not all([start_prim_path, end_prim_path, agent_prim_path]):
            print("Error: Incomplete prim paths in scenario configuration.")
            return

        # 2. 開始地点と目標地点のワールド座標を取得
        start_pos = self._get_prim_world_position(start_prim_path)
        end_pos = self._get_prim_world_position(end_prim_path)

        if start_pos is None or end_pos is None:
            print("Error: Could not determine start or end position from prims.")
            return

        print(f"Start position: {start_pos}, End position: {end_pos} for agent {agent_prim_path}")

        # 3. 経路探索
        try:
            path_points: List[Gf.Vec3d] = self._path_finder.find(start_pos, end_pos)
            if not path_points or len(path_points) < 2:
                print("Error: Path could not be found or is too short.")
                return
            print(f"Path found with {len(path_points)} points.")
        except Exception as e:
            print(f"Error during path finding: {e}")
            return

        # 4. エージェントプリムの取得とAnimatorの初期化
        agent_prim = self._current_stage.GetPrimAtPath(agent_prim_path)
        if not agent_prim.IsValid():
            print(f"Error: Agent prim not found at {agent_prim_path}")
            return

        # 既存のAnimatorがあれば停止・クリーンアップ
        if self._animator:
            self._animator.stop_animation() # 以前のアニメーションを停止
            self._animator.cleanup()

        self._animator = Animator(agent_prim, path_points, agent_speed)
        self._animator.start_animation(on_complete_callback=lambda: self._on_animation_complete(layout_id, scenario_id, path_points, output_filename))

        print(f"Animation started for agent: {agent_prim_path}")


    def _on_animation_complete(self, layout_id: str, scenario_id: str, path_points: List[Gf.Vec3d], output_filename: str):
        """アニメーション完了時のコールバック"""
        print(f"Animation completed for Layout: {layout_id}, Scenario: {scenario_id}")

        if not path_points or len(path_points) < 1:
            print("Error: Path points are empty, cannot calculate distance.")
            return

        # 5. 結果の計算と出力
        total_distance = 0.0
        for i in range(len(path_points) - 1):
            total_distance += omath.length(path_points[i+1] - path_points[i])

        # PoC仕様の必須項目
        start_coord_dict = {"X": path_points[0][0], "Y": path_points[0][1], "Z": path_points[0][2]}
        end_coord_dict = {"X": path_points[-1][0], "Y": path_points[-1][1], "Z": path_points[-1][2]}

        # PoC仕様の推奨項目
        agent_speed = POC_SETTINGS.get(layout_id, {}).get(scenario_id, {}).get("agent_speed", 1.0)
        estimated_time = total_distance / agent_speed if agent_speed > 0 else 0.0
        path_coords_list = [{"X": p[0], "Y": p[1], "Z": p[2]} for p in path_points]


        simulation_results = {
            "layout_id": layout_id,
            "scenario_id": scenario_id,
            "start_point_coords": start_coord_dict,
            "end_point_coords": end_coord_dict,
            "total_distance": round(total_distance, 3),
            "estimated_time_seconds": round(estimated_time, 3), # 推奨項目
            "path_coordinates": path_coords_list # 推奨項目
        }

        print(f"Results: {simulation_results}")
        self._data_exporter.export_to_yaml(simulation_results, output_filename) # または settings からファイル名取得

        # Animatorのリソース解放 (必要であれば)
        if self._animator:
            self._animator.cleanup() # アニメーションが完了したらクリーンアップ
            self._animator = None


    def cleanup(self):
        print("SimulationManager cleanup.")
        if self._animator:
            self._animator.stop_animation()
            self._animator.cleanup()
            self._animator = None
        # 他に必要なクリーンアップ処理があればここに記述
        # (例: イベントサブスクリプションの解除など)
        # for sub in self._event_subs:
        #     sub.unsubscribe()
        # self._event_subs.clear()