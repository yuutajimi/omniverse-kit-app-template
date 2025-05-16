import omni.ext
import omni.ui as ui
import omni.kit.app
from .ui.main_window import MainWindow
from .simulation.manager import SimulationManager
from .core import settings # PoCの設定を読み込むため (仮)

EXTENSION_NAME = "Warehouse PoC" # Extensionウィンドウのタイトルなどに使用

class WarehousePocExtension(omni.ext.IExt):
    def on_startup(self, ext_id: str):
        print(f"[{EXTENSION_NAME}] on_startup")
        self._ext_id = ext_id
        self._window = None
        self._simulation_manager = None

        # メインウィンドウの作成と表示
        # 引数としてSimulationManagerのインスタンスを渡すことを検討
        self._window = MainWindow(EXTENSION_NAME, width=300, height=400)
        self._window.set_visibility_changed_fn(self._on_window_visibility_changed)

        # SimulationManagerの初期化
        # settings.pyから設定を読み込む例
        # sim_settings = settings.get_simulation_settings() # 仮の関数
        self._simulation_manager = SimulationManager() # 必要に応じて設定を渡す

        # MainWindowにSimulationManagerの参照を渡す
        if self._window:
            self._window.set_simulation_manager(self._simulation_manager)

    def _on_window_visibility_changed(self, visible: bool):
        if self._window:
            if visible:
                print(f"[{EXTENSION_NAME}] Window is now visible.")
            else:
                print(f"[{EXTENSION_NAME}] Window is now hidden.")
        # 必要であれば、ウィンドウ非表示時にリソースを解放する処理などを記述

    def on_shutdown(self):
        print(f"[{EXTENSION_NAME}] on_shutdown")
        if self._simulation_manager:
            self._simulation_manager.cleanup() # シミュレーション関連のリソース解放
            self._simulation_manager = None
        if self._window:
            self._window.destroy() # ウィンドウを破棄
            self._window = None