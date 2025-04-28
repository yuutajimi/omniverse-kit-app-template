import omni.ui as ui
from omni.ui import scene as sc

class Move(sc.DragGesture):
    def __init__(self, transform: sc.Transform, **kwargs):
        super().__init__(**kwargs)
        self._transform = transform

    def on_changed(self):
        translate = self.sender.gesture_payload.moved
        current = sc.Matrix44.get_translation_matrix(*translate)
        self._transform.transform *= current


class GestureManager(sc.GestureManager):
    def should_prevent(self, gesture: sc.AbstractGesture, preventer: sc.AbstractGesture):
        if gesture.name == "SelectionDrag" and preventer.state == sc.GestureState.BEGAN:
            return True


gesture_manager = GestureManager()


class LineManipulator(sc.Manipulator):
    def __init__(self, desc: dict, **kwargs):
        super().__init__(**kwargs)

    def on_build(self):
        transform = sc.Transform()
        with transform:
            sc.Line(
                [-50, -50, 0],
                [50, 50, 0],
                color = ui.color.beige,
                thickness=10,
                gesture=Move(transform, manager=gesture_manager)
            )
