# core/settings.py

# PoCのシミュレーション設定
# SimulationManager内のPOC_SETTINGSをこちらに移動・拡張することを想定
# 例:
# DEFAULT_AGENT_SPEED = 1.5  # m/s
# DEFAULT_OUTPUT_DIR = "outputs/poc_results"

# LAYOUT_CONFIGS = {
#     "Layout_A": {
#         "description": "Standard layout A",
#         "navmesh_path": "/World/Layout_A/NavMesh", # (もしレイアウト毎にNavMeshが違うなら)
#         "scenarios": {
#             "Scenario_1": {
#                 "start_prim_path": "/World/Layout_A/StartPoints/Start_1",
#                 "end_prim_path": "/World/Layout_A/EndPoints/End_1",
#                 "agent_prim_path": "/World/Agents/SimpleAgent_A",
#                 "agent_speed": 2.0,
#                 "output_filename_template": "layout_A_scenario_1_results.yaml"
#             },
#             # ...
#         }
#     },
#     # ...
# }

def get_layout_config(layout_id: str):
    # return LAYOUT_CONFIGS.get(layout_id)
    pass # ここで上記のような設定辞書から情報を取得するロジックを実装

def get_scenario_config(layout_id: str, scenario_id: str):
    # layout_conf = get_layout_config(layout_id)
    # if layout_conf:
    #     return layout_conf.get("scenarios", {}).get(scenario_id)
    pass # ここでシナリオ設定を取得するロジックを実装

# 他にもExtension全体で共有したい設定や定数があればここに追加