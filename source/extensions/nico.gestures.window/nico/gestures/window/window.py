import omni.ui as ui
from omni.ui import scene as sc

proj = [
    0.5,    0,      0,      0,
    0,      0.5,    0,      0,
    0,      0,      2e-7,   0,
    0,      0,      1,      1
]

class Move(sc.DragGesture):
    def __init__(self, transform: sc.Transform, **kwargs):
        super().__init__(**kwargs)
        self.__transform = transform

    def on_changed(self):
        translate = self.sender.gesture_payload.moved
        current = sc.Matrix44.get_translation_matrix(*translate)
        self.__transform.transform *= current

    # def on_began(self):
        # self.sender.color = ui.color.indigo

    # def on_ended(self):
        # self.sender.color = ui.color.beige


def setcolor(sender, color):
    sender.color = color


class Manager(sc.GestureManager):
    def should_prevent(self, gesture: sc.AbstractGesture, preventer: sc.AbstractGesture) -> bool:
        if gesture.name != "gesture_name" and preventer.state == sc.GestureState.BEGAN:
            return True

manager = Manager()


class GestureWindowExample(ui.Window):
    def __init__(self, title: str, **kwargs) -> None:
        super().__init__(title, **kwargs)
        self.frame.set_build_fn(self._build_fn)


    def _build_fn(self):
        with self.frame:
            with ui.VStack():
                scene_view = sc.SceneView(
                    sc.CameraModel(proj, 1),
                    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT)

                with scene_view.scene:
                    transform = sc.Transform()

                    with transform:
                        sc.Rectangle(
                            2, # width
                            2, # height
                            color=ui.color.beige,
                            thickness=5,
                            gestures=[
                                Move(transform, manager=manager, name="gesture_name"),
                                sc.ClickGesture(lambda s: setcolor(s, ui.color.red), manager=manager, name="gesture_name"),
                                sc.DoubleClickGesture(lambda s: setcolor(s, ui.color.beige), manager=manager, name="gesture_name")
                            ]
                        )

                    transform = sc.Transform(transform=sc.Matrix44.get_translation_matrix(0,0,-1))
                    with transform:
                        sc.Rectangle(
                            2, # width
                            2, # height
                            color=ui.color.olive,
                            thickness=5,
                            gesture=Move(transform)
                        )