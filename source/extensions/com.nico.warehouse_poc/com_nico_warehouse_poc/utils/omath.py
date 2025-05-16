import carb
from pxr import Gf
from typing import TypeVar, overload, cast

TVector = TypeVar('TVector', float, float|Gf.Vec3d)

def to_gf(v: carb.Float3):
    return Gf.Vec3d(v.x, v.y, v.z)

def to_carb(v: Gf.Vec3d):
    return carb.Float3(v[0], v[1], v[2])

# --- Vec3d specific ---
@overload
def lerp(start: Gf.Vec3d, end: Gf.Vec3d, t: float) -> Gf.Vec3d: ...

# --- float specific ---
@overload
def lerp(start: float, end: float, t: float) -> float: ...

def lerp(start, end, t): # Implementation
    if isinstance(start, Gf.Vec3d) and isinstance(end, Gf.Vec3d):
        return start + (end - start) * t
    elif isinstance(start, (float, int)) and isinstance(end, (float, int)):
        return start + (end - start) * t
    raise TypeError("Unsupported types for lerp")

def length(v: TVector) -> float:
    return Gf.Vec3d.GetLength()