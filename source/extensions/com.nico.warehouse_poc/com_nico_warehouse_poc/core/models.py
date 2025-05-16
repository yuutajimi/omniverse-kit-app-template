# core/models.py
# (今回は中身は省略。必要に応じてデータクラスなどを定義)
# from dataclasses import dataclass, field
# from typing import List, Dict
# from pxr import Gf

# @dataclass
# class Point3D:
#     X: float
#     Y: float
#     Z: float

# @dataclass
# class SimulationResultData:
#     layout_id: str
#     scenario_id: str
#     start_point_coords: Point3D
#     end_point_coords: Point3D
#     total_distance_meters: float
#     estimated_time_seconds: float
#     path_coordinates: List[Point3D] = field(default_factory=list)