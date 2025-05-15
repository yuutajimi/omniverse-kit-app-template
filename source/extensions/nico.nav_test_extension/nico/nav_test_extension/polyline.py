import omni.usd
from pxr import Usd, UsdGeom, Gf, Vt, Sdf
import carb

class Polyline:
    def __init__(
            self,
            stage: Usd.Stage,
            prim_path: str,
            points: list[Gf.Vec3d] = [],
            width: float = 1.0,
            color: Gf.Vec3f = Gf.Vec3f(1.0, 1.0, 1.0)
    ):
        """
        UsdGeom.BasisCurvesを使って折れ線を作成・管理するクラス。

        :param stage: USDステージのインスタンス
        :param prim_path: 作成する折れ線のPrimのパス (例: "/World/MyPolyline")
        :param points: 初期状態の頂点リスト (Gf.Vec3fのリスト)
        :param width: 線の太さ (幅)
        :param color: 線の色 (Gf.Vec3f RGB)
        """
        self._stage = stage
        self._prim_path = Sdf.Path(prim_path) # Sdf.Pathオブジェクトに変換
        self._curves_prim = UsdGeom.BasisCurves.Define(self._stage, self._prim_path)

        if not self._curves_prim:
            carb.log_error(f"Failed to define BasisCurves at {self._prim_path}")
            return

        # 基本的な属性を設定
        self._curves_prim.CreateTypeAttr().Set(UsdGeom.Tokens.linear) # 直線的なカーブ
        self.set_width(width)
        self.set_color(color)

        if points:
            self.update_points(points)

    def update_points(self, points: list[Gf.Vec3d]):
        """
        折れ線の頂点リストを更新する。

        :param points: 新しい頂点リスト (Gf.Vec3fのリスト)
        """
        if not self._curves_prim:
            return

        if not points or len(points) < 2:
            # 点が2つ未満の場合は線を定義できないので、既存の点をクリアする (または何もしない)
            self._curves_prim.GetPointsAttr().Clear()
            self._curves_prim.GetCurveVertexCountsAttr().Clear()
            # carb.log_warn(f"Polyline at {self._prim_path} requires at least 2 points.")
            return

        points_attr = self._curves_prim.CreatePointsAttr()
        curve_vertex_counts_attr = self._curves_prim.CreateCurveVertexCountsAttr()

        points = [
            Gf.Vec3f(x[0], x[1], x[2])
            for x in points
        ]

        # Vt.Vec3fArray に変換して設定
        points_attr.Set(Vt.Vec3fArray(points))
        # 1本の折れ線なので、頂点数はリストの要素数
        curve_vertex_counts_attr.Set(Vt.IntArray([len(points)]))

    def set_width(self, width: float):
        """
        折れ線の太さ（幅）を設定する。

        :param width: 新しい太さ
        """
        if not self._curves_prim:
            return

        widths_attr = self._curves_prim.CreateWidthsAttr()
        widths_attr.Set(Vt.FloatArray([width]))
        # 幅の補間方法を一定 (constant) に設定 (始点から終点まで同じ太さ)
        self._curves_prim.SetWidthsInterpolation(UsdGeom.Tokens.constant)

    def set_color(self, color: Gf.Vec3f):
        """
        折れ線の色を設定する。

        :param color: 新しい色 (Gf.Vec3f RGB)
        """
        if not self._curves_prim:
            return

        # displayColor Primvar を作成または取得して設定
        # BasisCurves の色は displayColor Primvar で制御するのが一般的
        display_color_primvar = self._curves_prim.CreateDisplayColorPrimvar(UsdGeom.Tokens.constant) # 補間なし(全体一色)
        display_color_primvar.Set(Vt.Vec3fArray([color]))


    def get_prim(self) -> Usd.Prim:
        """
        BasisCurvesのPrimオブジェクトを返す。
        """
        return self._curves_prim.GetPrim()