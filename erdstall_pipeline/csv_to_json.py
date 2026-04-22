import csv


def _csv_to_json(filepath):
    """
    Parses a CSV file containing 3D path points into a JSON-compatible dictionary.

    The CSV is expected to be semicolon-delimited with columns for ID, coordinates
    (x, y, z), and neighbor connections (prev/next). It handles decimal conversion
    (comma to dot) for coordinates.

    Args:
        filepath (str): The absolute path to the CSV file.

    Returns:
        dict: A dictionary with keys:
            - "startNode": The ID of the starting node (usually point_id '0').
            - "nodes": A list of dictionaries, each representing a point in 3D space
                       with 'id', 'position' [x, y, z], and 'neighbors' list.
    """
    result = {
        "startNode": None,
        "nodes": []
    }

    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')

        for row in reader:
            p_id = row['point_id']
            node_id = f"n{p_id}"

            if p_id == '0':
                result["startNode"] = node_id

            x = float(row['x'].replace(',', '.'))
            y = float(row['y'].replace(',', '.'))
            z = float(row['z'].replace(',', '.'))

            position = [x, y, z]
            neighbors = []

            prev_id = row.get('prev_point_id', '').strip()
            if prev_id:
                neighbors.append(f"n{prev_id}")

            next_id = row.get('next_point_id', '').strip()
            if next_id:
                neighbors.append(f"n{next_id}")

            node_obj = {
                "id": node_id,
                "position": position,
                "neighbors": neighbors
            }

            result["nodes"].append(node_obj)

    if result["startNode"] is None and result["nodes"]:
        result["startNode"] = result["nodes"][0]["id"]

    return result

import json
from pathlib import Path


def csv_to_json_file(csv_path: str | Path, json_path: str | Path) -> Path:
    csv_path = Path(csv_path)
    json_path = Path(json_path)

    data = _csv_to_json(csv_path)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return json_path