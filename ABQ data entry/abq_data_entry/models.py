import csv
import os
import json
from typing import Any
from .constants import FieldTypes as FT


class CSVModel:
    """CSV file storage"""

    fields = {
        "Date": {"req": True, "type": FT.iso_date_string},
        "Time": {
            "req": True,
            "type": FT.string_list,
            "values": ["8:00", "12:00", "16:00", "20:00"],
        },
        "Technician": {"req": True, "type": FT.string},
        "Lab": {
            "req": True,
            "type": FT.string_list,
            "values": ["A", "B", "C", "D", "E"],
        },
        "Plot": {
            "req": True,
            "type": FT.string_list,
            "values": [str(x) for x in range(1, 21)],
        },
        "Seed sample": {"req": True, "type": FT.string},
        "Humidity": {
            "req": True,
            "type": FT.decimal,
            "min": 0.5,
            "max": 52.0,
            "inc": 0.01,
        },
        "Light": {"req": True, "type": FT.decimal, "min": 0, "max": 100.0, "inc": 0.01},
        "Temperature": {
            "req": True,
            "type": FT.decimal,
            "min": 4,
            "max": 40,
            "inc": 0.01,
        },
        "Equipment Fault": {"req": False, "type": FT.boolean},
        "Plants": {"req": True, "type": FT.integer, "min": 0, "max": 20},
        "Blossoms": {"req": True, "type": FT.integer, "min": 0, "max": 1000},
        "Fruit": {"req": True, "type": FT.integer, "min": 0, "max": 1000},
        "Min Height": {
            "req": True,
            "type": FT.decimal,
            "min": 0,
            "max": 1000,
            "inc": 0.01,
        },
        "Max Height": {
            "req": True,
            "type": FT.decimal,
            "min": 0,
            "max": 1000,
            "inc": 0.01,
        },
        "Median Height": {
            "req": True,
            "type": FT.decimal,
            "min": 0,
            "max": 1000,
            "inc": 0.01,
        },
        "Notes": {"req": False, "type": FT.long_string},
    }

    def __init__(self, filename) -> None:
        self.filename = filename

    def save_record(self, data):
        """Save a dict of data to the CSV file"""
        with open(self.filename, "a") as fh:
            csv_writer = csv.DictWriter(fh, fieldnames=self.fields.keys())
            if not os.path.exists(self.filename):
                csv_writer.writeheader()
            csv_writer.writerow(data)


class SettingsModel:
    """A model for saving (and loading) settings"""

    def __init__(self, filename: str = "abq_settings.json", path: str = None) -> None:
        path = path or os.getenv("APPDATA")
        self.filepath = os.path.join(path, filename)
        self.load()

    variables = {
        "autofill date": {"type": "bool", "value": True},
        "autofill sheet data": {"type": "bool", "value": True},
    }

    def load(self):
        """Load the settings from file"""
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, "r") as fh:
            raw_values = json.loads(fh.read())
        for key in self.variables:
            if key in raw_values and "value" in raw_values[key]:
                self.variables[key]["value"] = raw_values[key]["value"]

    def save(self, settings: dict[str, dict[str, Any]] = None):
        """Save settings to file"""
        json_string = json.dumps(self.variables)
        with open(self.filepath, "w") as fh:
            fh.write(json_string)

    def set(self, key: str, value: Any):
        """Allow external access to variables"""
        if (
            key in self.variables
            and type(value).__name__ == self.variables[key]["type"]
        ):
            self.variables[key]["value"] = value
        else:
            raise ValueError(f"Unknown key '{key}' or invalid variable type")
