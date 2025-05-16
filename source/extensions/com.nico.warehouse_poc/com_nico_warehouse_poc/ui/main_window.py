import omni.ui as ui
from typing import Optional
# from ..simulation.manager import SimulationManager # 型ヒント用だが、循環参照を避けるため文字列でも可

class MainWindow(ui.Window):
    def __init__(self, title: str, **kwargs):
        super().__init__(title, **kwargs)
        self._simulation_manager: Optional["SimulationManager"] = None # 遅延参照のため文字列

        # UI要素の構築
        with self.frame:
            with ui.VStack(spacing=5, height=0):
                ui.Label("Warehouse PoC Controls", alignment=ui.Alignment.CENTER)

                # --- レイアウト選択 (PoCではスクリプト直書き or 設定ファイルなので簡易的に) ---
                with ui.HStack():
                    ui.Label("Layout ID:", width=ui.Percent(30))
                    self._layout_id_strfield = ui.StringField()
                    self._layout_id_strfield.model.set_value("Layout_A") # 初期値

                # --- 動線シナリオ選択 (PoCではスクリプト直書き or 設定ファイルなので簡易的に) ---
                with ui.HStack():
                    ui.Label("Scenario ID:", width=ui.Percent(30))
                    self._scenario_id_strfield = ui.StringField()
                    self._scenario_id_strfield.model.set_value("Scenario_1") # 初期値

                # --- 開始地点 (PoC仕様ではスクリプトor設定ファイルだが、UIで指定するなら) ---
                # ui.Label("Start Position (X,Y,Z):")
                # with ui.HStack():
                #     self._start_x = ui.FloatField(width=ui.Percent(30))
                #     self._start_y = ui.FloatField(width=ui.Percent(30))
                #     self._start_z = ui.FloatField(width=ui.Percent(30))

                # --- 目標地点 (同上) ---
                # ui.Label("End Position (X,Y,Z):")
                # with ui.HStack():
                #     self._end_x = ui.FloatField(width=ui.Percent(30))
                #     self._end_y = ui.FloatField(width=ui.Percent(30))
                #     self._end_z = ui.FloatField(width=ui.Percent(30))

                # --- シミュレーション開始ボタン ---
                self._sim_button = ui.Button("Start Simulation", clicked_fn=self._on_start_simulation_clicked)

                # --- 結果表示エリア (任意) ---
                # self._result_label = ui.Label("Result: -")

    def set_simulation_manager(self, manager: "SimulationManager"):
        self._simulation_manager = manager

    def _on_start_simulation_clicked(self):
        if not self._simulation_manager:
            print("Error: SimulationManager not set.")
            # if self._result_label: self._result_label.text = "Error: SimulationManager not set."
            return

        # UIからパラメータを取得 (PoCでは設定ファイルやスクリプト直書きが主なので、ここでは固定値やUIから取得する例)
        layout_id = self._layout_id_strfield.model.get_value_as_string()
        scenario_id = self._scenario_id_strfield.model.get_value_as_string()

        print(f"Starting simulation for Layout: {layout_id}, Scenario: {scenario_id}")
        # if self._result_label: self._result_label.text = f"Running: {layout_id}, {scenario_id}"

        # SimulationManagerのメソッドを呼び出す
        # ここでは非同期実行を考慮していないが、重い処理の場合は omni.kit.async_engine などを使用
        try:
            # PoCの仕様では、開始/終了地点はスクリプト/設定ファイルから読み込む想定
            # もしUIで指定する場合は、FloatFieldから値を取得する
            # start_pos = Gf.Vec3d(self._start_x.model.get_value_as_float(), ...)
            # end_pos = Gf.Vec3d(self._end_x.model.get_value_as_float(), ...)

            # manager.run_simulation(layout_id, scenario_id, start_pos, end_pos) # UIで指定する場合
            self._simulation_manager.run_poc_simulation(layout_id, scenario_id) # 設定ファイルベースの場合

            # if self._result_label: self._result_label.text = "Simulation Complete. Check console/output file."
            print("Simulation request sent to manager.")

        except Exception as e:
            print(f"Error during simulation: {e}")
            # if self._result_label: self._result_label.text = f"Error: {e}"

    def destroy(self):
        # SimulationManagerの参照をクリア
        self._simulation_manager = None
        super().destroy()