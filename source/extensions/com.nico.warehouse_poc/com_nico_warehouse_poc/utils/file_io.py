# utils/file_io.py
import yaml # Requires PyYAML
import json
import csv
import os
from typing import Dict, Any, List, Optional

# Helper to ensure a Dumper that doesn't write !!python/object tags for simple dicts
# This is often the desired behavior for simple data export.
class SafeDumperNoTags(yaml.SafeDumper):
    def represent_dict(self, data):
        return self.represent_mapping('tag:yaml.org,2002:map', data.items())

SafeDumperNoTags.add_representer(dict, SafeDumperNoTags.represent_dict)


def write_yaml(filepath: str, data: Dict[str, Any], use_safe_dumper_no_tags: bool = True):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            if use_safe_dumper_no_tags:
                yaml.dump(data, f, Dumper=SafeDumperNoTags, allow_unicode=True, sort_keys=False, indent=2)
            else:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False, indent=2) # Uses default (SafeDumper)
        print(f"FileIO: Data successfully written to YAML: {filepath}")
    except Exception as e:
        print(f"FileIO Error: Writing YAML to {filepath} failed: {e}")
        raise

def read_yaml(filepath: str) -> Optional[Dict[str, Any]]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        print(f"FileIO: Data successfully read from YAML: {filepath}")
        return data
    except FileNotFoundError:
        print(f"FileIO Error: YAML file not found at {filepath}")
        return None
    except Exception as e:
        print(f"FileIO Error: Reading YAML from {filepath} failed: {e}")
        return None


def write_json(filepath: str, data: Dict[str, Any]):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"FileIO: Data successfully written to JSON: {filepath}")
    except Exception as e:
        print(f"FileIO Error: Writing JSON to {filepath} failed: {e}")
        raise

def read_json(filepath: str) -> Optional[Dict[str, Any]]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"FileIO: Data successfully read from JSON: {filepath}")
        return data
    except FileNotFoundError:
        print(f"FileIO Error: JSON file not found at {filepath}")
        return None
    except Exception as e:
        print(f"FileIO Error: Reading JSON from {filepath} failed: {e}")
        return None


def write_csv(filepath: str, data_list: List[Dict[str, Any]], headers: Optional[List[str]] = None):
    if not data_list:
        print("FileIO: No data provided to write_csv.")
        return
    if not headers:
        headers = list(data_list[0].keys()) # Assumes all dicts have the same structure
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data_list)
        print(f"FileIO: Data successfully written to CSV: {filepath}")
    except Exception as e:
        print(f"FileIO Error: Writing CSV to {filepath} failed: {e}")
        raise

def read_csv(filepath: str) -> Optional[List[Dict[str, Any]]]:
    try:
        data_list = []
        with open(filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data_list.append(row)
        print(f"FileIO: Data successfully read from CSV: {filepath}")
        return data_list
    except FileNotFoundError:
        print(f"FileIO Error: CSV file not found at {filepath}")
        return None
    except Exception as e:
        print(f"FileIO Error: Reading CSV from {filepath} failed: {e}")
        return None