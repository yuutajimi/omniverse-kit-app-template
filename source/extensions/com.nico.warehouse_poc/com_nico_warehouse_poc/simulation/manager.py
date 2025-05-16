import omni.usd
import omni.kit.app # For app time if needed, though Animator handles it
from pxr import Gf, UsdGeom, Usd
from typing import Dict, Any, List, Optional, Callable

from .path_finder import PathFinder
from .animator import Animator
from .data_exporter import DataExporter
from ..utils import usdutils, omath
from ..core import settings as ext_settings # Using ext_settings to avoid conflict

# Default settings that could be overridden by ext_settings.py
DEFAULT_POC_SETTINGS = {
    "Layout_A": {
        "Scenario_1": {
            "start_prim_path": "/World/Layout_A/StartPoints/Start_1",
            "end_prim_path": "/World/Layout_A/EndPoints/End_1",
            "agent_prim_path": "/World/Agents/SimpleAgent_A",
            "agent_speed": 2.0,
            "output_filename_template": "results/layout_A_scenario_1_results.yaml"
        },
        "Scenario_2": {
            "start_prim_path": "/World/Layout_A/StartPoints/Start_2",
            "end_prim_path": "/World/Layout_A/EndPoints/End_2",
            "agent_prim_path": "/World/Agents/SimpleAgent_B",
            "agent_speed": 1.5,
            "output_filename_template": "results/layout_A_scenario_2_results.yaml"
        }
    },
    "Layout_B": {
        "Scenario_1": {
            "start_prim_path": "/World/Layout_B/StartPoints/Start_X",
            "end_prim_path": "/World/Layout_B/EndPoints/End_X",
            "agent_prim_path": "/World/Agents/SimpleAgent_A",
            "agent_speed": 2.5,
            "output_filename_template": "results/layout_B_scenario_1_results.yaml"
        }
    }
}


