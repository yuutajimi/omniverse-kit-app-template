import omni.ui as ui
from typing import Optional
from ..simulation.manager import SimulationManager # For type hinting if not using string

class MainWindow(ui.Window):
    def __init__(self, title: str, **kwargs):
        super().__init__(title, **kwargs)
        self._simulation_manager: Optional["SimulationManager"] = None # Use string for forward reference

        # UI要素の構築
        with self.frame:
            with ui.VStack(spacing=8, style={"margin": 10}):
                ui.Label("Warehouse Simulation Controls", alignment=ui.Alignment.CENTER, style={"font_size": 16})

                with ui.CollapsableFrame("Layout & Scenario"):
                    with ui.VStack(spacing=5, style={"margin": 5}):
                        with ui.HStack():
                            ui.Label("Layout ID:", width=ui.Percent(35))
                            self._layout_id_strfield = ui.StringField()
                            self._layout_id_strfield.model.set_value("Layout_A")

                        with ui.HStack():
                            ui.Label("Scenario ID:", width=ui.Percent(35))
                            self._scenario_id_strfield = ui.StringField()
                            self._scenario_id_strfield.model.set_value("Scenario_1")
                ui.Spacer(height=5)

                self._sim_button = ui.Button(
                    "Start Simulation",
                    clicked_fn=self._on_start_simulation_clicked,
                    style={"background_color": ui.color(0.2, 0.5, 0.2)} # A bit of styling
                )
                ui.Spacer(height=5)
                self._status_label = ui.Label("Status: Ready", style={"color": ui.color(0.8, 0.8, 0.8)})


    def set_simulation_manager(self, manager: "SimulationManager"):
        self._simulation_manager = manager

    def _on_start_simulation_clicked(self):
        if not self._simulation_manager:
            print("Error: MainWindow - SimulationManager not set.")
            self._status_label.text = "Error: SimulationManager not set."
            self._status_label.style = {"color": ui.color(0.8, 0.2, 0.2)}
            return

        layout_id = self._layout_id_strfield.model.get_value_as_string()
        scenario_id = self._scenario_id_strfield.model.get_value_as_string()

        if not layout_id or not scenario_id:
            self._status_label.text = "Error: Layout ID and Scenario ID are required."
            self._status_label.style = {"color": ui.color(0.8, 0.2, 0.2)}
            return

        print(f"MainWindow: Starting simulation for Layout: {layout_id}, Scenario: {scenario_id}")
        self._status_label.text = f"Running: {layout_id} - {scenario_id}..."
        self._status_label.style = {"color": ui.color(0.8, 0.8, 0.2)} # Yellowish for running

        try:
            # SimulationManagerのメソッドを呼び出す
            self._simulation_manager.run_poc_simulation(
                layout_id,
                scenario_id,
                on_success_callback=self._on_simulation_success,
                on_failure_callback=self._on_simulation_failure
            )
            # Note: run_poc_simulation is likely asynchronous due to animation.
            # Callbacks will handle the status update.
        except Exception as e:
            print(f"MainWindow: Error calling run_poc_simulation: {e}")
            self._on_simulation_failure(f"Error: {e}")

    def _on_simulation_success(self, message: str):
        self._status_label.text = f"Success: {message}"
        self._status_label.style = {"color": ui.color(0.2, 0.8, 0.2)} # Green for success
        print(f"MainWindow: Simulation successful - {message}")

    def _on_simulation_failure(self, error_message: str):
        self._status_label.text = f"Failure: {error_message}"
        self._status_label.style = {"color": ui.color(0.8, 0.2, 0.2)} # Red for failure
        print(f"MainWindow: Simulation failed - {error_message}")


    def destroy(self):
        self._simulation_manager = None # Clear reference
        super().destroy()