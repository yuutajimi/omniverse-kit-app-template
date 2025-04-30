import omni.anim.navigation.core as nav
import carb


def run():
    inav = nav.acquire_interface()
    navmesh = inav.get_navmesh()

    if not navmesh:
        print("NavMesh not found or not baked")
        return

    start_pos = carb.Float3(0, 0, 0)
    end_pos = carb.Float3(100, 50, 0)

    path_query_result = navmesh.query_shortest_path(
        start_pos=start_pos,
        end_pos=end_pos
    )

    if not path_query_result:
        print("Path not found")
        return

    path_points = path_query_result.get_points()
    if not path_points:
        print("failed to get points on path")
        return

    print(f"path found: {path_points}")