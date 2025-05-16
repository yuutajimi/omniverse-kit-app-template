import omni.anim.navigation.core as nav
import carb
import omni.usd
import omni.kit.app
from pxr import UsdGeom, Gf, Sdf, Usd, Tf


class Transform:
    def __init__(self, prim):
        self._xform = UsdGeom.Xformable(prim)
        self._translate_op = self._ensure_xform_ops(self._xform, UsdGeom.XformOp.TypeTranslate)

    @property
    def position(self) -> Gf.Vec3d:
        return self._translate_op.Get()

    @position.setter
    def position(self, value: Gf.Vec3d):
        self._translate_op.Set(value)

    @property
    def position_carb(self) -> carb.Float3:
        pos = self.position
        return carb.Float3(pos[0], pos[1], pos[2])

    @position_carb.setter
    def position_carb(self, value: carb.Float3):
        self.position = Gf.Vec3d(value.x, value.y, value.z)

    def _ensure_xform_ops(self, xform: UsdGeom.Xformable, type: UsdGeom.XformOp):
        for op in xform.GetOrderedXformOps():
            if op.GetOpType() == type:
                return op
        return xform.AddTranslateOp()
