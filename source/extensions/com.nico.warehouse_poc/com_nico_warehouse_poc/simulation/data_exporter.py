# import yaml # Requires PyYAML (ensure it's available or add to toml)
import json
import csv
import os
from typing import Dict, Any, List, Optional

# from ..utils import file_io # Option to use centralized file_io

class DataExporter:
    def __init__(self, default_output_subdir: str = "simulation_outputs"):
        print("DataExporter: Initialized.")
        # Try to create output dir relative to the extension's root or a user-defined path
        try:
            # This path is relative to this file, so ../.. goes to com_nico_warehouse_poc root
            extension_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self._base_output_dir = os.path.join(extension_root, default_output_subdir)
        except Exception:
            # Fallback if path resolution is tricky (e.g. during some testing scenarios)
            self._base_output_dir = os.path.abspath(default_output_subdir)

        if not os.path.exists(self._base_output_dir):
            try:
                os.makedirs(self._base_output_dir, exist_ok=True)
            except OSError as e:
                print(f"DataExporter Error: Creating base output directory {self._base_output_dir} failed: {e}")
                self._base_output_dir = os.path.abspath(".") # Fallback to current dir if creation fails


    def _prepare_filepath(self, filename: str) -> str:
        """Ensures the full path is ready and directories are created."""
        if os.path.isabs(filename):
            # If filename is already an absolute path, use it directly.
            # Ensure its directory exists.
            abs_path = filename
            dir_path = os.path.dirname(abs_path)
        else:
            # If filename is relative, join it with the base output directory.
            abs_path = os.path.join(self._base_output_dir, filename)
            dir_path = os.path.dirname(abs_path) # This will be self._base_output_dir if filename has no subdir

        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
            except OSError as e:
                print(f"DataExporter Warning: Could not create directory {dir_path} for {filename}: {e}. Attempting to save in base.")
                # Fallback to saving in base_output_dir if subdir creation fails
                abs_path = os.path.join(self._base_output_dir, os.path.basename(filename))
        return abs_path

    # def export_to_yaml(self, data: Dict[str, Any], filename: str = "simulation_results.yaml"):
    #     filepath = self._prepare_filepath(filename)
    #     print(f"DataExporter: Exporting results to YAML: {filepath}")
    #     try:
    #         with open(filepath, 'w', encoding='utf-8') as f:
    #             yaml.dump(data, f, allow_unicode=True, sort_keys=False, indent=2, Dumper=yaml.SafeDumper)
    #         print(f"DataExporter: Successfully exported to {filepath}")
    #     except Exception as e:
    #         print(f"DataExporter Error: Exporting data to YAML file {filepath} failed: {e}")
    #         raise # Re-raise to allow manager to handle UI feedback

    def export_to_json(self, data: Dict[str, Any], filename: str = "simulation_results.json"):
        filepath = self._prepare_filepath(filename)
        print(f"DataExporter: Exporting results to JSON: {filepath}")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"DataExporter: Successfully exported to {filepath}")
        except Exception as e:
            print(f"DataExporter Error: Exporting data to JSON file {filepath} failed: {e}")
            raise

    def export_to_csv(self, data_list: List[Dict[str, Any]], filename: str = "simulation_results.csv"):
        if not data_list:
            print("DataExporter: No data to export to CSV.")
            return

        filepath = self._prepare_filepath(filename)
        print(f"DataExporter: Exporting results to CSV: {filepath}")
        try:
            headers = list(data_list[0].keys()) # Assumes all dicts in list have same keys
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data_list)
            print(f"DataExporter: Successfully exported to {filepath}")
        except Exception as e:
            print(f"DataExporter Error: Exporting data to CSV file {filepath} failed: {e}")
            raise