class SimulationManager:
    def __init__(self):
        print("SimulationManager: Initialized.")
        self._path_finder: Optional[PathFinder] = None
        self._animator: Optional[Animator] = None
        self._data_exporter: DataExporter = DataExporter()
        self._current_stage: Optional[Usd.Stage] = None

        # Load settings from core.settings, with fallback to defaults
        self._poc_settings = getattr(ext_settings, 'POC_SIMULATION_CONFIG', DEFAULT_POC_SETTINGS)


    def _get_prim_world_position(self, prim_path: str) -> Optional[Gf.Vec3d]:
        if not self._current_stage:
            self._current_stage = usdutils.get_stage()
            if not self._current_stage:
                print(f"SimulationManager Error: Stage not found to get prim position for {prim_path}")
                return None

        prim = self._current_stage.GetPrimAtPath(prim_path)
        if not prim or not prim.IsValid():
            print(f"SimulationManager Error: Prim not found or invalid at {prim_path}")
            return None
        try:
            xformable = UsdGeom.Xformable(prim)
            world_transform: Gf.Matrix4d = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
            translation: Gf.Vec3d = world_transform.ExtractTranslation()
            return translation
        except Exception as e:
            print(f"SimulationManager Error: Getting world position for {prim_path}: {e}")
            return None

    def run_poc_simulation(
        self,
        layout_id: str,
        scenario_id: str,
        on_success_callback: Optional[Callable[[str], None]] = None,
        on_failure_callback: Optional[Callable[[str], None]] = None
    ):
        print(f"SimulationManager: Attempting to run PoC for Layout '{layout_id}', Scenario '{scenario_id}'")

        try:
            self._path_finder = PathFinder.create()
        except RuntimeError as e:
            msg = "PathFinder is not initialized. Cannot run simulation."
            print(f"SimulationManager Error: {msg}")
            if on_failure_callback: on_failure_callback(msg)
            return

        self._current_stage = usdutils.get_stage()
        if not self._current_stage:
            msg = "USD Stage not found."
            print(f"SimulationManager Error: {msg}")
            if on_failure_callback: on_failure_callback(msg)
            return

        scenario_config = self._poc_settings.get(layout_id, {}).get(scenario_id)
        if not scenario_config:
            msg = f"Configuration not found for Layout '{layout_id}', Scenario '{scenario_id}'"
            print(f"SimulationManager Error: {msg}")
            if on_failure_callback: on_failure_callback(msg)
            return

        start_prim_path = scenario_config.get("start_prim_path")
        end_prim_path = scenario_config.get("end_prim_path")
        agent_prim_path = scenario_config.get("agent_prim_path")
        agent_speed = float(scenario_config.get("agent_speed", 1.0)) # Ensure float
        output_filename = scenario_config.get("output_filename_template", f"sim_results_{layout_id}_{scenario_id}.yaml")

        if not all([start_prim_path, end_prim_path, agent_prim_path]):
            msg = "Incomplete prim paths in scenario configuration."
            print(f"SimulationManager Error: {msg}")
            if on_failure_callback: on_failure_callback(msg)
            return

        start_pos = self._get_prim_world_position(start_prim_path)
        end_pos = self._get_prim_world_position(end_prim_path)

        if start_pos is None or end_pos is None:
            msg = "Could not determine start or end position from prims."
            print(f"SimulationManager Error: {msg}")
            if on_failure_callback: on_failure_callback(msg)
            return

        print(f"SimulationManager: Start: {start_pos}, End: {end_pos} for agent {agent_prim_path}")

        try:
            path_points: List[Gf.Vec3d] = self._path_finder.find(start_pos, end_pos)
            if not path_points or len(path_points) < 1 : # PathNavigator handles <1 point, find should return at least 1 if successful
                msg = "Path could not be found or is too short (0 points)."
                print(f"SimulationManager Error: {msg}")
                if on_failure_callback: on_failure_callback(msg)
                return
            if len(path_points) == 1 and start_pos.GetDistance(end_pos) > 1e-3: # Start and end are different but only one point found
                msg = "Path found only one point, but start and end are different. NavMesh issue?"
                print(f"SimulationManager Warning: {msg}")
                # Proceed with one point, PathNavigator handles it.

            print(f"SimulationManager: Path found with {len(path_points)} points.")
        except Exception as e:
            msg = f"Error during path finding: {e}"
            print(f"SimulationManager Error: {msg}")
            if on_failure_callback: on_failure_callback(msg)
            return

        agent_prim = self._current_stage.GetPrimAtPath(agent_prim_path)
        if not agent_prim or not agent_prim.IsValid():
            msg = f"Agent prim not found at {agent_prim_path}"
            print(f"SimulationManager Error: {msg}")
            if on_failure_callback: on_failure_callback(msg)
            return

        if self._animator:
            self._animator.stop_animation()
            self._animator.cleanup()

        try:
            self._animator = Animator(agent_prim, path_points, agent_speed)
            animation_complete_handler = lambda: self._on_animation_complete(
                layout_id, scenario_id, path_points, agent_speed, output_filename, on_success_callback, on_failure_callback
            )
            self._animator.start_animation(on_complete_callback=animation_complete_handler)
            print(f"SimulationManager: Animation started for agent: {agent_prim_path}")
        except ValueError as ve: # Catch errors from Animator init (e.g. bad path)
            msg = f"Failed to initialize Animator: {ve}"
            print(f"SimulationManager Error: {msg}")
            if on_failure_callback: on_failure_callback(msg)
            return


    def _on_animation_complete(
        self,
        layout_id: str,
        scenario_id: str,
        path_points: List[Gf.Vec3d],
        agent_speed: float, # Pass speed for consistent calculation
        output_filename: str,
        on_success_callback: Optional[Callable[[str], None]],
        on_failure_callback: Optional[Callable[[str], None]]
    ):
        print(f"SimulationManager: Animation completed for Layout '{layout_id}', Scenario '{scenario_id}'")

        if not path_points: # Should not happen if path finding was successful
            msg = "Path points are empty at animation complete. Cannot calculate results."
            print(f"SimulationManager Error: {msg}")
            if on_failure_callback: on_failure_callback(msg)
            return

        total_distance = 0.0
        if len(path_points) > 1:
            for i in range(len(path_points) - 1):
                total_distance += omath.length(path_points[i+1] - path_points[i])

        start_coord_dict = {"X": path_points[0][0], "Y": path_points[0][1], "Z": path_points[0][2]}
        end_coord_dict = {"X": path_points[-1][0], "Y": path_points[-1][1], "Z": path_points[-1][2]}

        estimated_time = total_distance / agent_speed if agent_speed > 1e-6 else 0.0
        path_coords_list = [{"X": p[0], "Y": p[1], "Z": p[2]} for p in path_points]

        simulation_results = {
            "layout_id": layout_id,
            "scenario_id": scenario_id,
            "start_point_coords": start_coord_dict,
            "end_point_coords": end_coord_dict,
            "total_distance_meters": round(total_distance, 3), # Assuming units are meters
            "estimated_time_seconds": round(estimated_time, 3),
            "path_coordinates": path_coords_list
        }

        print(f"SimulationManager Results: {simulation_results}")
        try:
            self._data_exporter.export_to_json(simulation_results, output_filename)
            msg = f"Results exported to {output_filename}"
            if on_success_callback: on_success_callback(msg)
        except Exception as e:
            msg = f"Failed to export results: {e}"
            print(f"SimulationManager Error: {msg}")
            if on_failure_callback: on_failure_callback(msg)

        if self._animator: # Cleanup animator for this run
            self._animator.cleanup()
            self._animator = None

    def cleanup(self):
        print("SimulationManager: Cleanup.")
        if self._animator:
            self._animator.stop_animation()
            self._animator.cleanup()
            self._animator = None