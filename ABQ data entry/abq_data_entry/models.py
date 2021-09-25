import csv
import os
import json
from typing import Any
from .constants import FieldTypes as FT


class CSVModel:
    """CSV file storage"""

    TRUES = ["true", "yes", "1"]
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

    def __init__(self, filename: str) -> None:
        self.filename = filename

    def save_record(self, data: dict, row_number: int = None):
        """Save a dict of data to the CSV file"""
        if row_number is not None:
            # This is an update
            records = self.get_all_records()
            records[row_number] = data
            with open(self.filename, "w") as fh:
                writer = csv.DictWriter(fh, fieldnames=self.fields.keys())
                writer.writeheader()
                writer.writerows(records)
        else:
            # This is a new record
            newfile = not os.path.exists(self.filename)
            with open(self.filename, "a") as fh:
                writer = csv.DictWriter(fh, fieldnames=self.fields.keys())
                if newfile:
                    writer.writeheader()
                writer.writerow(data)

    def get_all_records(self):
        """Import all records from our csv file."""
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, "r") as fh:
            reader = csv.DictReader(fh)
            missing_fields = set(self.fields.keys()) - set(reader.fieldnames)
            if len(missing_fields) > 0:
                raise Exception(f"File is missing fields: {', '.join(missing_fields)}")
            records = list(reader)
        bool_fields = [
            key for key, meta in self.fields.items() if meta["type"] == FT.boolean
        ]
        for record in records:
            for key in bool_fields:
                record[key] = record[key].lower() in self.TRUES
        return records

    def get_record(self, row_number: int):
        return self.get_all_records()[row_number]


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
