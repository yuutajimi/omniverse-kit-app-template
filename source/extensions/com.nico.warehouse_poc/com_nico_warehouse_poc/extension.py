import omni.ext
import omni.ui as ui
import omni.kit.app
from .ui.main_window import MainWindow
from .simulation.manager import SimulationManager
from .core import settings as ext_settings # Renamed to avoid conflict with omni.kit.settings

EXTENSION_NAME = "Warehouse PoC"

class WarehousePocExtension(omni.ext.IExt):
    def on_startup(self, ext_id: str):
        print(f"[{EXTENSION_NAME}] ({ext_id}) on_startup")
        self._ext_id = ext_id
        self._window: MainWindow|None = None
        self._simulation_manager: SimulationManager|None = None

        # SimulationManagerの初期化
        # 将来的には ext_settings から設定を読み込んで渡す
        self._simulation_manager = SimulationManager()

        # メインウィンドウの作成と表示
        self._window = MainWindow(EXTENSION_NAME, width=350, height=250)
        self._window.set_visibility_changed_fn(self._on_window_visibility_changed)

        # MainWindowにSimulationManagerの参照を渡す
        if self._window:
            self._window.set_simulation_manager(self._simulation_manager)

    def _on_window_visibility_changed(self, visible: bool):
        if self._window:
            if visible:
                print(f"[{EXTENSION_NAME}] Window is now visible.")
            else:
                print(f"[{EXTENSION_NAME}] Window is now hidden.")

    def on_shutdown(self):
        print(f"[{EXTENSION_NAME}] ({self._ext_id}) on_shutdown")
        if self._simulation_manager:
            self._simulation_manager.cleanup()
            self._simulation_manager = None
        if self._window:
            self._window.destroy()
            self._window = None