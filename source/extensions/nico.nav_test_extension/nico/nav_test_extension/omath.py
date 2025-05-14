import carb
from pxr import Gf
from typing import TypeVar, overload, cast

TVector = TypeVar('TVector', float, float|Gf.Vec3d)

def to_gf(v: carb.Float3):
    return Gf.Vec3d(v.x, v.y, v.z)

# @overload
# def lerp(start: float, end: float, t: float) -> float:
#     ...

# @overload
# def lerp(start: Gf.Vec3d, end: Gf.Vec3d, t: float) -> Gf.Vec3d:
#     ...


def lerp(start: TVector, end: TVector, t: float) -> TVector:
    offset = end - start
    offset = offset * t
    return cast(TVector, start + offset)

def length(v: TVector) -> float:
    return Gf.Vec3d.GetLength(v)