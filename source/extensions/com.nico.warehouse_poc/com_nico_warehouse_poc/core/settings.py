# core/settings.py

# This file can be used to store more complex or externally configurable settings.
# For the PoC, SimulationManager uses its own DEFAULT_POC_SETTINGS, but
# this provides a place for future expansion.

# Example: How SimulationManager could load settings from here
POC_SIMULATION_CONFIG = {
    "Layout_A": {
        "Scenario_1": {
            "start_prim_path": "/World/Warehouse/Layout_A/Points/Start_A1", # More specific paths
            "end_prim_path": "/World/Warehouse/Layout_A/Points/End_A1",
            "agent_prim_path": "/World/Characters/Robot_Worker_1",
            "agent_speed": 1.8,  # m/s
            "output_filename_template": "results/layout_A/scenario_1_data.yaml" # Subdir for results
        },
        "Scenario_Debug": { # A scenario for quick debugging
            "start_prim_path": "/World/Debug/Start",
            "end_prim_path": "/World/Debug/End",
            "agent_prim_path": "/World/Debug/TestAgent",
            "agent_speed": 3.0,
            "output_filename_template": "debug_results/latest_run.json"
        }
    },
    "AnotherLayout": {
        # ... other layout configurations
    }
}

# Other global settings for the extension could go here
# مثلاً DEFAULT_AGENT_MODEL_USD_PATH = "/Projects/MyAssets/Agents/DefaultAgent.usd"
# DEFAULT_OUTPUT_DIRECTORY = "warehouse_sim_outputs" # Overrides DataExporter's default