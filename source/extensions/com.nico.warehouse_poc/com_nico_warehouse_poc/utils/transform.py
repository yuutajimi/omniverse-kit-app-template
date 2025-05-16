import carb
import omni.usd
import omni.kit.app
from pxr import UsdGeom, Gf, Sdf, Usd, Tf
from typing import Optional

class Transform:
    def __init__(self, prim: Usd.Prim): # Added type hint for prim
        if not prim or not prim.IsValid():
            raise ValueError(f"Transform: Provided prim '{prim.GetPath() if prim else 'None'}' is not valid.")
        self._prim = prim # Keep a reference to the prim
        self._xform = UsdGeom.Xformable(prim)
        self._translate_op = self._ensure_xform_op(self._xform, UsdGeom.XformOp.TypeTranslate, UsdGeom.XformOp.PrecisionDouble)
        # Could add scale and rotate ops similarly if needed

    @property
    def prim(self) -> Usd.Prim:
        return self._prim

    @property
    def position(self) -> Gf.Vec3d:
        if self._translate_op:
            return self._translate_op.Get()
        # Fallback if op somehow became invalid (should not happen with _ensure_xform_op)
        print(f"Warning: Translate op not valid for {self.prim.GetPath()}, returning (0,0,0)")
        return Gf.Vec3d(0,0,0)


    @position.setter
    def position(self, value: Gf.Vec3d):
        if self._translate_op:
            self._translate_op.Set(value)
        else:
            print(f"Warning: Cannot set position, translate op not valid for {self.prim.GetPath()}")


    @property
    def position_carb(self) -> carb.Float3:
        pos = self.position
        return carb.Float3(pos[0], pos[1], pos[2])

    @position_carb.setter
    def position_carb(self, value: carb.Float3):
        self.position = Gf.Vec3d(value.x, value.y, value.z)

    def _ensure_xform_op(
            self,
            xform: UsdGeom.Xformable,
            op_type: UsdGeom.XformOp.Type,
            precision: UsdGeom.XformOp.Precision = UsdGeom.XformOp.PrecisionDouble,
            op_suffix: str = "") -> Optional[UsdGeom.XformOp]:
        """
        Ensures that an XformOp of the given type exists.
        If not, it adds one. Returns the XformOp.
        """
        # Check existing ops
        for op in xform.GetOrderedXformOps():
            if op.GetOpType() == op_type and op.GetOpName().endswith(op_suffix): # Check suffix if provided
                return op

        # If not found, add a new one based on type
        added_op = None
        if op_type == UsdGeom.XformOp.TypeTranslate:
            added_op = xform.AddTranslateOp(precision, op_suffix)
        elif op_type == UsdGeom.XformOp.TypeScale:
            added_op = xform.AddScaleOp(precision, op_suffix)
        elif op_type == UsdGeom.XformOp.TypeRotateX: # Or use AddOrientOp for Quaternions
            added_op = xform.AddRotateXOp(precision, op_suffix)
        elif op_type == UsdGeom.XformOp.TypeRotateY:
            added_op = xform.AddRotateYOp(precision, op_suffix)
        elif op_type == UsdGeom.XformOp.TypeRotateZ:
            added_op = xform.AddRotateZOp(precision, op_suffix)
        elif op_type == UsdGeom.XformOp.TypeOrient: # For Quaternions
            added_op = xform.AddOrientOp(precision, op_suffix)
        # Add other types as needed (e.g., Matrix)

        if not added_op :
            carb.log_error(f"Failed to add XformOp of type {op_type} for prim {xform.GetPrim().GetPath()}")
        return added_op