import carb
import carb.events
import omni.usd
import omni.kit.app
from typing import Any
from pxr import UsdGeom, Sdf, Usd
from .transform import Transform
from . import omath


def get_stage() -> Usd.Stage|None:
    context: Any = omni.usd.get_context()
    return context.get_stage()