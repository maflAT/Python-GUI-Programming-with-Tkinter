import tkinter as tk
from tkinter import ttk
from datetime import date
from . import widgets as w
from .constants import EW


class DataRecordForm(tk.Frame):
    """The input form for our widgets"""

    def __init__(self, parent, fields: dict[str, dict], *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.inputs: dict[str, w.LabelInput] = {}
        self.init_record_info(fields).grid(sticky=EW, row=0, column=0)
        self.init_env_info(fields).grid(sticky=EW, row=1, column=0)
        self.init_plant_info(fields).grid(sticky=EW, row=2, column=0)
        self.init_notes().grid(sticky=tk.W, row=3, column=0)
        self.reset()

    def init_record_info(self, fields: dict[str, dict]):
        record_info = tk.LabelFrame(self, text="Record Information")
        self.inputs["Date"] = w.LabelInput(
            parent=record_info,
            label="Date",
            field_spec=fields["Date"],
        ).grid(row=0, column=0)
        self.inputs["Time"] = w.LabelInput(
            parent=record_info,
            label="Time",
            field_spec=fields["Time"],
        ).grid(row=0, column=1)
        self.inputs["Technician"] = w.LabelInput(
            parent=record_info,
            label="Technician",
            field_spec=fields["Technician"],
        ).grid(row=0, column=2)

        self.inputs["Lab"] = w.LabelInput(
            parent=record_info,
            label="Lab",
            field_spec=fields["Lab"],
        ).grid(row=1, column=0)
        self.inputs["Plot"] = w.LabelInput(
            parent=record_info,
            label="Plot",
            field_spec=fields["Plot"],
        ).grid(row=1, column=1)
        self.inputs["Seed sample"] = w.LabelInput(
            parent=record_info,
            label="Seed sample",
            field_spec=fields["Seed sample"],
        ).grid(row=1, column=2)
        return record_info

    def init_env_info(self, fields: dict[str, dict]):
        env_info = tk.LabelFrame(self, text="Environment Data")
        self.inputs["Humidity"] = w.LabelInput(
            parent=env_info,
            label="Humidity (g/m³)",
            field_spec=fields["Humidity"],
        ).grid(row=0, column=0)
        self.inputs["Light"] = w.LabelInput(
            parent=env_info,
            label="Light (klx)",
            field_spec=fields["Light"],
        ).grid(row=0, column=1)
        self.inputs["Temperature"] = w.LabelInput(
            parent=env_info,
            label="Temperature (°C)",
            field_spec=fields["Temperature"],
        ).grid(row=0, column=2)
        self.inputs["Equipment Fault"] = w.LabelInput(
            parent=env_info,
            label="Equipment Fault",
            field_spec=fields["Equipment Fault"],
        ).grid(row=1, column=0, columnspan=3)
        return env_info

    def init_plant_info(self, fields: dict[str, dict]):
        plant_info = tk.LabelFrame(self, text="Plant Data")
        self.inputs["Plants"] = w.LabelInput(
            parent=plant_info,
            label="Plants",
            field_spec=fields["Plants"],
        ).grid(row=0, column=0)
        self.inputs["Blossoms"] = w.LabelInput(
            parent=plant_info,
            label="Blossoms",
            field_spec=fields["Blossoms"],
        ).grid(row=0, column=1)
        self.inputs["Fruit"] = w.LabelInput(
            parent=plant_info,
            label="Fruit",
            field_spec=fields["Fruit"],
        ).grid(row=0, column=2)

        # Height data
        # create variables to be updated for min/max height
        # they can be referenced for min/max variables
        min_height_var = tk.DoubleVar(value="-infinity")
        max_height_var = tk.DoubleVar(value="infinity")
        self.inputs["Min Height"] = w.LabelInput(
            parent=plant_info,
            label="Min Height (cm)",
            field_spec=fields["Min Height"],
            input_args={
                "max_var": max_height_var,
                "focus_update_var": min_height_var,
            },
        ).grid(row=1, column=0)
        self.inputs["Max Height"] = w.LabelInput(
            parent=plant_info,
            label="Max Height (cm)",
            field_spec=fields["Max Height"],
            input_args={
                "min_var": min_height_var,
                "focus_update_var": max_height_var,
            },
        ).grid(row=1, column=1)
        self.inputs["Median Height"] = w.LabelInput(
            parent=plant_info,
            label="Median Height (cm)",
            field_spec=fields["Median Height"],
            input_args={
                "min_var": min_height_var,
                "max_var": max_height_var,
            },
        ).grid(row=1, column=2)
        return plant_info

    def init_notes(self):
        self.inputs["Notes"] = w.LabelInput(
            parent=self,
            label="Notes",
            input_class=tk.Text,
            input_args={"width": 75, "height": 10},
        )
        return self.inputs["Notes"]

    def get(self):
        return {key: widget.get() for key, widget in self.inputs.items()}

    def reset(self):
        """Reset the form for entries"""
        # get current values for auto-filling
        lab = self.inputs["Lab"].get()
        time = self.inputs["Time"].get()
        technician = self.inputs["Technician"].get()
        plot = self.inputs["Plot"].get()
        plot_values = self.inputs["Plot"].input.cget("values")

        # clear all fields
        for widget in self.inputs.values():
            widget.set("")

        # set defaults
        self.inputs["Date"].set(date.today().isoformat())
        if plot in ("", plot_values[-1]):
            self.inputs["Time"].input.focus()
            return
        self.inputs["Lab"].set(lab)
        self.inputs["Time"].set(time)
        self.inputs["Technician"].set(technician)
        next_plot_idx = plot_values.index(plot) + 1
        self.inputs["Plot"].set(plot_values[next_plot_idx])
        self.inputs["Seed sample"].input.focus()

    def get_errors(self):
        """Get a list of field errors in the form."""
        errors = {}
        for name, widget in self.inputs.items():
            if hasattr(widget.input, "trigger_focusout_validation"):
                widget.input.trigger_focusout_validation()
            if e := widget.error.get():
                errors[name] = e
        return errors
