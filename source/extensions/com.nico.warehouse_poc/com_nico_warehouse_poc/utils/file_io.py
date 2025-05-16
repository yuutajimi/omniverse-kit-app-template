# utils/file_io.py
import yaml
import json
import csv
from typing import Dict, Any, List

def write_yaml(filepath: str, data: Dict[str, Any]):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, indent=2)
        print(f"Data successfully written to YAML: {filepath}")
    except Exception as e:
        print(f"Error writing YAML to {filepath}: {e}")
        raise # 必要に応じてエラーを再送出

def read_yaml(filepath: str) -> Optional[Dict[str, Any]]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        print(f"Data successfully read from YAML: {filepath}")
        return data
    except Exception as e:
        print(f"Error reading YAML from {filepath}: {e}")
        return None


def write_json(filepath: str, data: Dict[str, Any]):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data successfully written to JSON: {filepath}")
    except Exception as e:
        print(f"Error writing JSON to {filepath}: {e}")
        raise

def read_json(filepath: str) -> Optional[Dict[str, Any]]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Data successfully read from JSON: {filepath}")
        return data
    except Exception as e:
        print(f"Error reading JSON from {filepath}: {e}")
        return None


def write_csv(filepath: str, data_list: List[Dict[str, Any]], headers: Optional[List[str]] = None):
    if not data_list:
        return
    if not headers:
        headers = list(data_list[0].keys())
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data_list)
        print(f"Data successfully written to CSV: {filepath}")
    except Exception as e:
        print(f"Error writing CSV to {filepath}: {e}")
        raise

# CSV読み込み関数も必要であれば追加