import csv
import os
import json
import psycopg2 as pg
from psycopg2.extras import DictCursor
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
        "Light": {"req": True, "type": FT.decimal, "min": 0, "max": 100.0, "inc": 0.1},
        "Temperature": {
            "req": True,
            "type": FT.decimal,
            "min": 4,
            "max": 40,
            "inc": 0.1,
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
            "inc": 1,
        },
        "Max Height": {
            "req": True,
            "type": FT.decimal,
            "min": 0,
            "max": 1000,
            "inc": 1,
        },
        "Median Height": {
            "req": True,
            "type": FT.decimal,
            "min": 0,
            "max": 1000,
            "inc": 1,
        },
        "Notes": {"req": False, "type": FT.long_string},
    }

    def __init__(self, filename: str, filepath: str = None) -> None:
        if filepath:
            if not os.path.exists(filepath):
                os.mkdir(filepath)
            self.filename = os.path.join(filepath, filename)
        else:
            self.filename = filename

    def save_record(self, data: dict, row_number: int = None):
        """Save a dict of data to the CSV file"""
        if row_number is not None:
            # This is an update
            records = self.get_all_records()
            records[row_number] = data
            with open(self.filename, "w", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=self.fields.keys())
                writer.writeheader()
                writer.writerows(records)
        else:
            # This is a new record
            newfile = not os.path.exists(self.filename)
            with open(self.filename, "a", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=self.fields.keys())
                if newfile:
                    writer.writeheader()
                writer.writerow(data)

    def get_all_records(self):
        """Import all records from our csv file."""
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(
                list(fh.readlines())  # mock open can't handle direct iteration over fh
            )
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

    def __init__(self, filename: str = "abq_settings.json", path: str = "~") -> None:
        self.filepath = os.path.join(os.path.expanduser(path), filename)
        self.load()

    variables = {
        "autofill date": {"type": "bool", "value": True},
        "autofill sheet data": {"type": "bool", "value": True},
        "font size": {"type": "int", "value": 9},
        "theme": {"type": "str", "value": "default"},
        "db_host": {"type": "str", "value": "localhost"},
        "db_name": {"type": "str", "value": "abq"},
        "weather_station": {"type": "str", "value": "KBMG"},
        "abq_auth_url": {"type": "str", "value": "http://localhost:8000/auth"},
        "abq_upload_url": {"type": "str", "value": "http://localhost:8000/upload"},
    }

    def load(self):
        """Load the settings from file"""
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, "r", encoding="utf-8") as fh:
            raw_values = json.loads(fh.read())
        for key in self.variables:
            if key in raw_values and "value" in raw_values[key]:
                self.variables[key]["value"] = raw_values[key]["value"]

    def save(self, settings: dict[str, dict[str, Any]] = None):
        """Save settings to file"""
        json_string = json.dumps(self.variables)
        with open(self.filepath, "w", encoding="utf-8") as fh:
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


