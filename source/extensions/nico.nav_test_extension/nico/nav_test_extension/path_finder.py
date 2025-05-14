import omni.anim.navigation.core as nav
from pxr import Gf
from . import omath

class PathFinder:
    def __init__(self, navmesh: nav.INavMesh) -> None:
        self.navmesh = navmesh

    def find(self, start: Gf.Vec3d, end: Gf.Vec3d) -> list[Gf.Vec3d]:
        start_pos = omath.to_carb(start)
        end_pos = omath.to_carb(end)

        path_query_result = self.navmesh.query_shortest_path(
            start_pos=start_pos,
            end_pos=end_pos
        )

        path_points = path_query_result.get_points()

        return [
            omath.to_gf(v)
            for v in path_points
        ]

    @staticmethod
    def create():
        inav = nav.acquire_interface()
        navmesh = inav.get_navmesh()

        if not navmesh:
            raise RuntimeError("NavMesh not found or not baked")

        return PathFinder(navmesh)