import omni.ui as ui

class ControlPanelWindow(ui.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frame.set_build_fn(self._build)

    def _build(self):
        with self.frame:
            with ui.VStack():
                def on_click():
                    print("Clicked")

                ui.Button("Button", clicked_fn=on_click)