class SQLModel:
    """Data Model for Postgres database"""

    fields = {
        "Date": {"req": True, "type": FT.iso_date_string},
        "Time": {
            "req": True,
            "type": FT.string_list,
            "values": ["8:00", "12:00", "16:00", "20:00"],
        },
        "Technician": {"req": True, "type": FT.string_list, "values": []},
        "Lab": {
            "req": True,
            "type": FT.string_list,
            "values": [],
        },
        "Plot": {
            "req": True,
            "type": FT.string_list,
            "values": [],
        },
        "Seed sample": {"req": True, "type": FT.string},
        "Humidity": {
            "req": True,
            "type": FT.decimal,
            "min": 0.5,
            "max": 52.0,
            "inc": 0.01,
        },
        "Light": {"req": True, "type": FT.decimal, "min": 0, "max": 100.0, "inc": 0.1},
        "Temperature": {
            "req": True,
            "type": FT.decimal,
            "min": 4,
            "max": 40,
            "inc": 0.1,
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
            "inc": 1,
        },
        "Max Height": {
            "req": True,
            "type": FT.decimal,
            "min": 0,
            "max": 1000,
            "inc": 1,
        },
        "Median Height": {
            "req": True,
            "type": FT.decimal,
            "min": 0,
            "max": 1000,
            "inc": 1,
        },
        "Notes": {"req": False, "type": FT.long_string},
    }

    def __init__(self, host, database, user: str = "max", password: str = "max"):
        """Establishes connection to database and fetch configuration data."""
        self.connection = pg.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            cursor_factory=DictCursor,
        )

        techs = self.query("SELECT * FROM lab_techs ORDER BY name")
        labs = self.query("SELECT id FROM labs ORDER BY id")
        plots = self.query("SELECT DISTINCT plot FROM plots ORDER BY plot")
        self.fields["Technician"]["values"] = [x["name"] for x in techs]
        self.fields["Lab"]["values"] = [x["id"] for x in labs]
        self.fields["Plot"]["values"] = [str(x["plot"]) for x in plots]

    def query(self, query: str, parameters: dict[str, str] = None):
        """Execute parametrized database query.

        `query`: query string with placeholders for parameters.
        `parameters`: dictionary containing parameters to fill into query."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, parameters)
        except (pg.Error) as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()
            if cursor.description is not None:
                return cursor.fetchall()

    def get_all_records(self, all_dates=False):
        query = (
            "SELECT * FROM data_record_view "
            'WHERE NOT %(all_dates)s OR "Date" = CURRENT_DATE '
            'ORDER BY "Date", "Time", "Lab", "Plot"'
        )
        return self.query(query, {"all_dates": all_dates})

    def get_record(self, date, time, lab, plot):
        query = (
            "SELECT * FROM data_record_view "
            'WHERE "Date" = %(date)s AND "Time" = %(time)s '
            'AND "Lab" = %(lab)s AND "Plot" = %(plot)s'
        )
        result = self.query(
            query, {"date": date, "time": time, "lab": lab, "plot": plot}
        )
        return result[0] if result else {}

    def get_lab_check(self, date, time, lab):
        query = (
            "SELECT date, time, lab_id, lab_tech_id, "
            "lt.name as lab_tech FROM lab_checks JOIN lab_techs as lt "
            "ON lab_checks.lab_tech_id = lt.id WHERE "
            "lab_id = %(lab)s AND date = %(date)s AND time = %(time)s"
        )
        results = self.query(query, {"date": date, "time": time, "lab": lab})
        return results[0] if results else {}

    lc_update_query = (
        "UPDATE lab_checks SET lab_tech_id = "
        "(SELECT id FROM lab_techs WHERE name = %(Technician)s) "
        "WHERE date=%(Date)s AND time=%(Time)s AND lab_id=%(Lab)s"
    )
    lc_insert_query = (
        "INSERT INTO lab_checks VALUES (%(Date)s, "
        "%(Time)s, %(Lab)s,(SELECT id FROM lab_techs "
        "WHERE name=%(Technician)s))"
    )
    pc_update_query = (
        "UPDATE plot_checks SET seed_sample = %(Seed sample)s, "
        "humidity = %(Humidity)s, light = %(Light)s, "
        "temperature = %(Temperature)s, "
        "equipment_fault = %(Equipment Fault)s, "
        "blossoms = %(Blossoms)s, plants = %(Plants)s, "
        "fruit = %(Fruit)s, max_height = %(Max Height)s, "
        "min_height = %(Min Height)s, median_height = "
        "%(Median Height)s, notes = %(Notes)s "
        "WHERE date=%(Date)s AND time=%(Time)s "
        "AND lab_id=%(Lab)s AND plot=%(Plot)s"
    )
    pc_insert_query = (
        "INSERT INTO plot_checks VALUES (%(Date)s, %(Time)s, %(Lab)s,"
        " %(Plot)s, %(Seed sample)s, %(Humidity)s, %(Light)s,"
        " %(Temperature)s, %(Equipment Fault)s, %(Blossoms)s,"
        " %(Plants)s, %(Fruit)s, %(Max Height)s, %(Min Height)s,"
        " %(Median Height)s, %(Notes)s)"
    )

    def save_record(self, record):
        date = record["Date"]
        time = record["Time"]
        lab = record["Lab"]
        plot = record["Plot"]

        if self.get_lab_check(date, time, lab):
            lc_query = self.lc_update_query
        else:
            lc_query = self.lc_insert_query
        if self.get_record(date, time, lab, plot):
            pc_query = self.pc_update_query
            self.last_write = "update"
        else:
            pc_query = self.pc_insert_query
            self.last_write = "insert"
        self.query(lc_query, record)
        self.query(pc_query, record)

    def get_current_seed_sample(self, lab, plot):
        result = self.query(
            "SELECT current_seed_sample FROM plots "
            "WHERE lab_id=%(lab)s AND plot=%(plot)s",
            {"lab": lab, "plot": plot},
        )
        return result[0]["current_seed_sample"] if result else ""

    #####################
    # Weather functions #
    #####################

    def add_weather_data(self, data: dict[str, str]):
        query = (
            "INSERT INTO local_weather VALUES "
            "(%(observation_time_rfc822)s, %(temp_c)s, "
            "%(relative_humidity)s, %(pressure_mb)s, "
            "%(weather)s)"
        )
        try:
            self.query(query, data)
        except pg.IntegrityError:
            # already have weather for this timestamp
            pass
