import yaml
import json
import csv
import os
from typing import Dict, Any, List

from ..utils import file_io # (推奨) YAML/JSON/CSVの具体的な書き出し処理を委譲

class DataExporter:
    def __init__(self):
        print("DataExporter initialized.")
        # 出力ディレクトリがなければ作成 (プロジェクトルートからの相対パスなどを想定)
        self._output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs")) # 例: Extensionルート/outputs
        if not os.path.exists(self._output_dir):
            try:
                os.makedirs(self._output_dir)
            except OSError as e:
                print(f"Error creating output directory {self._output_dir}: {e}")
                self._output_dir = os.path.abspath(".") # Fallback to current dir


    def _ensure_output_path(self, filename: str) -> str:
        """ファイル名から完全な出力パスを生成し、ディレクトリが存在することを確認する"""
        # ファイル名にディレクトリが含まれている場合、それを優先する
        if os.path.dirname(filename):
             abs_path = os.path.abspath(filename)
             dir_path = os.path.dirname(abs_path)
        else: # ファイル名のみの場合、デフォルトの出力ディレクトリを使用
             dir_path = self._output_dir
             abs_path = os.path.join(dir_path, filename)

        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError as e:
                print(f"Error creating directory {dir_path} for output file {filename}: {e}")
                # エラー時はプロジェクトルート直下などにフォールバックも検討
                return os.path.abspath(filename) # とりあえずそのまま返す
        return abs_path


    def export_to_yaml(self, data: Dict[str, Any], filename: str = "simulation_results.yaml"):
        """シミュレーション結果をYAMLファイルに出力する"""
        filepath = self._ensure_output_path(filename)
        print(f"Exporting results to YAML: {filepath}")
        try:
            # file_io.write_yaml(filepath, data) # file_io.py を使う場合
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False, indent=2)
            print(f"Successfully exported to {filepath}")
        except Exception as e:
            print(f"Error exporting data to YAML file {filepath}: {e}")

    def export_to_json(self, data: Dict[str, Any], filename: str = "simulation_results.json"):
        """シミュレーション結果をJSONファイルに出力する"""
        filepath = self._ensure_output_path(filename)
        print(f"Exporting results to JSON: {filepath}")
        try:
            # file_io.write_json(filepath, data) # file_io.py を使う場合
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Successfully exported to {filepath}")
        except Exception as e:
            print(f"Error exporting data to JSON file {filepath}: {e}")

    def export_to_csv(self, data_list: List[Dict[str, Any]], filename: str = "simulation_results.csv"):
        """
        シミュレーション結果のリストをCSVファイルに出力する。
        PoCの仕様では結果は1シナリオ1ファイルだが、将来的な拡張を考慮。
        """
        if not data_list:
            print("No data to export to CSV.")
            return

        filepath = self._ensure_output_path(filename)
        print(f"Exporting results to CSV: {filepath}")
        try:
            # file_io.write_csv(filepath, data_list) # file_io.py を使う場合
            # ヘッダーは最初の辞書のキーから取得
            headers = list(data_list[0].keys())
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data_list)
            print(f"Successfully exported to {filepath}")
        except Exception as e:
            print(f"Error exporting data to CSV file {filepath}: {e}")