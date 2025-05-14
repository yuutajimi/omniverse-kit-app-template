from pxr import UsdGeom, Gf, Sdf, Usd
from .transform import Transform

class PathVisualizer:
    def __init__(self, stage: Usd.Stage, visualize_path: str, path_points: list[Gf.Vec3d]):
        self._stage = stage
        root_path = Sdf.Path(visualize_path)
        self._root = UsdGeom.Xform.Define(stage, root_path)

        for i, point in enumerate(path_points):
            self._create_point(point, i)

    def destroy(self):
        self._stage.RemovePrim(self._root.GetPath())

    def _create_point(self, position: Gf.Vec3d, number: int):
        root_path = self._root.GetPath()
        path = root_path.AppendChild(f"Point_{number}")
        sphere: UsdGeom.Sphere = UsdGeom.Sphere.Define(self._stage, path)
        sphere.GetRadiusAttr().Set(10)
        Transform(sphere).position = position
