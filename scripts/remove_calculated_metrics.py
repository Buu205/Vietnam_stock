
import json
import os

file_path = '/Users/buuphan/Dev/Vietnam_dashboard/config/metadata/metric_registry.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'calculated_metrics' in data:
        print("Found 'calculated_metrics'. Removing...")
        del data['calculated_metrics']
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Successfully removed 'calculated_metrics' and saved file.")
    else:
        print("'calculated_metrics' key not found in the file.")

except Exception as e:
    print(f"Error: {e}")
